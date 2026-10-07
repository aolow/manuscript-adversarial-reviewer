"""Source authenticity, conservative support checks, and cross-review reconciliation.

Exact quotation is testable locally. Scientific entailment is not certified by
this module; accepted interpretations remain hypotheses for human adjudication.
"""
from __future__ import annotations

from dataclasses import asdict
from difflib import SequenceMatcher
import re
import unicodedata

from .errors import ReviewError
from .models import Finding, evidence, stable_id, SEVERITIES
from .prioritization import prioritize
from .extraction import substantive_blocks
from .providers.contracts import (REVIEW_ENVELOPE_SCHEMA, FINDING, CLAIM, STRENGTH,
                                  validate_payload)

CERTAINTY = re.compile(r"\b(?:definitely|undoubtedly|conclusively|certainly|proves? that|"
                       r"proven (?:invalid|false)|fatal flaw|guarantees?)\b", re.I)
TOPIC_CUES = {
    "leakage": r"train|test|split|fold|select|feature|leak|label|integrat|partition|rank|panel|held.out",
    "pseudoreplication": r"cell|donor|replicat|patient|independen|sample",
    "circularity": r"same|signature|gene|marker|construct|defin|annotat|validat",
    "causality": r"caus|mechanis|observ|correlat|associat|perturb|random",
    "conservation": r"conserv|transfer|similar|regulat|tissue",
    "novelty": r"first|novel|new|unprecedent|contribut|method",
    "validation": r"validat|cohort|independen|external|test|predict",
    "confounding": r"confound|batch|platform|condition|response|cohort",
    "statistics": r"p.value|significan|test|interval|replicat|statistic|sample|effect",
    "calibration": r"calibrat|predict|probabilit|AUROC|AUPRC|Brier",
    "reproducibility": r"code|data|seed|version|software|method|preprocess|pipeline|cohort|exclu",
    "clinical": r"clinical|patient|treatment|biomarker|response|survival|endpoint",
}
STOP = {"the", "and", "that", "this", "with", "were", "was", "from", "for", "are",
        "not", "but", "have", "has", "had", "their", "our", "these", "which"}


def words(text):
    return {word for word in re.findall(r"[a-z]{3,}", text.lower()) if word not in STOP}


_CANONICAL_CHARS = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
})


def _canonical_with_map(text):
    """Normalize harmless Unicode/whitespace drift while retaining source offsets."""
    chars, positions = [], []
    for index, char in enumerate(text):
        expanded = unicodedata.normalize("NFC", char).translate(_CANONICAL_CHARS)
        for unit in expanded:
            if unit.isspace():
                if chars and chars[-1] != " ":
                    chars.append(" ")
                    positions.append(index)
            else:
                chars.append(unit)
                positions.append(index)
    return "".join(chars), positions


def _safe_slug(value, fallback):
    if isinstance(value, str):
        slug = re.sub(r"[^a-z0-9_-]+", "-", value.strip().lower()).strip("-_")
        if slug and not slug[0].isalpha():
            slug = "item-" + slug
        slug = slug[:80]
        if re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", slug):
            return slug
    return fallback


def _record_schema_rejection(rejections, kind, index, exc):
    path = getattr(exc, "schema_path", None)
    validator = getattr(exc, "schema_validator", None)
    prefix = kind + "s." + str(index)
    rejections.append({
        "kind": kind,
        "index": index,
        "status": "schema_rejected",
        "path": prefix if path in (None, "root") else prefix + "." + path,
        "validator": validator or "unknown",
    })


def _validate_review_item(row, schema, kind, index, rejections, normalizations):
    if not isinstance(row, dict):
        try:
            validate_payload(row, schema)
        except ReviewError as exc:
            _record_schema_rejection(rejections, kind, index, exc)
        return None, None
    value = dict(row)
    raw_id = value.get("id")
    if kind in ("finding", "claim"):
        normalized_id = _safe_slug(raw_id, kind + "-" + str(index + 1))
        if raw_id != normalized_id:
            value["id"] = normalized_id
            normalizations.append({"kind": kind, "index": index, "field": "id"})
    if kind == "finding":
        properties = FINDING["properties"]
        for field in ("topic", "issue_key", "category"):
            allowed = properties[field]["enum"]
            if value.get(field) not in allowed and field in value:
                value[field] = "other"
                normalizations.append({"kind": kind, "index": index, "field": field})
    try:
        validate_payload(value, schema)
    except ReviewError as exc:
        _record_schema_rejection(rejections, kind, index, exc)
        return None, raw_id
    return value, raw_id


def _provider_finding_id(role, row, citations):
    # Block-level anchors remain stable when a model quotes a longer or shorter
    # unique excerpt from the same source passage on a later run.
    anchors = "|".join(sorted({ev.block_id for ev in citations}))
    fallback = row["evidence_statement"] if not anchors else ""
    seed = "|".join((role, row["issue_key"], row["topic"], row["basis"], anchors, fallback))
    return "reviewer." + role + "." + stable_id("finding", seed).split("-", 1)[1]


def resolve_citations(citations, documents):
    blocks = {b.id: b for d in documents for b in d.blocks}
    resolved = []
    for citation in citations:
        if not isinstance(citation, dict) or set(citation) != {"block_id", "quote"}:
            raise ReviewError("Generated citations may specify only block_id and quote; locations are derived locally.")
        block = blocks.get(citation["block_id"])
        quote = citation["quote"]
        if block is None or not isinstance(quote, str) or not quote.strip():
            raise ReviewError("Fabricated or mismatched manuscript quote/block rejected.")
        if block.kind == "heading" or block.section.lower().startswith(("references", "bibliography")):
            raise ReviewError("Heading/reference citations cannot establish manuscript methods or results.")
        if quote in block.text:
            if block.text.count(quote) != 1:
                raise ReviewError("Ambiguous repeated quote; use a longer uniquely locating excerpt.")
            start, end = block.text.index(quote), block.text.index(quote) + len(quote)
        else:
            normalized_block, positions = _canonical_with_map(block.text)
            normalized_quote, _ = _canonical_with_map(quote.strip())
            if not normalized_quote or normalized_block.count(normalized_quote) != 1:
                raise ReviewError("Fabricated or mismatched manuscript quote/block rejected.")
            normalized_start = normalized_block.index(normalized_quote)
            normalized_end = normalized_start + len(normalized_quote)
            start = positions[normalized_start]
            end = positions[normalized_end - 1] + 1
        resolved.append(evidence(block, start, end))
    return resolved


def action_flags(action, severity="major"):
    if severity not in ("major", "moderate"):
        return []
    kind = action.get("kind")
    required = (("input", "comparison", "held_out_unit", "metric", "expected_interpretation")
                if kind in ("analysis", "experiment") else
                ("text_section", "text_claim", "recommended_framing")
                if kind == "text" else ("input", "expected_interpretation") if kind == "reporting" else ())
    if not required or any(not action.get(key) or not str(action[key]).strip() for key in required):
        return ["incomplete_action"]
    content = " ".join(str(action.get(key) or "") for key in required)
    if len(words(content)) < 8 or re.fullmatch(r"(?:more validation|further analysis|validate more)[. ]*", content, re.I):
        return ["vague_action"]
    return []


def action_context_flags(action, documents):
    blocks = substantive_blocks(documents)
    if action.get("kind") in ("analysis", "experiment"):
        flags = ["feasibility_not_verified"]
        if action["kind"] == "experiment":
            return flags  # A proposed new experiment need not already have data.
        source = " ".join(" ".join(b.text for b in blocks).split())
        needed = " ".join(str(action.get(k) or "") for k in ("input", "comparison", "held_out_unit"))
        unavailable = (
            (r"no longitudinal|only baseline|longitudinal.{0,30}(?:unavailable|not collected)",
             r"longitudinal|within.patient change|follow.up|trajector"),
            (r"no (?:independent )?external cohort|external.{0,30}(?:unavailable|not collected)",
             r"external cohort|independent cohort"),
            (r"raw (?:reads|counts).{0,40}(?:unavailable|not retained)|no raw (?:reads|counts)",
             r"raw (?:reads|counts)|realign"),
            (r"no (?:untreated|negative.control)|(?:untreated|negative.control).{0,30}not (?:measured|collected)",
             r"untreated|negative.control"),
            (r"(?:protein|proteomic).{0,40}not (?:measured|collected)|no protein measurements",
             r"protein|proteomic"),
        )
        if any(re.search(absence, source, re.I) and re.search(requirement, needed, re.I)
               for absence, requirement in unavailable):
            flags.append("action_requires_unavailable_data")
        return flags
    if action.get("kind") != "text":
        return []
    flags = []
    matching = [b for b in blocks if b.section == action.get("text_section")]
    if not matching:
        flags.append("text_edit_section_not_found")
    if not action.get("text_claim") or not any(action["text_claim"] in b.text for b in matching):
        flags.append("text_edit_claim_not_found")
    return flags


def interpretation_flags(text, quotes):
    """Narrow contradiction checks, not a semantic verifier."""
    flags = []
    for sentence in re.split(r"[.!?]\s+", text):
        qualified = re.search(r"\b(?:may|might|could|if|not|no|cannot|without|lacks?|unsupported|unverified|overclaim\w*)\b", sentence, re.I)
        if qualified:
            continue
        for design in (r"randomized (?:controlled )?trial", r"prospective external validation",
                       r"paired longitudinal (?:design|samples)", r"independent replication cohort"):
            if re.search(design, sentence, re.I) and not re.search(design, quotes, re.I):
                flags.append("invented_design_in_interpretation")
        if (re.search(r"observational|associat|correlat", quotes, re.I)
                and re.search(r"\b(?:establish\w*|demonstrat\w*|prov\w*)\b.{0,70}\b(?:caus\w*|mechanis\w*)", sentence, re.I)):
            flags.append("association_promoted_to_causation")
        for match in re.finditer(r"\b(\d+)\s+(?:independent\s+)?(patients|donors|subjects|biological replicates)\b", sentence, re.I):
            number = match.group(1)
            if not re.search(r"\b" + number + r"\s+(?:independent\s+)?(?:patients|donors|subjects|biological replicates)\b", quotes, re.I):
                flags.append("unsupported_biological_unit_count")
    if re.search(r"\b(?:literature (?:establishes|proves|confirms)|prior studies (?:proved|established)|already established in the literature)\b", text, re.I):
        flags.append("external_verification_required")
    if (re.search(r"\b(?:no (?:negative |untreated )?controls? (?:were |was )?(?:used|measured|performed)|controls? (?:are|were) absent)\b", text, re.I)
            and not re.search(r"\b(?:no (?:untreated|negative.control)|controls?.{0,30}(?:absent|not (?:used|measured|performed)))", quotes, re.I)):
        flags.append("unreported_control_treated_as_absent")
    return flags


def support_audit(basis, premise, interpretation, rationale, citations, topic, confidence, issue_key="other"):
    flags = []
    quotes = "\n".join(ev.quote for ev in citations)
    if basis == "external_claim":
        return "external_unverified", "low", ["external_verification_required"]
    if not citations:
        return "ungrounded", "low", ["no_manuscript_evidence"]
    if basis == "manuscript_direct" and not any(premise in ev.quote for ev in citations):
        flags.append("factual_premise_not_an_exact_excerpt")
    if basis == "manuscript_inference" and len({ev.block_id for ev in citations}) < 2:
        flags.append("synthesis_needs_multiple_source_chunks")
    if topic in TOPIC_CUES and not re.search(TOPIC_CUES[topic], quotes, re.I):
        flags.append("source_topic_mismatch")
    # This catches obvious unsupported premises, not general semantic entailment.
    numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", premise))
    if numbers - set(re.findall(r"\b\d+(?:\.\d+)?\b", quotes)):
        flags.append("unsupported_numeric_premise")
    if basis != "reviewer_opinion" and len(words(premise) & words(quotes)) < min(2, len(words(premise))):
        flags.append("unsupported_factual_premise")
    if CERTAINTY.search(interpretation):
        flags.append("unsupported_certainty")
    flags += interpretation_flags(interpretation, quotes)
    protections = {
        "feature_selection_before_split": r"\b(?:not select\w*.{0,60}before|selection.{0,50}only within.{0,30}training|selected.{0,40}after.{0,20}split)",
        "cell_pseudoreplication": r"\bcells.{0,25}not treated.{0,25}independent",
        "test_set_tuning": r"\b(?:tuning|hyperparameters).{0,40}(?:only in|only within).{0,30}(?:inner|training)",
    }
    if issue_key in protections and re.search(protections[issue_key], quotes, re.I | re.S):
        flags.append("source_describes_protection_not_flaw")
    # Interpreting a explicitly observational design as a completed randomized trial.
    if (re.search(r"\b(?:randomized trial|random allocation)\b", premise, re.I)
            and not re.search(r"\b(?:randomized trial|random allocation)\b", quotes, re.I)):
        flags.append("unsupported_design_claim")
    if not words(rationale) & words(quotes):
        flags.append("support_rationale_unrelated")
    if flags:
        return "needs_semantic_review", "low", flags
    # Never promote subjective interpretation to verified scientific truth.
    return "source_verified", "medium" if confidence == "high" else confidence, ["semantic_entailment_not_verified"]


def normalize_response(role, response, documents, extraction, provider_name,
                       rejections=None, normalizations=None):
    rejections = [] if rejections is None else rejections
    normalizations = [] if normalizations is None else normalizations
    validate_payload(response, REVIEW_ENVELOPE_SCHEMA)
    findings, claims, strengths = [], [], []
    claim_map = {claim["id"]: claim["id"] for claim in extraction["claims"]}
    rejected_claim_ids, seen_claim_ids, seen_finding_ids = set(), set(), set()

    for index, raw_row in enumerate(response["claims"]):
        row, raw_id = _validate_review_item(
            raw_row, CLAIM, "claim", index, rejections, normalizations)
        if row is None:
            if isinstance(raw_id, str):
                rejected_claim_ids.add(raw_id)
            continue
        aliases = {row["id"]}
        if isinstance(raw_id, str):
            aliases.add(raw_id)
        if aliases & seen_claim_ids:
            rejections.append({"kind": "claim", "index": index, "status": "duplicate_id",
                               "path": "claims.%d.id" % index, "validator": "unique"})
            rejected_claim_ids.update(aliases)
            continue
        seen_claim_ids.update(aliases)
        try:
            sources = resolve_citations(row["manuscript_evidence"], documents)
            if not sources:
                rejected_claim_ids.update(aliases)
                rejections.append({"kind": "claim", "index": index, "status": "ungrounded",
                                   "path": "claims.%d.manuscript_evidence" % index,
                                   "validator": "source"})
                continue
            supporting = resolve_citations(row["supporting_evidence"], documents)
        except ReviewError:
            rejected_claim_ids.update(aliases)
            rejections.append({"kind": "claim", "index": index, "status": "source_rejected",
                               "path": "claims.%d" % index, "validator": "citation"})
            continue
        identifier = stable_id("central-claim", row["claim_text"])
        for alias in aliases:
            claim_map[alias] = identifier
        flags = []
        if any(ev.quote != citation["quote"] for ev, citation in
               zip(sources, row["manuscript_evidence"])):
            flags.append("normalized_citation_match")
        if any(ev.quote != citation["quote"] for ev, citation in
               zip(supporting, row["supporting_evidence"])):
            flags.append("normalized_citation_match")
        claim_words = words(row["claim_text"])
        source_words = words(" ".join(ev.quote for ev in sources))
        if claim_words and not claim_words & source_words:
            flags.append("claim_paraphrase_needs_semantic_review")
        if not supporting:
            flags.append("support_not_established")
        flags += action_flags(row["falsification_analysis"]) + action_flags(row["decisive_analysis"])
        flags += action_context_flags(row["falsification_analysis"], documents)
        flags += action_context_flags(row["decisive_analysis"], documents)
        if CERTAINTY.search(row["strongest_support"]):
            flags.append("unsupported_certainty")
        flags += interpretation_flags(row["strongest_support"], " ".join(ev.quote for ev in supporting))
        if set(re.findall(r"\b\d+(?:\.\d+)?\b", row["strongest_support"])) - set(
                re.findall(r"\b\d+(?:\.\d+)?\b", " ".join(ev.quote for ev in supporting))):
            flags.append("unsupported_support_summary")
        claims.append({
            **{key: value for key, value in row.items() if key not in ("manuscript_evidence", "supporting_evidence")},
            "id": identifier, "manuscript_evidence": [asdict(e) for e in sources],
            "supporting_evidence": [asdict(e) for e in supporting],
            "confidence_in_claim": "low" if set(flags) - {"feasibility_not_verified"} else (
                "medium" if row["confidence_in_claim"] == "high" else row["confidence_in_claim"]),
            "origin": "provider:" + provider_name, "reviewer_role": role,
            "quality_flags": sorted(set(flags + ["scientific_judgment_unverified"])),
        })

    for index, raw_row in enumerate(response["findings"]):
        row, _ = _validate_review_item(
            raw_row, FINDING, "finding", index, rejections, normalizations)
        if row is None:
            continue
        citations, rejected_citations, normalized_citations = [], 0, 0
        for citation in row["citations"]:
            try:
                resolved = resolve_citations([citation], documents)
                citations.extend(resolved)
                normalized_citations += sum(ev.quote != citation["quote"] for ev in resolved)
            except ReviewError:
                rejected_citations += 1
        if row["citations"] and not citations:
            rejections.append({"kind": "finding", "index": index, "status": "source_rejected",
                               "path": "findings.%d.citations" % index, "validator": "citation"})
            continue
        unknown = set(row["claim_ids"]) - set(claim_map)
        truly_unknown = unknown - rejected_claim_ids
        linked_claim_ids = [claim_map[x] for x in row["claim_ids"] if x in claim_map]
        grounding, confidence, flags = support_audit(
            row["basis"], row["evidence_statement"], row["interpretation"],
            row["support_rationale"], citations, row["topic"], row["confidence"], row["issue_key"])
        if rejected_citations:
            flags.append("invalid_citations_dropped")
        if normalized_citations:
            flags.append("normalized_citation_match")
        if truly_unknown:
            flags.append("dangling_claim_ref_dropped")
        flags += action_flags(row["action"], row["severity"])
        flags += action_context_flags(row["action"], documents)
        disposition = ("needs_review" if grounding != "source_verified"
                       or any(flag in flags for flag in ("incomplete_action", "vague_action",
                                                        "text_edit_section_not_found", "text_edit_claim_not_found",
                                                        "action_requires_unavailable_data")) else "active")
        if disposition == "needs_review":
            confidence = "low"
        identifier = _provider_finding_id(role, row, citations)
        if identifier in seen_finding_ids:
            rejections.append({"kind": "finding", "index": index, "status": "duplicate_finding",
                               "path": "findings.%d" % index, "validator": "unique"})
            continue
        seen_finding_ids.add(identifier)
        findings.append(prioritize(Finding(
            id=identifier,
            rule_id=row["issue_key"] if row["issue_key"] != "other" else "reviewer." + role,
            severity=row["severity"], category=row["category"],
            manuscript_section=citations[0].section if citations else "Not located",
            claim=citations[0].quote if citations else "Not established from the manuscript.",
            issue=row["interpretation"], why_it_matters=row["why_it_matters"],
            evidence=citations, suggested_fix=row["suggested_fix"],
            suggested_analysis=row["suggested_analysis"], confidence=confidence,
            issue_status=row["issue_status"], reviewer_roles=[role],
            origin="provider:" + provider_name, basis=row["basis"], grounding_status=grounding,
            evidence_statement=row["evidence_statement"], support_rationale=row["support_rationale"],
            topic=row["topic"], claim_ids=linked_claim_ids,
            action=row["action"], quality_flags=sorted(set(flags)), disposition=disposition,
            reviewer_assessments=[{"role": role, "severity": row["severity"], "confidence": row["confidence"]}],
            limitation="Exact or conservatively normalized source text was checked. Reviewer interpretation, external facts, and scientific adequacy are unverified.")))

    for index, raw_row in enumerate(response["strengths"]):
        row, _ = _validate_review_item(
            raw_row, STRENGTH, "strength", index, rejections, normalizations)
        if row is None:
            continue
        try:
            sources = resolve_citations(row["citations"], documents)
        except ReviewError:
            rejections.append({"kind": "strength", "index": index, "status": "source_rejected",
                               "path": "strengths.%d.citations" % index, "validator": "citation"})
            continue
        if not sources:
            rejections.append({"kind": "strength", "index": index, "status": "ungrounded",
                               "path": "strengths.%d.citations" % index, "validator": "source"})
            continue
        status, _, flags = support_audit("reviewer_opinion", row["text"], row["text"],
                                         row["text"], sources, "other", "low")
        if any(ev.quote != citation["quote"] for ev, citation in zip(sources, row["citations"])):
            flags.append("normalized_citation_match")
        strengths.append({"text": row["text"], "evidence": [asdict(e) for e in sources],
                          "reviewer_role": role, "grounding_status": status,
                          "quality_flags": sorted(set(flags)),
                          "interpretation_status": "reviewer_judgment_unverified"})
    return findings, claims, strengths


def reconcile(findings):
    """Conservative duplicate grouping; originals and rating disagreements remain."""
    candidates, events = [], []
    for finding in findings:
        if not finding.origin.startswith("provider:") or finding.disposition not in ("active", "confirmed"):
            continue
        canonical = None
        for existing in candidates:
            overlap = any(
                left.block_id == right.block_id and max(left.start, right.start) < min(left.end, right.end)
                for left in existing.evidence for right in finding.evidence)
            similarity = SequenceMatcher(None, existing.issue.lower(), finding.issue.lower()).ratio()
            if (existing.topic and existing.topic == finding.topic and overlap
                    and (similarity >= 0.65 or (existing.evidence_statement == finding.evidence_statement
                                              and existing.action == finding.action))):
                canonical = existing
                break
        if canonical is None:
            candidates.append(finding)
            continue
        finding.disposition = "duplicate"
        finding.duplicate_of = canonical.id
        canonical.reviewer_roles = sorted(set(canonical.reviewer_roles + finding.reviewer_roles))
        canonical.reviewer_assessments.extend(finding.reviewer_assessments)
        if canonical.severity != finding.severity:
            canonical.quality_flags.append("severity_disagreement")
            # Keep the less severe rating until a human arbitrates; do not manufacture consensus.
            canonical.severity = max((canonical.severity, finding.severity), key=SEVERITIES.index)
            canonical.confidence = "low"
            prioritize(canonical)
        events.append({"canonical_id": canonical.id, "duplicate_id": finding.id,
                       "severity_disagreement": "severity_disagreement" in canonical.quality_flags})
    return events
