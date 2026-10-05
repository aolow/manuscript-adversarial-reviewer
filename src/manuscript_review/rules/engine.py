from __future__ import annotations

import re
from ..extraction import substantive_blocks, sentences
from ..models import CheckResult, Finding, evidence
from ..prioritization import prioritize
from .catalogue import CHECKS, PATTERNS

ROLE_MAP = {
    "leakage": ["methods", "statistics"], "circularity": ["scientific", "methods"],
    "single_cell": ["methods", "statistics"], "statistics": ["statistics"],
    "confounding": ["methods", "statistics"], "validation": ["methods", "scientific"],
    "interpretation": ["scientific"], "positioning": ["novelty"],
    "clinical": ["clinical"], "perturbation": ["scientific", "methods"],
    "reporting": ["methods"], "reproducibility": ["methods"], "design": ["methods"],
}
NONASSERTION = re.compile(
    r"\b(?:will|would|should|could|might|future work|plan to|planned|propos\w* to|"
    r"previous studies|prior work|for example|hypothetical|we recommend|whether|"
    r"requires? further|needs? further|pending|remain(?:s)? to be)\b", re.I)
NEGATION = re.compile(
    r"\b(?:no|not|never|without|neither|avoid\w*|prevent\w*|lack\w*|absen\w*|"
    r"unavailable|unreported|unperformed|unassessed|omitt\w*|didn't|wasn't|weren't|cannot)\b", re.I)


def clause_for(text, start, end):
    # Bound scope to a semicolon or explicit contrast, avoiding unrelated negation.
    bounds = [0]
    for match in re.finditer(r";|\b(?:but|however|whereas)\b", text, re.I):
        bounds.extend([match.start(), match.end()])
    bounds.append(len(text))
    left = max(n for n in bounds if n <= start)
    right = min(n for n in bounds if n >= end)
    return text[left:right]


def affirmative(text, start, end):
    clause = clause_for(text, start, end)
    # Phrases that explicitly report safe handling should remain affirmative.
    clause = re.sub(r"\bno missing (?:values|data)\b", "complete data", clause, flags=re.I)
    return not NONASSERTION.search(clause) and not NEGATION.search(clause)


def run_rules(documents, extraction, disabled=()):
    blocks = substantive_blocks(documents)
    candidates = [(b, text, ev) for b in blocks for text, ev in sentences(b)]
    domains = set(extraction["domains"])
    findings, results = [], []
    for spec in CHECKS:
        if spec.id in disabled:
            continue
        relevant = spec.domain in domains
        positive, negative, uncertain = [], [], []
        if relevant:
            for block, text, ev in candidates:
                match = re.search(spec.pattern, text, re.I | re.S)
                if not match:
                    continue
                clause = clause_for(text, *match.span())
                negative_outcome = (
                    spec.id == "missingness" and re.search(r"\bno missing (?:values|data)\b", clause, re.I) or
                    spec.id == "doublets" and re.search(r"\bno doublets? (?:were )?(?:detected|identified|found)\b", clause, re.I) or
                    spec.id == "ambient_rna" and re.search(r"\bno ambient RNA (?:was )?(?:detected|identified|found)\b", clause, re.I))
                missing_interval = spec.id == "confidence_intervals" and re.search(
                    r"\bmissing (?:confidence|credible) intervals?\b", clause, re.I)
                if missing_interval:
                    negative.append(ev)
                elif spec.id == "limitations" or (negative_outcome and not NONASSERTION.search(clause)) or affirmative(text, *match.span()):
                    positive.append(ev)
                elif NONASSERTION.search(clause):
                    uncertain.append(ev)
                else:
                    negative.append(ev)
        status = ("not_applicable" if not relevant else
                  "conflicting" if positive and negative else
                  "reported" if positive else
                  "explicit_negative_statement" if negative else "not_established")
        interpretation = {
            "not_applicable": "No applicability cue detected; this is not a verified determination of irrelevance.",
            "reported": "An affirmative textual cue was found; adequacy and implementation are not verified.",
            "conflicting": "Affirmative and negative cues coexist; manually reconcile their scope.",
            "explicit_negative_statement": "A negative textual cue was found; verify negation scope and applicability.",
            "not_established": "Not established from the manuscript text searched; this does not establish that the work was not done.",
        }[status]
        hits = (positive + negative + uncertain)[:8]
        results.append(CheckResult(spec.id, spec.label, status, hits,
                                   [d.id for d in documents], len(blocks) if relevant else 0,
                                   "medium" if positive or negative else "low", interpretation, spec.domain))
        if status in ("not_applicable", "reported"):
            continue
        anchors = hits or [evidence(b, relation="context_only") for b in blocks
                           if b.section.startswith("Methods")][:2]
        if not anchors and blocks:
            anchors = [evidence(blocks[0], relation="context_only")]
        # Absence evidence is the declared search scope, not a quote that proves omission.
        issue = spec.label + (": contradictory reporting cues require reconciliation." if status == "conflicting"
                              else ": not established from the manuscript.")
        findings.append(prioritize(Finding(
            id="check." + spec.id, rule_id=spec.id, severity=spec.severity,
            category=spec.category, manuscript_section=anchors[0].section if anchors else "Unsectioned",
            claim=anchors[0].quote if anchors else "No applicable extractable passage.",
            issue=issue, why_it_matters=spec.why, evidence=anchors,
            suggested_fix=spec.fix, suggested_analysis=spec.analysis,
            confidence="medium" if negative or positive else "low", issue_status="plausible_issue",
            reviewer_roles=ROLE_MAP[spec.category],
            effort="low" if spec.category in ("reporting", "reproducibility") else "medium",
            limitation=interpretation + " Section and language heuristics can miss synonymous or implicit descriptions.")))
    for spec in PATTERNS:
        if spec.id in disabled or spec.domain not in domains:
            continue
        hits = []
        for block, text, ev in candidates:
            match = re.search(spec.pattern, text, re.I | re.S)
            if spec.id == "design_confounding" and not match:
                assignments = re.findall(
                    r"\ball\s+([\w-]+)(?:\s+patients)?\s+(?:were\s+(?:measured|profiled|processed|sequenced)\s+)?"
                    r"(?:on|in|using)\s+(platform|batch)\s+([\w-]+)", text, re.I)
                if (len(assignments) == 2 and assignments[0][0].lower() != assignments[1][0].lower()
                        and assignments[0][1].lower() == assignments[1][1].lower()
                        and assignments[0][2].lower() != assignments[1][2].lower()):
                    match = re.search(r".+", text, re.S)
            if match and affirmative(text, *match.span()):
                if (spec.id == "feature_selection_before_split" and
                        re.search(r"\b(?:prespecified|pre.specified|prior literature|external reference)\b", text, re.I)
                        and not re.search(r"\b(?:all samples|all patients|full dataset|entire cohort|response labels|outcome labels)\b", text, re.I)):
                    continue
                hits.append(ev)
        if not hits:
            continue
        status = spec.status
        if spec.id == "feature_selection_before_split" and not any(
                re.search(r"\b(?:all samples|all patients|full dataset|entire cohort|response labels|outcome labels)\b", ev.quote, re.I)
                for ev in hits):
            status = "plausible_issue"
        findings.append(prioritize(Finding(
            id="pattern." + spec.id, rule_id=spec.id, severity=spec.severity,
            category=spec.category, manuscript_section=hits[0].section, claim=hits[0].quote,
            issue=spec.label + ": review the cited passage.",
            why_it_matters=spec.why, evidence=hits[:8], suggested_fix=spec.fix,
            suggested_analysis=spec.analysis,
            confidence="high" if status == "established_issue" else "medium",
            issue_status=status, reviewer_roles=ROLE_MAP[spec.category])))
    return findings, results
