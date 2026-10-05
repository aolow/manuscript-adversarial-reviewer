"""Two-version concern assessment with separate old/new source registries."""
from dataclasses import asdict
from importlib import resources

from .errors import ReviewError
from .grounding import resolve_citations
from .models import SEVERITIES, evidence
from .providers.contracts import COMPARISON_SCHEMA, validate_payload


def deterministic_assessments(old, new, comparison):
    old_items = [f for f in old.findings if f.disposition in ("active", "confirmed")]
    new_items = {f.id: f for f in new.findings if f.disposition in ("active", "confirmed")}
    reporting = {r["id"]: r for r in comparison["concerns_resolved"]}
    remediation = {r["id"]: r for r in comparison["reported_remediation"]}
    rows = []
    for finding in old_items:
        current = new_items.get(finding.id)
        status, scope = "cannot_determine", "not_verified"
        rationale = "No sufficient evidence establishes resolution; a disappearing flag is not a fix."
        new_evidence = []
        if current:
            new_evidence = [asdict(e) for e in current.evidence]
            status = "worsened" if SEVERITIES.index(current.severity) < SEVERITIES.index(finding.severity) else "unresolved"
            rationale = "The concern is still supported by detected passages in the revised manuscript."
        elif finding.id in reporting:
            status, scope = "resolved", "reporting_only"
            rationale = "A previously missing description is now reported; adequacy and execution remain unverified."
            new_evidence = reporting[finding.id]["evidence"]
        elif finding.id in remediation:
            status, scope = "partially_resolved", "reported_design_only"
            rationale = "A corrective design is described, but sufficiency and execution have not been verified."
            new_evidence = remediation[finding.id]["evidence"]
        # Context is provided for inspection, explicitly not called proof of resolution.
        if not new_evidence:
            related = [b for doc in new.documents for b in doc.blocks
                       if b.kind != "heading" and b.section == finding.manuscript_section]
            new_evidence = [asdict(evidence(b, relation="context_only")) for b in related[:2]]
        rows.append({"prior_issue_id": finding.id, "status": status, "rationale": rationale,
                     "prior_severity": finding.severity, "issue": finding.issue,
                     "old_evidence": [asdict(e) for e in finding.evidence], "new_evidence": new_evidence,
                     "resolution_scope": scope, "execution_verified": False,
                     "wording_softened_only": bool(current and comparison["claims_weakened"]
                                                   and finding.category in ("leakage", "confounding", "circularity", "single_cell")),
                     "remaining_action": current.suggested_fix if current else finding.suggested_fix,
                     "confidence": "low", "origin": "deterministic", "quality_flags": []})
    return rows


def comparison_packet(old, new):
    instructions = resources.files("manuscript_review.reviewers").joinpath("prompts/comparison.txt").read_text(encoding="utf-8")
    return {
        "instructions": instructions,
        "old_source_blocks": [asdict(b) for d in old.documents for b in d.blocks],
        "new_source_blocks": [asdict(b) for d in new.documents for b in d.blocks],
        "prior_issues": [asdict(f) for f in old.findings if f.disposition in ("active", "confirmed")],
        "new_deterministic_issues": [asdict(f) for f in new.findings if f.disposition in ("active", "confirmed")],
        "old_claim_candidates": old.extraction["claims"], "new_claim_candidates": new.extraction["claims"],
    }


def add_semantic_comparison(old, new, comparison, provider):
    packet = comparison_packet(old, new)
    try:
        response = provider.compare(packet)
        validate_payload(response, COMPARISON_SCHEMA)
        if provider.dry_run:
            comparison["llm"] = provider.metadata()
            return
        by_id = {r["prior_issue_id"]: r for r in comparison["issue_assessments"]}
        original_findings = {f.id: f for f in old.findings}
        new_active = {f.id: f for f in new.findings if f.disposition in ("active", "confirmed")}
        accepted, seen = {}, set()
        for row in response["assessments"]:
            identifier = row["prior_issue_id"]
            if identifier not in by_id or identifier in seen:
                raise ReviewError("Comparison returned unknown or duplicate prior issue IDs.")
            seen.add(identifier)
            old_ev = resolve_citations(row["old_citations"], old.documents)
            new_ev = resolve_citations(row["new_citations"], new.documents)
            flags = []
            status = row["status"]
            if not old_ev or not new_ev:
                status = "cannot_determine"
                flags.append("missing_two_version_evidence")
            # At least one old citation must anchor the actual issue being assessed.
            if old_ev and not {e.block_id for e in old_ev} & {e.block_id for e in original_findings[identifier].evidence}:
                status = "cannot_determine"
                flags.append("prior_issue_evidence_mismatch")
            if identifier in new_active and status in ("resolved", "no_longer_applicable"):
                status = "unresolved"
                flags.append("conflicts_with_persistent_deterministic_evidence")
            if row["wording_softened_only"] and status in ("resolved", "no_longer_applicable"):
                status = "unresolved"
                flags.append("wording_is_not_methodological_remediation")
            if status == "no_longer_applicable":
                import re
                if not any(re.search(r"\b(?:no longer|removed|withdrawn|outside the scope|do not claim)\b",
                                     e.quote, re.I) for e in new_ev):
                    status = "cannot_determine"
                    flags.append("scope_change_not_explicitly_supported")
            accepted[identifier] = {
                "prior_issue_id": identifier, "status": status, "rationale": row["rationale"],
                "prior_severity": original_findings[identifier].severity, "issue": original_findings[identifier].issue,
                "old_evidence": [asdict(e) for e in old_ev], "new_evidence": [asdict(e) for e in new_ev],
                "resolution_scope": "manuscript_description_only", "execution_verified": False,
                "wording_softened_only": row["wording_softened_only"],
                "remaining_action": row["remaining_action"], "confidence": "low" if flags else "medium",
                "origin": "provider:openai", "quality_flags": flags + ["semantic_judgment_unverified"],
            }
        for identifier, fallback in by_id.items():
            if identifier not in accepted:
                fallback["quality_flags"].append("not_assessed_by_llm")
        comparison["issue_assessments"] = [accepted.get(identifier, row) for identifier, row in by_id.items()]
        comparison["limitations"].extend(response["limitations"])
        comparison["llm"] = provider.metadata()
        comparison["llm"]["coverage"] = {"prior_issues": len(by_id), "assessed_by_llm": len(accepted)}
        comparison["llm"]["incomplete"] = len(accepted) != len(by_id)
    except ReviewError as exc:
        comparison["llm"] = {**provider.metadata(), "failed": True, "error": str(exc)}
        comparison["limitations"].append("LLM comparison failed; deterministic assessment retained.")


def major_progress(comparison):
    groups = {k: [] for k in ("resolved", "partially_resolved", "persistent", "worsened", "unclear",
                              "newly_introduced_or_detected", "scope_withdrawn")}
    mapping = {"unresolved": "persistent", "cannot_determine": "unclear",
               "no_longer_applicable": "scope_withdrawn"}
    for row in comparison["issue_assessments"]:
        if row.get("prior_severity") in ("major", "fatal_flaw"):
            groups[mapping.get(row["status"], row["status"])].append(row)
    groups["newly_introduced_or_detected"] = [r for r in comparison["new_concerns"]
                                            if r.get("severity") in ("major", "fatal_flaw")]
    return groups
