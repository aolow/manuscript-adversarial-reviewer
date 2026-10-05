# Review rubric

## Severity and epistemic status

| Severity | Meaning |
| --- | --- |
| Fatal flaw | Human-adjudicated defect that prevents the principal inference |
| Major | Could materially change a central conclusion or its validity |
| Moderate | Meaningful robustness, interpretation, or reporting concern |
| Minor | Local clarity or reproducibility issue |
| Optional strengthening | Potential benefit depending on study scope |

No rule or provider automatically assigns a fatal flaw. Established issues are
narrow, explicit descriptions of a concerning design. Plausible issues need
verification. Speculative concerns are hypotheses. Missing reporting is treated
cautiously. A provider cannot create an established issue without human review.

## Prioritization

| Tier | Decision rule |
| --- | --- |
| P0: verify before submission | Fatal, or explicit major leakage/circularity/pseudoreplication concern |
| P1: high-value revision | Major, or moderate with high value, high notice likelihood, and low effort |
| P2: targeted clarification | Remaining reporting/analysis clarification |
| P3: optional strengthening | Optional severity or speculative status |

Effort/value and reviewer likelihood are editable judgments, not probabilities.
Reanalysis may be unnecessary when a clarification establishes the actual design.
Do not demand every suggested analysis automatically.

## Reviewer mandates

| Role | Focus |
| --- | --- |
| Scientific | Biology, alternatives, perturbations, causal/mechanistic interpretation |
| Methods | Design, cohorts, preprocessing, leakage, replication, reproducibility |
| Statistics | Estimands, dependence, uncertainty, multiplicity, evaluation assumptions |
| Clinical | Use, endpoints, prognostic/predictive distinction, transportability, utility |
| Reviewer 2 | Pointed stress tests of consequential weak links |
| Novelty | Scoped contribution and literature comparisons |
| Editor | Audience, significance, maturity, and bounded journal-fit triage |
| Strategist | Dependencies, essential fixes, effort/value, conditional text edits |

Offline reviewer runs route findings, not independent LLM judgments.
Opt-in LLM review defaults to scientific, combined methods/statistics,
computational, novelty, Reviewer 2, and reproducibility. The existing statistics,
clinical, editor, and strategist mandates can also be selected.

Headline selection considers central-claim links and substantive severity before
checklist omissions, and shows at most seven issues without padding. Ungrounded,
external, duplicate, and quarantined findings do not enter that list.
Duplicate reviewers are not independent scientific confirmation: originals are
preserved, severity disagreements are exposed, and the less severe rating is used
pending human adjudication.

For provider output, high subjective confidence is capped at medium until human
review. An exact excerpt certifies source authenticity, not interpretation.
Unsupported locations and quotations reject the response; shallow support flags
require review rather than asserting semantic truth.

## Coverage and limits

| Topic | Offline behavior | Judgment still needed |
| --- | --- | --- |
| Split leakage, test tuning, cohort reuse | Explicit patterns; split/grouping/external-validation cues | All fitted steps, label/reference leakage, true independence |
| Cell pseudoreplication | Cell-as-independent pattern; donor/pseudobulk cues | Appropriate model and true biological units |
| Circular feature/signature validation | Same-gene construction/validation pattern | Annotation/gene-set overlap, independent endpoints |
| Causality/conservation | Strong causal, mechanistic, transfer/similarity wording | Identification, perturbation/rescue evidence |
| AUROC/AUPRC, intervals, calibration, baselines | Reporting cues | Metric/interval validity and incremental value |
| Multiplicity, nulls, permutations | Reporting cues | Hypothesis families, exchangeability, permutation power |
| Batch/platform/cancer confounding | Cues and alternative-explanation questions | Identifiability, cross-tabs, adjustment, remaining bias |
| Single-cell robustness | Donor/cell balance, clusters, annotations, doublets, ambient RNA, integration, composition, thresholds | QC adequacy, artifacts, annotation circularity, abundance validity |
| Perturbation screens | Efficiency, guides, MOI, toxicity, off-targets, controls, QC, modality/model cues | Essential-gene effects, control/replicate quality, MAGeCK/modality assumptions |
| Biomarkers | Use, endpoint, ascertainment, shift, cutoff, interaction, subgroups, missingness, censoring, utility | Clinical validity, utility, endpoint quality, survival assumptions |
| Novelty | Absolute novelty wording | Current literature and comparators |
| Reproducibility | Seeds, software, code/data cues | Accessible artifacts and reproducible results |

All requested topics have either an offline cue or an explicit reviewer mandate.
Mention is not adequacy. Rightmost-column judgments are **not solved by the
current offline tool**.

## False-positive precautions

Exclude references. Guard prior-work, hypothetical, planned, and negated
statements where recognized. Scope negation to semicolons and contrasts.
Distinguish negative QC outcomes from unperformed QC. Do not count internal
held-out data as external validation. Do not call prespecified literature
features leakage solely because they precede the split. Preserve conflicting
descriptions.

Complex language can defeat these shallow heuristics in either direction.
Verify consequential concerns and use version-bound overrides when needed.
