# Review rubric

The rubric separates severity, confidence, evidence quality, and priority. These are related, but they are not interchangeable.

## Severity

| Severity | Meaning |
| --- | --- |
| Fatal flaw | Human-adjudicated defect that prevents the principal inference |
| Major | Could materially change a central conclusion or its validity |
| Moderate | Meaningful robustness, interpretation, or reporting concern |
| Minor | Local clarity or reproducibility issue |
| Optional strengthening | Useful improvement that is not required for the main inference |

The deterministic engine and LLM providers do not automatically declare a fatal flaw.

## Issue status

| Status | Meaning |
| --- | --- |
| Established issue | Narrow deterministic pattern with explicit supporting text |
| Plausible issue | Credible concern that still needs scientific verification |
| Speculative concern | Hypothesis or question that should not be asserted as fact |

A valid source quote does not prove that the reviewer's interpretation is correct.

## Priority

| Tier | Meaning |
| --- | --- |
| P0 | Verify before submission |
| P1 | High-value revision |
| P2 | Targeted clarification |
| P3 | Optional strengthening |

Priority also considers likely impact, effort, and reviewer salience. Suggested analyses are proposals, not automatic requirements.

## Reviewer roles

| Role | Focus |
| --- | --- |
| Scientific | Biology, alternatives, causal interpretation, generalizability |
| Methods | Design, cohorts, controls, preprocessing, replication |
| Computational | Leakage, representations, pipelines, baselines, ablations |
| Novelty | Contribution framing and literature comparisons that still need external verification |
| Reviewer 2 | Pointed attempts to falsify consequential claims |
| Reproducibility | Parameters, software, cohort definitions, seeds, manual steps |
| Statistics | Estimands, uncertainty, multiplicity, dependence |
| Clinical | Intended use, endpoints, prediction, transportability, utility |
| Editor | Significance, maturity, audience, journal positioning |
| Strategist | Revision dependencies, effort, value, and ordering |

The default LLM run uses scientific, methods, computational, novelty, Reviewer 2, and reproducibility.

## Headline concerns

The revision brief shows at most seven consequential concerns and does not pad the list.

Ungrounded, duplicate, external-only, or quarantined findings do not enter the headline set.

Agreement across multiple model roles is not treated as independent scientific confirmation.

## Provider evidence handling

Provider output has to pass the response schema before any scientific grounding occurs. That schema gate is currently atomic, so one malformed required field or invalid ID can reject the entire role.

After schema acceptance, grounding is intentionally more granular:

- Invalid claim evidence drops that claim without erasing unrelated findings.
- Invalid finding citations are removed individually; an all-invalid cited finding is dropped.
- Finding links to rejected or unknown claims are removed instead of aborting the finding.
- Invalid or empty strengths are skipped individually and do not offset, rescue, or erase findings.

A grounded strength is still reviewer judgment, not proof that the corresponding design or conclusion is strong.

## Coverage

The deterministic layer has explicit checks for selected problems including:

- Train/test leakage and cohort reuse.
- Cell-level pseudoreplication.
- Circular feature or signature validation.
- Strong causal or mechanistic claims.
- Missing uncertainty, calibration, baselines, multiplicity, or null procedures.
- Batch, platform, and cancer-type confounding cues.
- Selected single-cell, perturbation-screen, biomarker, novelty, and reproducibility reporting.

These checks are intentionally incomplete. Complex wording, study-specific design, biological context, and statistical validity still require expert judgment.

## False-positive precautions

The rule engine tries to distinguish:

- Prior work from the current study.
- Hypothetical or planned work from completed work.
- Explicit negative QC results from missing QC.
- Internal held-out validation from external validation.
- Prespecified literature features from data-driven leakage.

These protections reduce obvious false positives, but they are not semantic understanding.

Verify consequential findings against the manuscript and underlying analysis before acting on them.
