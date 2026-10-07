"""Version-aware text comparison, with explicitly bounded resolution claims."""
from __future__ import annotations

from dataclasses import asdict
from difflib import SequenceMatcher
import re
from .extraction import substantive_blocks, sentences
from .models import SCHEMA_VERSION

REMEDIATION = {
    "feature_selection_before_split": r"\b(?:feature|gene) selection\b.{0,65}\b(?:within|inside|only)\b.{0,40}\btraining\b",
    "cell_pseudoreplication": r"\b(?:pseudobulk|mixed.effects|hierarchical model|donor.level)\b",
    "test_set_tuning": r"\b(?:nested cross.validation|untouched test set|inner validation)\b",
    "cohort_reuse": r"\b(?:disjoint|independent external)\b.{0,50}\b(?:cohort|dataset)\b",
    "circular_signature": r"\b(?:independent|disjoint|non.overlapping)\b.{0,45}\b(?:features|genes|markers)\b",
}


def _strength(text):
    if re.search(r"\b(?:prove|proves|establish|establishes|causal|first.ever)\b", text, re.I):
        return 2
    if re.search(r"\b(?:may|suggest|suggests|consistent with|association|associated)\b", text, re.I):
        return 0
    return 1


def compare_reviews(old, new):
    from .rules.engine import affirmative
    comparison = {
        "schema_version": SCHEMA_VERSION, "old_run_id": old.run_id, "new_run_id": new.run_id,
        "old_document_hashes": {d.id: d.sha256 for d in old.documents},
        "new_document_hashes": {d.id: d.sha256 for d in new.documents},
        "substantive_changes": [], "claims_strengthened": [], "claims_weakened": [],
        "concerns_resolved": [], "reported_remediation": [], "concerns_unresolved": [],
        "new_concerns": [], "no_longer_detected": [],
        "rigor_assessment": "", "positioning_assessment": "",
        "limitations": [
            "Resolution refers to reporting cues only; no analysis execution or scientific correctness was verified.",
            "Disappearing findings can reflect removed text, changed vocabulary, or changed applicability.",
            "Claim-strength changes measure wording, not increased or decreased evidential support.",
            "Text matching may miss paraphrases, reorderings, or moved sections.",
            "Each rule aggregates a concern family; one repaired instance does not prove all instances are resolved.",
        ],
    }
    old_groups, new_groups = {}, {}
    for review, groups in ((old, old_groups), (new, new_groups)):
        for block in substantive_blocks(review.documents):
            groups.setdefault((block.document_id, block.section), []).append(block.text)
    for key in sorted(set(old_groups) | set(new_groups)):
        before, after = old_groups.get(key, []), new_groups.get(key, [])
        matcher = SequenceMatcher(None, before, after, autojunk=False)
        for tag, a, b, c, d in matcher.get_opcodes():
            if tag != "equal":
                comparison["substantive_changes"].append({
                    "document_id": key[0], "section": key[1], "change_type": tag,
                    "summary": key[0] + " / " + key[1] + ": " + tag,
                    "old_text": "\n\n".join(before[a:b]), "new_text": "\n\n".join(after[c:d]),
                    "interpretation": "Text changed; scientific substance requires manual review."})
    remaining = list(new.extraction["claims"])
    for claim in old.extraction["claims"]:
        eligible = [candidate for candidate in remaining if candidate["section"] == claim["section"]]
        if not eligible:
            continue
        best = max(eligible, key=lambda c: SequenceMatcher(None, claim["text"], c["text"]).ratio())
        similarity = SequenceMatcher(None, claim["text"], best["text"]).ratio()
        if similarity < 0.4:
            continue
        remaining.remove(best)
        change = _strength(best["text"]) - _strength(claim["text"])
        if change:
            comparison["claims_strengthened" if change > 0 else "claims_weakened"].append({
                "old_claim_id": claim["id"], "new_claim_id": best["id"],
                "old_text": claim["text"], "new_text": best["text"],
                "summary": "Matched claim has stronger wording." if change > 0 else "Matched claim has more qualified wording.",
                "evidence": [claim["evidence"], best["evidence"]],
                "matching_confidence": "medium" if similarity > 0.7 else "low"})
    old_findings = {f.id: f for f in old.findings if f.disposition in ("active", "confirmed")}
    new_findings = {f.id: f for f in new.findings if f.disposition in ("active", "confirmed")}
    new_checks = {c.id: c for c in new.checklist}
    for identifier, finding in old_findings.items():
        row = {"id": identifier, "summary": identifier, "evidence": []}
        if identifier in new_findings:
            row.update(summary=identifier + ": still detected; compare individual passages.",
                       evidence=[asdict(e) for e in new_findings[identifier].evidence])
            comparison["concerns_unresolved"].append(row)
        elif finding.id.startswith("check.") and finding.rule_id in new_checks and new_checks[finding.rule_id].status == "reported":
            row.update(summary=identifier + ": a new affirmative reporting cue was found; adequacy is unverified.",
                       resolution_scope="reporting_only", scientific_resolution="not_verified",
                       evidence=[asdict(e) for e in new_checks[finding.rule_id].evidence])
            comparison["concerns_resolved"].append(row)
        else:
            remediation = REMEDIATION.get(finding.rule_id)
            hits = []
            if remediation:
                for block in substantive_blocks(new.documents):
                    for text, ev in sentences(block):
                        match = re.search(remediation, text, re.I | re.S)
                        if match and affirmative(text, *match.span()):
                            hits.append(asdict(ev))
            if hits:
                row.update(summary=identifier + ": candidate corrective design is now described; execution and adequacy unverified.",
                           resolution_scope="reported_design_only", scientific_resolution="not_verified", evidence=hits)
                comparison["reported_remediation"].append(row)
            else:
                row["summary"] = identifier + ": no longer detected; resolution is not established."
                comparison["no_longer_detected"].append(row)
    for identifier in sorted(set(new_findings) - set(old_findings)):
        comparison["new_concerns"].append({
            "id": identifier, "summary": identifier + ": newly detected, possibly due to newly disclosed methods.",
            "severity": new_findings[identifier].severity, "issue": new_findings[identifier].issue,
            "evidence": [asdict(e) for e in new_findings[identifier].evidence]})
    changed = bool(comparison["substantive_changes"])
    positive = bool(comparison["concerns_resolved"] or comparison["reported_remediation"])
    comparison["rigor_assessment"] = (
        "No substantive-text changes were detected." if not changed else
        "The revision contains candidate improvements in reporting or design description. Material improvement "
        "in scientific rigor is not established without inspecting the actual analyses." if positive else
        "The text changed, but material improvement in scientific rigor is not established from this comparison.")
    comparison["positioning_assessment"] = (
        "Some matched claims use more qualified wording, which may make positioning more defensible; "
        "novelty and evidential adequacy remain unverified." if comparison["claims_weakened"] else
        "A material improvement in positioning is not established by the wording checks.")
    from .resolution import deterministic_assessments
    comparison["issue_assessments"] = deterministic_assessments(old, new, comparison)
    comparison["llm"] = {}
    if old.configuration != new.configuration:
        comparison["limitations"].append("Old and new audit configurations differ; changed flags may reflect overrides or coverage changes.")
    if old.tool_version != new.tool_version:
        comparison["limitations"].append(
            "Old and new reviews were generated by different tool versions; changed findings may reflect engine changes as well as manuscript revision.")
    return comparison
