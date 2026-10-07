from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import re

from .extraction import substantive_blocks, sentences
from .models import evidence

SECTION_TITLES = [
    ("executive_assessment", "Executive assessment"),
    ("claimed_contribution", "Claimed contribution"),
    ("strongest_evidence", "Strongest evidence"),
    ("weakest_links", "Weakest links"),
    ("scientific_concerns", "Major scientific concerns"),
    ("methods_statistics", "Major methods/statistics concerns"),
    ("biological_interpretation", "Biological interpretation concerns"),
    ("claim_evidence_map", "Claim-to-evidence map"),
    ("leakage_confounding_circularity", "Potential leakage/confounding/circularity"),
    ("missing_controls", "Missing controls or analyses"),
    ("alternative_explanations", "Alternative explanations"),
    ("reviewer2", "Reviewer-2 style objections"),
    ("writing_clarity", "Writing/clarity problems"),
    ("innovation_positioning", "Innovation and positioning assessment"),
    ("reproducibility", "Reproducibility/reporting gaps"),
    ("revision_plan", "Prioritized revision plan"),
    ("additional_analyses", "Suggested additional analyses"),
    ("text_edits", "Suggested text edits"),
    ("journal_fit", "Journal-fit assessment"),
    ("uncertainty", "Confidence/uncertainty notes"),
]


def build_sections(review):
    active = [f for f in review.findings if f.disposition in ("active", "confirmed")]
    ordered = sorted(active, key=lambda f: (f.priority, f.id))
    by_category = lambda names: [f.id for f in active if f.category in names]
    counts = Counter(f.severity for f in active)
    sections = {key: {"key": key, "title": title, "summary": "", "items": [], "finding_ids": []}
                for key, title in SECTION_TITLES}
    sections["executive_assessment"]["summary"] = (
        "Text audit: %d active concerns (%s). These are review leads, not a judgment "
        "of scientific validity or submission acceptance. No automatic finding is classified as a fatal flaw."
        % (len(active), ", ".join("%s: %d" % pair for pair in sorted(counts.items())) or "none"))
    sections["claimed_contribution"].update(
        summary="Heuristic claim candidates; centrality and support require scientific review.",
        items=[{"text": c["text"], "evidence": [c["evidence"]]} for c in review.extraction["claims"][:20]])
    results = []
    for block in substantive_blocks(review.documents):
        if block.section.startswith(("Results", "Results and Discussion")) and re.search(r"\d", block.text):
            results.append({"text": "Reported quantitative result (not independently verified): " + block.text,
                            "evidence": [asdict(evidence(block, relation="reported_result"))]})
    sections["strongest_evidence"].update(
        summary="Scientific strength cannot be ranked by text heuristics. Candidate reported quantitative results are listed below.",
        items=results[:8])
    sections["weakest_links"].update(
        summary="Highest-priority active concerns from the rule rubric.",
        finding_ids=[f.id for f in ordered[:8]])
    sections["scientific_concerns"]["finding_ids"] = by_category(["interpretation", "validation", "perturbation", "design"])
    sections["methods_statistics"]["finding_ids"] = by_category(["statistics", "leakage", "single_cell", "confounding", "design"])
    sections["biological_interpretation"]["finding_ids"] = by_category(["interpretation", "circularity"])
    sections["claim_evidence_map"].update(
        summary="Explicit figure/table links are candidates, not confirmed support. Unlinked claims have unestablished support.",
        items=review.extraction["claim_evidence_map"])
    sections["leakage_confounding_circularity"]["finding_ids"] = by_category(["leakage", "confounding", "circularity"])
    sections["missing_controls"].update(
        summary="Reporting gaps require verification of applicability and of work that may exist outside the supplied text.",
        finding_ids=[f.id for f in active if f.id.startswith("check.") and f.category not in ("reporting", "reproducibility")])
    alternatives = {
        "confounding": "Could donor, batch, cancer type, platform, or ascertainment explain the reported difference?",
        "leakage": "Could evaluation information entering development account for apparent predictive performance?",
        "single_cell": "Could donor composition, cell counts, annotation, or integration choices explain the signal?",
        "perturbation": "Could viability, stress, efficiency, or off-target effects explain the phenotype?",
        "circularity": "Could construction or annotation choices make the validation result true by definition?",
    }
    sections["alternative_explanations"].update(
        summary="Hypotheses to test, not established explanations.",
        items=[{"text": alternatives[cat], "finding_ids": by_category([cat])}
               for cat in alternatives if by_category([cat])])
    sections["reviewer2"]["items"] = [{"text": q["question"], "finding_ids": [q["finding_id"]]}
                                    for run in review.reviewer_runs if run["role"] == "reviewer2"
                                    for q in run["questions"]]
    for block in substantive_blocks(review.documents):
        for text, ev in sentences(block):
            if len(text.split()) > 55:
                sections["writing_clarity"]["items"].append({
                    "text": "Long sentence: consider separating the result, interpretation, and caveat.",
                    "evidence": [asdict(ev)]})
    sections["writing_clarity"]["summary"] = "Length-based suggestions are stylistic leads, not a comprehensive prose edit."
    sections["innovation_positioning"].update(
        summary="The offline tool cannot verify novelty or the current literature. Compare the precise contribution with the closest prior studies.",
        finding_ids=by_category(["positioning"]))
    sections["reproducibility"]["finding_ids"] = by_category(["reproducibility", "reporting"])
    sections["revision_plan"]["items"] = [
        {"text": f.priority + ": " + f.suggested_fix, "finding_ids": [f.id],
         "rationale": f.priority_rationale} for f in ordered]
    sections["additional_analyses"]["items"] = [
        {"text": f.suggested_analysis, "finding_ids": [f.id],
         "condition": "First verify the concern and applicability; this is a proposal, not a reported result."}
        for f in ordered if f.category not in ("reporting", "reproducibility")]
    for finding in active:
        if finding.rule_id in ("causal_overclaim", "conservation_overclaim", "novelty_overclaim"):
            replacement = ("These results are consistent with [specific interpretation]; the proposed mechanism "
                           "requires independent testing." if finding.rule_id != "novelty_overclaim" else
                           "We present [specific contribution] and evaluate it against [named comparators].")
            sections["text_edits"]["items"].append({
                "text": "Conditional edit template: " + replacement,
                "original": finding.claim, "finding_ids": [finding.id],
                "condition": "Fill placeholders only with supported facts; confirm the revised sentence fits the actual study."})
    sections["journal_fit"]["summary"] = (
        "Target: %s. Current scope, article types, and editorial requirements were not checked. "
        "Fit is not established from a journal name alone. Assess audience, contribution type, "
        "validation depth, reporting requirements, and the journal's current aims."
        % (review.target_journal or "not supplied"))
    reviewer_limitations = [
        {"text": run["role"] + " reviewer limitation: " + limitation}
        for run in review.reviewer_runs
        for limitation in run.get("limitations", [])
        if isinstance(limitation, str) and limitation.strip()
    ]
    sections["uncertainty"].update(
        summary="Confidence describes the text match, not the probability that a scientific conclusion is wrong.",
        items=[{"text": warning} for warning in review.warnings + review.extraction["limitations"]]
        + reviewer_limitations + [
            {"text": "Absence means not established from the supplied text. Reported cues do not establish method adequacy."},
            {"text": "Established issues identify an explicitly described design or wording; they do not verify execution or effect on results."},
            {"text": "Manual overrides are version-bound and retained with reasons. Dismissed findings remain in JSON."}])
    for section in sections.values():
        if not section["summary"] and not section["items"] and not section["finding_ids"]:
            section["summary"] = "No finding generated in this scope; adequacy is not established."
    return list(sections.values())


def _clean(text):
    return str(text).replace("\r", "").replace("<", "&lt;").replace(">", "&gt;")


def citation(ev):
    location = [ev["document_id"], ev["section"]]
    for key, label in (("page", "page"), ("line_start", "line"), ("paragraph", "paragraph")):
        if ev.get(key) is not None:
            location.append(label + " " + str(ev[key]))
    location.append("block " + ev["block_id"])
    return "; ".join(location)


def render_markdown(review):
    lines = ["# Manuscript adversarial review", "",
             "**Run:** " + review.run_id + "  ", "**Schema:** " + review.schema_version + "  ",
             "**Mode:** " + ("provider-assisted" if any(r["mode"] in ("provider", "manual_import") for r in review.reviewer_runs)
                            else "offline deterministic audit") + "", "",
             "This report supports scientific judgment. Findings are traceable review leads; "
             "missing reporting is not proof of missing work.", ""]
    lines.extend(render_adversarial(review))
    lines.extend(["<details>", "<summary>Detailed 20-section audit, findings, and deterministic checklist</summary>", ""])
    for number, section in enumerate(review.sections, 1):
        lines.extend(["## %d. %s" % (number, section["title"]), ""])
        if section["summary"]:
            lines.extend([_clean(section["summary"]), ""])
        for item in section["items"]:
            if "claim_id" in item:
                lines.append("- **" + item["claim_id"] + "**: " + _clean(item["claim"]))
                lines.append("  - Support: " + item["support_status"] + ". " + _clean(item["interpretation"]))
                lines.append("  - Source: " + _clean(citation(item["claim_evidence"])))
                for candidate in item["candidate_evidence"]:
                    lines.append("  - Candidate: " + _clean(citation(candidate)))
            else:
                lines.append("- " + _clean(item["text"]))
                if item.get("original"):
                    lines.append("  - Original: " + _clean(item["original"]))
                if item.get("condition"):
                    lines.append("  - Condition: " + _clean(item["condition"]))
                if item.get("rationale"):
                    lines.append("  - Rationale: " + _clean(item["rationale"]))
                for ev in item.get("evidence", []):
                    lines.append("  - Source: " + _clean(citation(ev)))
                if item.get("finding_ids"):
                    lines.append("  - Findings: " + ", ".join("[" + fid + "](#" + fid.replace(".", "") + ")"
                                                            for fid in item["finding_ids"]))
        if section["finding_ids"]:
            lines.extend(["- [" + fid + "](#" + fid.replace(".", "") + ")" for fid in section["finding_ids"]])
        lines.append("")
    lines.extend(["## Finding details", ""])
    for finding in sorted(review.findings, key=lambda f: (f.disposition == "dismissed", f.priority, f.id)):
        lines.extend(["### " + finding.id, "",
                      "**%s | %s | %s | confidence: %s | %s**" %
                      (finding.severity, finding.issue_status, finding.priority, finding.confidence, finding.disposition), "",
                      _clean(finding.issue), "",
                      "**Why it matters:** " + _clean(finding.why_it_matters), "",
                      "**Suggested fix:** " + _clean(finding.suggested_fix), "",
                      "**Suggested analysis:** " + _clean(finding.suggested_analysis), "",
                      "**Priority rationale:** " + _clean(finding.priority_rationale), "",
                      "**Limit:** " + _clean(finding.limitation), ""])
        if finding.origin.startswith("provider:"):
            lines.extend(["**Basis / grounding:** " + finding.basis + " / " + finding.grounding_status, "",
                          "**Reviewer interpretation:** " + _clean(finding.issue), "",
                          "**Support rationale:** " + _clean(finding.support_rationale), "",
                          "**Quality flags:** " + ", ".join(finding.quality_flags or ["none"]), ""])
            if finding.duplicate_of:
                lines.extend(["**Duplicate of:** " + finding.duplicate_of, ""])
        for ev in finding.evidence:
            lines.extend(["> " + _clean(ev.quote).replace("\n", "\n> "), "",
                          "Source: " + _clean(citation(asdict(ev))) + " (" + ev.relation + ")", ""])
        if finding.manual_note:
            lines.extend(["**Manual override:** " + _clean(finding.manual_note), ""])
    lines.extend(["## Reporting checklist", "", "| Check | Status | Confidence |",
                  "| --- | --- | --- |"])
    for check in review.checklist:
        lines.append("| %s | %s | %s |" % (check.label, check.status, check.confidence))
    lines.extend(["", "</details>", ""])
    if review.comparison:
        lines.extend(["", render_comparison(review.comparison)])
    lines.extend(["", "## Input provenance", ""])
    for doc in review.documents:
        lines.append("- %s: %s; SHA-256 %s" % (doc.id, _clean(doc.name), doc.sha256))
    return "\n".join(lines) + "\n"


def _action_lines(action, prefix="- "):
    labels = {"input": "Input", "comparison": "Comparison", "held_out_unit": "Held-out / biological unit",
              "metric": "Metric", "expected_interpretation": "Interpretation / failure criterion",
              "text_section": "Section", "text_claim": "Claim to revise", "recommended_framing": "Framing"}
    return [prefix + "**" + label + ":** " + _clean(action[key])
            for key, label in labels.items() if action.get(key)]


def render_adversarial(review):
    data = review.adversarial
    if not data:
        return []
    by_id = {f.id: f for f in review.findings}
    lines = ["## Revision brief", "", "**What the paper is trying to claim**", ""]
    for claim in review.claim_analyses[:3]:
        lines.append("- " + _clean(claim["claim_text"]) + " (" + claim["id"] + ")")
    if not review.claim_analyses:
        lines.append("A central claim was not reliably extracted; identify it before interpreting this review.")
    claim_text = " ".join(c["claim_text"] for c in review.claim_analyses).lower()
    types = []
    for pattern, label in (
        (r"predict|biomarker|diagnos", "predictive or biomarker contribution"),
        (r"framework|algorithm|method|pipeline", "methodological contribution"),
        (r"mechanis|caus|pathway|biolog", "biological interpretation"),
        (r"atlas|dataset|resource", "dataset or reference resource"),
    ):
        if re.search(pattern, claim_text):
            types.append(label)
    lines.extend(["", "**Contribution if the claims survive:** " +
                  (", ".join(types) if types else "Requires scientific judgment.") +
                  " — inferred from claim wording; novelty and impact remain unverified.", "",
                  "## What could kill this paper", "", data["what_could_kill_this_paper"]["note"], ""])
    for fid in data["what_could_kill_this_paper"]["finding_ids"]:
        finding = by_id[fid]
        lines.extend(["- **[" + fid + "](#" + fid.replace(".", "") + ")** — " + _clean(finding.issue),
                      "  - Why central: " + _clean(finding.why_it_matters),
                      "  - " + finding.severity + "; " + finding.issue_status + "; confidence: " + finding.confidence])
    if not data["what_could_kill_this_paper"]["finding_ids"]:
        lines.append("No sufficiently grounded major threat was identified; this is not evidence of scientific validity.")
    lines.extend(["", "## Major strengths", ""])
    for strength in data["major_strengths"][:3]:
        lines.append("- " + _clean(strength["text"]) + " (" + strength["interpretation_status"] + ")")
        for ev in strength["evidence"][:1]:
            lines.append("  - " + _clean(citation(ev)))
    if not data["major_strengths"]:
        lines.append("Not established by the current review.")
    lines.extend(["", "## Analyses most likely to change the story", ""])
    for fid in data["high_priority_analyses"][:3]:
        finding = by_id[fid]
        lines.append("- **" + fid + "**: " + _clean(finding.suggested_fix))
        lines.extend(_action_lines(finding.action, "  - "))
    if not data["high_priority_analyses"]:
        lines.append("No decisive feasible analysis was established by this review.")
    lines.extend(["", "## Text and positioning changes", "",
                  "These address wording; they do not repair an unsupported experiment or design.", ""])
    for fid in data["writing_framing"][:3]:
        finding = by_id[fid]
        lines.append("- **" + _clean(finding.manuscript_section) + "**: " + _clean(finding.suggested_fix) + " (" + fid + ")")
    if not data["writing_framing"]:
        lines.append("No source-specific text-only correction was established.")
    attacks = [f for f in review.findings if f.disposition in ("active", "confirmed")
               and "reviewer2" in f.reviewer_roles and f.origin.startswith("provider:")]
    if not attacks:
        attacks = [by_id[fid] for fid in data["what_could_kill_this_paper"]["finding_ids"]]
    lines.extend(["", "## Likely Reviewer 2 attacks", ""])
    for finding in attacks[:3]:
        lines.append("- " + _clean(finding.issue) + " — " + _clean(finding.suggested_analysis))
    if not attacks:
        lines.append("No specific supported attack was identified; this does not establish readiness.")
    lines.extend(["", "<details>", "<summary>Full claim analyses and revision plan</summary>", "",
                  "## Central claims and evidence", ""])
    for claim in review.claim_analyses[:7]:
        lines.extend(["### Claim %d: %s" % (claim["rank"], claim["importance"]), "",
                      _clean(claim["claim_text"]), "",
                      "- Importance: " + _clean(claim["importance_rationale"]),
                      "- Strongest reported support: " + _clean(claim["strongest_support"]),
                      "- Strongest weakness: " + _clean(claim["strongest_weakness"]),
                      "- Alternative explanation: " + _clean(claim["alternative_explanation"]),
                      "- Impact if false: " + _clean(claim["impact_if_false"]),
                      "- Confidence in claim: " + claim["confidence_in_claim"] + " (" + claim["origin"] + ")"])
        for ev in claim["manuscript_evidence"] + claim["supporting_evidence"]:
            lines.append("- Source: " + _clean(citation(ev)) + "; excerpt: " + _clean(ev["quote"]))
        framing = []
        for key, label in (("falsification_analysis", "Falsification test"),
                           ("decisive_analysis", "Proposed decisive analysis")):
            action = claim[key]
            if action.get("kind") in ("analysis", "experiment"):
                lines.extend(["", "**" + label + ":**", ""] + _action_lines(action))
            else:
                lines.extend(["", "**" + label + ":** Not specified by this review."])
                if action.get("kind") == "text" and action not in framing:
                    framing.append(action)
        for action in framing:
            lines.extend(["", "**Proposed framing change:**", ""] + _action_lines(action))
        lines.append("")
    for key, title in (
        ("high_priority_analyses", "High-priority analyses"), ("secondary_analyses", "Secondary analyses"),
        ("writing_framing", "Writing and framing changes"), ("novelty_positioning", "Novelty and positioning"),
        ("reproducibility_gaps", "Reproducibility gaps"), ("lower_priority_reporting", "Lower-priority reporting fixes"),
        ("requires_human_review", "Unverified reviewer suggestions"),
    ):
        lines.extend(["## " + title, ""])
        for fid in data[key][:8]:
            finding = by_id[fid]
            lines.extend(["- **" + fid + "**: " + _clean(finding.suggested_fix)])
            if key in ("high_priority_analyses", "writing_framing"):
                lines.extend(_action_lines(finding.action, "  - "))
            if finding.disposition == "needs_review":
                lines.append("  - Requires verification: " + ", ".join(finding.quality_flags))
        if len(data[key]) > 8:
            lines.append("- Additional items are retained in JSON and the detailed audit.")
        if not data[key]:
            lines.append("No additional item identified in this scope.")
        lines.append("")
    lines.extend(["</details>", ""])
    if review.quality.get("failed_roles"):
        lines.extend(["**Incomplete LLM review:** failed roles: " + ", ".join(review.quality["failed_roles"]),
                      "The independent deterministic audit is preserved.", ""])
    if review.llm.get("dry_run"):
        lines.extend(["**Dry run:** exact requests were exported locally; no model judgment was performed.", ""])
    return lines


def render_comparison(comparison):
    lines = ["# Manuscript version comparison", "", comparison["rigor_assessment"], "",
             comparison["positioning_assessment"], ""]
    from .resolution import major_progress
    labels = {"resolved": "Resolved", "partially_resolved": "Partially resolved", "persistent": "Persistent",
              "worsened": "Worsened", "unclear": "Unclear", "newly_introduced_or_detected": "Newly introduced / detected",
              "scope_withdrawn": "Scope withdrawn (not a methodological repair)"}
    lines.extend(["## Major concerns at a glance", "",
                  "Newly detected concerns may reflect new disclosure or prior detection gaps. Resolution does not verify execution.", ""])
    for group, rows in major_progress(comparison).items():
        lines.append("- **" + labels[group] + " (" + str(len(rows)) + ")**")
        for row in rows:
            identifier = row.get("prior_issue_id", row.get("id"))
            lines.append("  - " + identifier + ": " + _clean(row.get("issue", row.get("summary", ""))))
    if any("prior_severity" not in r for r in comparison["issue_assessments"]):
        lines.append("Legacy comparison lacks severity metadata; inspect the complete assessments below.")
    lines.append("")
    if comparison.get("issue_assessments"):
        lines.extend(["## Scientific concern resolution", "",
                      "Resolution is assessed from supplied manuscript descriptions; execution is not independently verified.", ""])
        for row in comparison["issue_assessments"]:
            lines.extend(["- **" + row["prior_issue_id"] + ": " + row["status"] + "** — " + _clean(row["rationale"]),
                          "  - Scope: " + row["resolution_scope"]])
            if row.get("wording_softened_only"):
                lines.append("  - Wording softened while the methodological concern remains.")
            for side in ("old_evidence", "new_evidence"):
                for ev in row[side]:
                    lines.append("  - " + side.split("_")[0] + ": " + _clean(citation(ev)) + "; " + _clean(ev["quote"]))
        lines.append("")
    for key, label in (
        ("substantive_changes", "Textual changes in substantive sections"),
        ("claims_strengthened", "Claims strengthened in wording"),
        ("claims_weakened", "Claims weakened in wording"),
        ("concerns_resolved", "Reporting concerns with new affirmative cues"),
        ("reported_remediation", "Explicit design concerns with candidate remediation"),
        ("concerns_unresolved", "Concerns still detected"),
        ("new_concerns", "Newly detected concerns"),
        ("no_longer_detected", "Concerns no longer detected without resolution evidence"),
    ):
        lines.extend(["## " + label, ""])
        entries = comparison[key]
        if not entries:
            lines.extend(["None detected.", ""])
        for entry in entries:
            lines.append("- " + _clean(entry.get("summary") or entry.get("id", "")))
            if "old_text" in entry:
                lines.append("  - Before: " + _clean(entry["old_text"]))
            if "new_text" in entry:
                lines.append("  - After: " + _clean(entry["new_text"]))
            for ev in entry.get("evidence", []):
                lines.append("  - Source: " + _clean(citation(ev)))
        lines.append("")
    lines.extend(["## Comparison limits", ""] + ["- " + _clean(s) for s in comparison["limitations"]])
    return "\n".join(lines) + "\n"
