"""Claim-centered synthesis shared by deterministic and opt-in provider runs."""
from dataclasses import asdict

from .grounding import words
from .models import stable_id


def action_template(finding):
    """Conditional plans, never a claim that an analysis has already been run."""
    action = dict(kind="analysis", input=None, comparison=None, held_out_unit=None,
                  metric=None, expected_interpretation=None, text_section=None,
                  text_claim=None, recommended_framing=None)
    if finding.category == "leakage":
        action.update(input="Original predictor inputs and participant/cohort labels",
                      comparison="Reported pipeline versus all learned steps refit inside nested training folds",
                      held_out_unit="Patients or donors, grouped by cohort where relevant",
                      metric="Held-out discrimination and calibration with biological-unit confidence intervals",
                      expected_interpretation="A material loss of performance would weaken the claimed generalization; stability would address this specific concern.")
    elif finding.category == "single_cell":
        action.update(input="Cell-level measurements with donor, condition, and batch labels",
                      comparison="Original cell-level result versus a justified donor-aware model or pseudobulk analysis",
                      held_out_unit="Independent donors; preserve within-donor dependence",
                      metric="Donor-level effect estimates, uncertainty, multiplicity-adjusted evidence, and sensitivity to cell counts",
                      expected_interpretation="A disappearing or reversed donor-level effect would undermine the pooled-cell conclusion.")
    elif finding.category == "circularity":
        action.update(input="Construction features, validation features, independent phenotypes, and cohort membership",
                      comparison="Reported validation versus validation excluding construction/annotation information",
                      held_out_unit="Independent cohort and independent validation features",
                      metric="Prespecified association or predictive performance under an appropriate null",
                      expected_interpretation="Loss of support when defining information is withheld would indicate circular validation.")
    elif finding.category == "confounding":
        action.update(input="Condition-by-donor, cohort, batch, and platform assignments",
                      comparison="Original contrast versus within-stratum contrasts with genuine overlap or a balanced external cohort",
                      held_out_unit="Independent biological units within comparable technical strata",
                      metric="Contrast estimates and uncertainty by stratum, plus overlap/identifiability diagnostics",
                      expected_interpretation="No within-stratum overlap means adjustment cannot separately identify the effects; reversal across strata weakens the biological explanation.")
    elif finding.category in ("interpretation", "positioning", "writing"):
        action.update(kind="text", text_section=finding.manuscript_section, text_claim=finding.claim,
                      recommended_framing=finding.suggested_fix)
    else:
        action.update(kind="reporting", input=finding.suggested_fix,
                      expected_interpretation="First establish the actual method and applicability, then assess whether the proposed analysis is required.")
    return action


def central_claims(review):
    supplied = [claim for run in review.reviewer_runs for claim in run.get("claim_analyses", [])]
    selected = {}
    for claim in sorted(supplied, key=lambda c: (c["reviewer_role"] != "scientific", c["rank"])):
        selected.setdefault(claim["id"], claim)
    if selected:
        ordered = sorted(selected.values(), key=lambda c: ({"central": 0, "supporting": 1, "exploratory": 2}[c["importance"]], c["rank"]))
        return [{**claim, "reviewer_rank": claim["rank"], "rank": rank}
                for rank, claim in enumerate(ordered, 1)]
    candidates = sorted(review.extraction["claims"],
                        key=lambda c: (not c["section"].startswith(("Abstract", "Conclusion")), len(c["text"])))
    links = {row["claim_id"]: row for row in review.extraction["claim_evidence_map"]}
    result, texts = [], set()
    for candidate in candidates:
        if candidate["text"] in texts:
            continue
        texts.add(candidate["text"])
        linked = [f for f in review.findings if f.disposition in ("active", "confirmed")
                  and len(words(f.claim + " " + f.issue) & words(candidate["text"])) >= 3]
        linked.sort(key=lambda f: f.priority)
        strongest = linked[0] if linked else None
        result.append({
            "id": candidate["id"], "claim_text": candidate["text"],
            "importance": "central" if candidate["section"].startswith(("Abstract", "Conclusion")) else "supporting",
            "importance_rationale": "Heuristic based on source section; scientific importance is not independently established.",
            "rank": len(result) + 1, "manuscript_evidence": [candidate["evidence"]],
            "supporting_evidence": links[candidate["id"]]["candidate_evidence"],
            "strongest_support": "Candidate reference-linked passages only; strongest scientific support is not established.",
            "strongest_weakness": strongest.issue if strongest else "Not established by deterministic analysis.",
            "alternative_explanation": (strongest.why_it_matters if strongest else
                                        "A specific alternative requires scientific review."),
            "falsification_analysis": action_template(strongest) if strongest else {},
            "decisive_analysis": action_template(strongest) if strongest else {},
            "impact_if_false": "Reassess the central interpretation and contribution if this claim fails.",
            "confidence_in_claim": "low", "origin": "deterministic",
            "reviewer_role": "heuristic", "quality_flags": ["scientific_judgment_not_performed"],
        })
        if len(result) >= 12:
            break
    return result


def build_adversarial(review):
    review.claim_analyses = central_claims(review)
    central_ids = {c["id"] for c in review.claim_analyses if c["importance"] == "central"}
    canonical_by_text = {c["claim_text"]: c["id"] for c in review.claim_analyses}
    claim_aliases = {c["id"]: canonical_by_text.get(c["text"], c["id"]) for c in review.extraction["claims"]}
    for finding in review.findings:
        finding.claim_ids = [claim_aliases.get(identifier, identifier) for identifier in finding.claim_ids]
        if not finding.action:
            finding.action = action_template(finding)
        if not finding.topic:
            finding.topic = {"single_cell": "pseudoreplication", "interpretation": "causality",
                             "positioning": "novelty"}.get(finding.category, finding.category)
        if finding.id.startswith("check."):
            finding.basis = "manuscript_inference"
        # Explicit model links are preferred; these heuristic links are labeled.
        if not finding.claim_ids:
            finding.claim_ids = [c["id"] for c in review.claim_analyses
                                 if len(words(c["claim_text"]) & words(finding.claim + " " + finding.issue)) >= 3][:3]
            if finding.claim_ids:
                finding.quality_flags = sorted(set(finding.quality_flags + ["claim_link_is_heuristic"]))
    active = [f for f in review.findings if f.disposition in ("active", "confirmed")]
    substantive = [f for f in active if f.severity in ("fatal_flaw", "major")
                   and f.category not in ("reporting", "reproducibility")
                   and f.basis not in ("external_claim", "reviewer_opinion")
                   and f.grounding_status == "source_verified"]
    substantive.sort(key=lambda f: (not bool(set(f.claim_ids) & central_ids),
                                    f.id.startswith("check."), f.priority, f.id))
    top = substantive[:7]
    strengths = [s for run in review.reviewer_runs for s in run.get("strengths", [])
                 if s.get("grounding_status", "source_verified") == "source_verified"]
    if not strengths:
        strengths = [{"text": "Reported design element; scientific adequacy requires review: " + c.label,
                      "evidence": [asdict(e) for e in c.evidence], "interpretation_status": "reported_cue_only"}
                     for c in review.checklist if c.status == "reported" and c.id in
                     ("external_validation", "biological_replicates", "confidence_intervals", "baseline_models", "pseudobulk")][:5]
    return {
        "what_could_kill_this_paper": {
            "finding_ids": [f.id for f in top],
            "note": "Up to seven consequential review leads, not fatal-flaw verdicts. Fewer than three are shown when fewer are justified.",
        },
        "major_strengths": strengths,
        "central_claim_ids": [c["id"] for c in review.claim_analyses if c["importance"] == "central"],
        "high_priority_analyses": [f.id for f in top if f.action.get("kind") in ("analysis", "experiment")],
        "secondary_analyses": [f.id for f in active if f not in top and f.action.get("kind") in ("analysis", "experiment")],
        "writing_framing": [f.id for f in active if f.action.get("kind") == "text"],
        "novelty_positioning": [f.id for f in review.findings if f.category == "positioning" and f.disposition != "duplicate"],
        "reproducibility_gaps": [f.id for f in active if f.category == "reproducibility"],
        "lower_priority_reporting": [f.id for f in active if f.id.startswith("check.") and f not in top],
        "requires_human_review": [f.id for f in review.findings if f.disposition == "needs_review"],
    }
