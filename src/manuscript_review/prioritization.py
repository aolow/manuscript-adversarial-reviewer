"""Transparent ordinal prioritization; no pseudo-precise scientific score."""
from .models import Finding


def prioritize(finding: Finding):
    if finding.severity == "fatal_flaw" or (
            finding.severity == "major" and finding.issue_status == "established_issue"
            and finding.category in ("leakage", "circularity", "single_cell")):
        finding.priority = "P0_verify_before_submission"
        reason = "The described design may invalidate a primary inference; verify it before relying on the result."
    elif finding.severity == "optional_strengthening" or finding.issue_status == "speculative_concern":
        finding.priority = "P3_optional_strengthening"
        reason = "An optional or speculative improvement; assess benefit before committing effort."
    elif finding.severity == "major" or (
            finding.severity == "moderate" and finding.value == "high"
            and finding.effort == "low" and finding.reviewer_likelihood == "high"):
        finding.priority = "P1_high_value_revision"
        reason = "Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention."
    else:
        finding.priority = "P2_targeted_clarification"
        reason = "Targeted reporting or analysis can clarify the concern after primary design risks are addressed."
    finding.priority_rationale = (
        reason + " Severity: " + finding.severity + "; notice likelihood: "
        + finding.reviewer_likelihood + "; effort: " + finding.effort
        + "; value: " + finding.value + ". These are editable heuristic judgments.")
    return finding
