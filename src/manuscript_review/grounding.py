"""Source authenticity, conservative support checks, and cross-review reconciliation.

Exact quotation is testable locally. Scientific entailment is not certified by
this module; accepted interpretations remain hypotheses for human adjudication.
"""
from __future__ import annotations

from dataclasses import asdict
from difflib import SequenceMatcher
import re

from .errors import ReviewError
from .models import Finding, evidence, stable_id, SEVERITIES
from .prioritization import prioritize
from .providers.contracts import REVIEW_SCHEMA, validate_payload

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


def resolve_citations(citations, documents):
    blocks = {b.id: b for d in documents for b in d.blocks}
    resolved = []
    for citation in citations:
        if not isinstance(citation, dict) or set(citation) != {"block_id", "quote"}:
            raise ReviewError("Generated citations may specify only block_id and quote; locations are derived locally.")
        block = blocks.get(citation["block_id"])
        quote = citation["quote"]
        if block is None or not isinstance(quote, str) or not quote.strip() or quote not in block.text:
            raise ReviewError("Fabricated or mismatched manuscript quote/block rejected.")
        if block.text.count(quote) != 1:
            raise ReviewError("Ambiguous repeated quote; use a longer uniquely locating excerpt.")
        if block.kind == "heading" or block.section.lower().startswith(("references", "bibliography")):
            raise ReviewError("Heading/reference citations cannot establish manuscript methods or results.")
        start = block.text.index(quote)
        resolved.append(evidence(block, start, start + len(quote)))
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
    blocks = [b for d in documents for b in d.blocks if b.kind != "heading"]
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


def normalize_response(role, response, documents, extraction, provider_name):
    validate_payload(response, REVIEW_SCHEMA)
    findings, claims, strengths = [], [], []
    claim_map = {claim["id"]: claim["id"] for claim in extraction["claims"]}
    raw_ids = [row["id"] for row in response["findings"]]
    claim_raw_ids = [row["id"] for row in response["claims"]]
    if len(set(raw_ids)) != len(raw_ids) or len(set(claim_raw_ids)) != len(claim_raw_ids):
        raise ReviewError("Duplicate LLM IDs within one reviewer response.")
    rejected_claim_ids = set()
    for row in response["claims"]:
        try:
            sources = resolve_citations(row["manuscript_evidence"], documents)
            if not sources:
                rejected_claim_ids.add(row["id"])
                continue
            supporting = resolve_citations(row["supporting_evidence"], documents)
        except ReviewError:
            # A bad claim must not discard independently grounded findings from the role.
            rejected_claim_ids.add(row["id"])
            continue
        identifier = stable_id("central-claim", row["claim_text"])
        claim_map[row["id"]] = identifier
        flags = []
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
        # Numeric results cannot be introduced through the supporting-evidence summary.
        if set(re.findall(r"\b\d+(?:\.\d+)?\b", row["strongest_support"])) - set(
                re.findall(r"\b\d+(?:\.\d+)?\b", " ".join(ev.quote for ev in supporting))):
            flags.append("unsupported_support_summary")
        claims.append({
            **{key: value for key, value in row.items() if key not in ("manuscript_evidence", "supporting_evidence")},
            "id": identifier, "manuscript_evidence": [asdict(e) for e in sources],
            "supporting_evidence": [asdict(e) for e in supporting],
            "confidence_in_claim": "low" if set(flags) - {"feasibility_not_verified"} else ("medium" if row["confidence_in_claim"] == "high" else row["confidence_in_claim"]),
            "origin": "provider:" + provider_name, "reviewer_role": role,
            "quality_flags": sorted(set(flags + ["scientific_judgment_unverified"])),
        })
    for row in response["findings"]:
        citations, rejected_citations = [], 0
        for citation in row["citations"]:
            try:
                citations.extend(resolve_citations([citation], documents))
            except ReviewError:
                rejected_citations += 1
        if row["citations"] and not citations:
            continue
        unknown = set(row["claim_ids"]) - set(claim_map)
        truly_unknown = unknown - rejected_claim_ids
        linked_claim_ids = [claim_map[x] for x in row["claim_ids"] if x in claim_map]
        grounding, confidence, flags = support_audit(
            row["basis"], row["evidence_statement"], row["interpretation"],
            row["support_rationale"], citations, row["topic"], row["confidence"], row["issue_key"])
        if rejected_citations:
            flags.append("invalid_citations_dropped")
        if truly_unknown:
            flags.append("dangling_claim_ref_dropped")
        flags += action_flags(row["action"], row["severity"])
        flags += action_context_flags(row["action"], documents)
        substantive = row["basis"] in ("manuscript_direct", "manuscript_inference")
        disposition = ("needs_review" if grounding != "source_verified"
                       or any(flag in flags for flag in ("incomplete_action", "vague_action",
                                                        "text_edit_section_not_found", "text_edit_claim_not_found",
                                                        "action_requires_unavailable_data")) else "active")
        if disposition == "needs_review":
            confidence = "low"
        findings.append(prioritize(Finding(
            id="reviewer." + role + "." + row["id"],
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
            limitation="Exact source text was checked. Reviewer interpretation, external facts, and scientific adequacy are unverified.")))
    for row in response["strengths"]:
        sources = resolve_citations(row["citations"], documents)
        if not sources:
            raise ReviewError("A claimed strength needs manuscript evidence.")
        status, _, flags = support_audit("reviewer_opinion", row["text"], row["text"],
                                         row["text"], sources, "other", "low")
        strengths.append({"text": row["text"], "evidence": [asdict(e) for e in sources],
                          "reviewer_role": role, "grounding_status": status, "quality_flags": flags,
                          "interpretation_status": "reviewer_judgment_unverified"})
    return findings, claims, strengths


def reconcile(findings):
    """Conservative duplicate grouping; originals and rating disagreements remain."""
    candidates, events = [], []
    for finding in findings:
        if not finding.origin.startswith("provider:") or finding.disposition not in ("active", "confirmed"):
            continue
        anchors = {(e.block_id, e.start, e.end) for e in finding.evidence}
        canonical = None
        for existing in candidates:
            overlap = anchors & {(e.block_id, e.start, e.end) for e in existing.evidence}
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
