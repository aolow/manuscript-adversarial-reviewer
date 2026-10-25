# Virtual Biotech: trace the claim from association to proposed intervention

## Review at a glance

**Assessment:** The preprint reports computational case studies and observational associations. These generate therapeutic hypotheses; causal mechanisms and treatment-specific benefit remain untested. Trial-level uncertainty requires verification. [VB-1](#vb-1) [VB-2](#vb-2) [VB-3](#vb-3)

**Main contribution:** Documents a reviewer critique followed by a spatial analysis addressing the missing tissue context. [VB-5](#vb-5)

**Review priorities:**

1. Describe B7-H3 findings as spatial and survival associations. A causal mechanism requires intervention evidence. [VB-1](#vb-1)
2. Keep enrollment based on oncostatin M receptor (OSMR) expression as a hypothesis: nonresponse to other therapies does not establish benefit from vixarelimab. [VB-2](#vb-2)
3. Check whether uncertainty accounts for drugs, targets and development programs represented in multiple trials. [VB-3](#vb-3)

**Next step:** Align the claims with the observational evidence, then inspect the trial–drug–target mapping to assess dependence. [VB-1](#vb-1) [VB-3](#vb-3)

*Scope: February 2026 preprint v1, not the later journal article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and data were not inspected; no independent human validation of this review.*

---

> Model-native scientific review with a separately executed offline CLI baseline. No provider panel was run. Not independently human-validated.

Source: [The Virtual Biotech: A Multi-Agent AI Framework for Therapeutic Discovery and Development](https://pmc.ncbi.nlm.nih.gov/articles/PMC12970349/). Harrison G. Zhang, Peter Eckmann, Jiacheng Miao, Andrew B. Mahon, James Zou. bioRxiv preprint v1, 23 February 2026; PMC12970349.1.

This review covers the February 2026 preprint. It identifies three revision priorities, two verification questions, one supported strength and five dismissed concerns. The assessments distinguish the reported computational results from mechanistic, treatment-selection and comparative-quality conclusions.

## Coverage

Read: abstract, main text, Extended Methods, five figure captions and data availability in the 23 February 2026 preprint v1 (PMC12970349.1). The offline CLI produced 30 leads from 150 source blocks. One model-native synthesis followed the MAR evidence-challenge checklist; no provider panel or independent expert assessment was run. Supplementary PDF, figure images, execution logs, source code and raw datasets were not inspected. The September 2026 Science version is outside this review.

All decisions below are model-native interpretations, including the decisions to dismiss a concern. Exact source-span checks do not verify those interpretations. Engine dispositions remain unchanged in [baseline.json](baseline.json).

## Revision priorities

<a id="vb-1"></a>

### VB-1 — B7-H3 association and mechanism

**Decision: retain.** The reported evidence links B7-H3 expression with spatial cell patterns and survival. These observational associations do not establish that changing B7-H3 activity causes or reverses immune exclusion. Describing them as “functional evidence” needs qualification. [VB-A1](#vb-a1)

**Counterevidence / scope:** The methods exclude B7-H3 from cell-abundance estimation and account for spatial composition and sample effects. The discussion also identifies the case studies as hypotheses requiring validation. [VB-A2](#vb-a2) [VB-A3](#vb-a3) [VB-A4](#vb-a4)

**Next step:** Revise the mechanistic wording to reflect observational evidence. If a causal claim is required, propose a new study perturbing B7-H3 in matched fibroblast, immune-cell and tumor systems across independent donors. Compare appropriate controls and measure immune exclusion or function, with viability checks.

**What would change this decision:** Replicated interventions separating B7-H3 activity from correlated fibroblast state would support stronger mechanistic language.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

<a id="vb-2"></a>

### VB-2 — OSMR expression and treatment selection

**Decision: narrow.** Baseline oncostatin M receptor (OSMR) expression is associated with nonresponse to other biologics. This does not establish greater benefit from vixarelimab in a selected subgroup or explain why MOONGLOW stopped. [VB-A5](#vb-a5) [VB-A6](#vb-a6)

**Counterevidence / scope:** The authors use conditional language, describe the case studies as hypotheses and identify unresolved assay and cutoff choices. The review should retain those qualifications. [VB-A4](#vb-a4) [VB-A7](#vb-a7)

**Next step:** Check whether baseline biopsies, randomized treatment assignments and outcomes from MOONGLOW are available. If available, estimate whether treatment effects vary with the biomarker, including uncertainty. An exploratory result would require a prespecified assay and cutoff plus independent prospective evaluation before supporting a validated selection strategy.

**What would change this decision:** Treatment-interaction evidence replicated in an independent cohort could justify predictive language. General association with disease severity or other-therapy nonresponse would not.

**Origin:** model-native. **Related engine leads:** `check.treatment_interaction`, `check.clinical_utility`, `check.clinical_use`.

<a id="vb-4"></a>

### VB-4 — Evidence for comparative review quality

**Decision: narrow.** The case studies, API expenditure and parallel execution demonstrate feasibility. They do not measure improvement over human teams or the contribution of the reviewer agent to scientific accuracy. API expenditure also does not measure total project cost. [VB-A11](#vb-a11) [VB-A12](#vb-a12)

**Counterevidence / scope:** The authors describe an inspectable workflow and acknowledge that agent errors can propagate. These observations do not substitute for a controlled comparison. [VB-A13](#vb-a13) [VB-A14](#vb-a14)

**Next step:** Qualify comparative claims. A validation study could compare the full workflow, a version without the reviewer and a simpler agent on the same unseen questions, information and budget. Blinded experts would assess correct conclusions, unsupported claims and missing evidence; record time and total cost. This study was not performed for the showcase.

**What would change this decision:** A controlled assessment showing repeatable quality gains would support a stronger claim about the reviewer loop. Reported case costs alone would not.

**Origin:** model-native. **Related engine leads:** `check.baseline_models`.

## Open verification questions

<a id="vb-3"></a>

### VB-3 — Dependence across trials

**Decision: verify.** Related trials can share drugs, targets and molecular features. The reported modality and disease-area random effects do not establish that this dependence is accounted for, and shuffling individual outcomes may not preserve it. The effect on uncertainty remains unverified. [VB-A8](#vb-a8) [VB-A10](#vb-a10)

**Counterevidence / scope:** The paper reports adjusted mixed models, adjustment for genetic evidence, correction for multiple comparisons and an observational limitation. These address other sources of bias and uncertainty. [VB-A9](#vb-a9) [VB-A26](#vb-a26)

**Next step:** Inspect the trial–drug–target mapping and scripts; count independent groups and their overlap. If dependence remains, compare uncertainty using a variance model or resampling scheme that accounts for shared drugs, programs or targets, including drugs with multiple targets. Claims about future prediction also need evaluation on later trials and unseen groups. The required mapping and code were not audited.

**What would change this decision:** Existing adequate dependence handling in code, or stable effect sizes and uncertainty under the appropriate grouped analysis, would close or narrow this concern.

**Origin:** model-native. **Related engine leads:** `check.external_validation`, `check.train_test_split`.

<a id="vb-9"></a>

### VB-9 — Reproducibility and annotation uncertainty

**Decision: verify.** The paper describes downloadable code and reports, plus human annotation checks. This review did not execute a pinned release or inspect the full supplementary protocol. Agreement on the checked subset does not establish accuracy across all annotations or quantify the effect of remaining errors. [VB-A20](#vb-a20) [VB-A21](#vb-a21) [VB-A22](#vb-a22)

**Counterevidence / scope:** The article reports two human annotators and a comparison with the Therapeutic Data Commons (TDC) dataset. Human validation is present; its coverage and the effect of annotation errors require assessment. [VB-A21](#vb-a21)

**Next step:** Locate the exact code and data release and supplementary annotation rules. Check missing data, disagreement patterns, random seeds, assay and threshold sensitivity, and tool versions. Test whether plausible annotation errors change key results. Treat uninspected details as open checks.

**What would change this decision:** A reproducible release plus an adequate error/missingness sensitivity analysis could close these checks. A confirmed execution or annotation failure would justify a narrower issue.

**Origin:** model-native. **Related engine leads:** `check.code_availability`, `check.missingness`.

## Supported strengths

<a id="vb-5"></a>

### VB-5 — Reviewer feedback leads to a follow-up analysis

**Decision: strength.** The reviewer identifies missing spatial context, and the workflow follows with a spatial analysis. This documents a specific link between a criticism and an analysis addressing it. [VB-A14](#vb-a14) [VB-A15](#vb-a15)

**Counterevidence / scope:** The case studies remain observational hypotheses requiring validation. The example does not measure improvement in review accuracy. [VB-A4](#vb-a4)

**Next step:** Retain this example as a rationale for linking each MAR concern to a specific next check. Evaluate its effect on review quality in a future blinded comparison.

**What would change this decision:** If logs showed that the follow-up was unrelated to the critique, the claimed workflow example would weaken; execution logs were not audited.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Dismissed concerns

<a id="vb-6"></a>

### VB-6 — Donor and sample effects are reported

**Decision: dismiss.** The methods aggregate counts by donor and cell type and include patient effects for longitudinal ulcerative colitis data. The generic contradiction combines different analyses; the evidence does not support a blanket concern about absent donor control. [VB-A16](#vb-a16) [VB-A17](#vb-a17)

**Counterevidence / scope:** A sample intercept is also reported for spatial data. Trial reuse and correlation within a slide remain distinct questions. [VB-A3](#vb-a3)

**Next step:** Close the generic contradiction. Inspect a specific model and its independent biological unit before raising a dependence concern.

**What would change this decision:** A mismatch between the described and executed analysis could justify a specific issue.

**Origin:** model-native. **Related engine leads:** `check.pseudobulk`.

<a id="vb-7"></a>

### VB-7 — “First trained” describes analysis order

**Decision: dismiss.** The engine matched “first” in a methods description of model fitting. It refers to the order of analysis steps, not a claim of scientific priority. [VB-A18](#vb-a18)

**Counterevidence / scope:** The surrounding paragraph describes reference fitting followed by spatial mapping; there is no novelty assertion in this evidence span. [VB-A2](#vb-a2)

**Next step:** Discard this particular novelty lead. Any actual priority or originality claim needs a separate literature check.

**What would change this decision:** A different passage making an explicit first-ever claim would need its own evidence and review.

**Origin:** model-native. **Related engine leads:** `pattern.novelty_overclaim`.

<a id="vb-8"></a>

### VB-8 — Reported thresholds and endpoints

**Decision: dismiss.** The paper reports a cell-type specificity (tau) threshold and spatial quartiles within samples. Endpoint failures and successes refer to different trials. The proposed OSMR enrollment cutoff is a separate, unresolved choice. [VB-A19](#vb-a19) [VB-A25](#vb-a25) [VB-A24](#vb-a24)

**Counterevidence / scope:** A reported threshold does not establish robustness to its choice. Trials with multiple treatment groups may also require further annotation checks. [VB-A7](#vb-a7)

**Next step:** Close the generic missing-cutoff and contradictory-endpoint leads. Tie any sensitivity or annotation question to the analysis it could affect.

**What would change this decision:** An inconsistent definition for the same outcome or an unreported threshold used in a main analysis would reopen a specific reporting concern.

**Origin:** model-native. **Related engine leads:** `check.cutoff`, `check.endpoint`.

<a id="vb-10"></a>

### VB-10 — Original-screen checks do not apply to reused data

**Decision: dismiss.** The workflow reuses Tahoe perturbation profiles. This does not establish that the study performed a new pooled screen, so screen-specific control requirements cannot be inferred from those terms alone. [VB-A23](#vb-a23)

**Counterevidence / scope:** Dataset provenance and the validity of the reused signatures remain relevant, but must be checked against the original data and the actual analysis. [VB-A23](#vb-a23)

**Next step:** Mark original-screen reporting leads out of scope; route provenance checks to the source dataset and released analysis.

**What would change this decision:** If a new original screen were supplied, the corresponding experimental controls would become applicable.

**Origin:** model-native. **Related engine leads:** `check.guides`, `check.moi`.

<a id="vb-11"></a>

### VB-11 — Batch handling is described

**Decision: dismiss.** The manuscript describes Harmony preprocessing. This answers the generic reporting concern about absent batch handling; whether the correction is adequate requires the data and study design. [VB-A27](#vb-a27)

**Counterevidence / scope:** The authors acknowledge residual confounding in the observational trial analysis. Naming a correction method does not establish that all relevant confounding is removed. [VB-A26](#vb-a26)

**Next step:** Close the reporting-absence lead. Assess any remaining confounding against a specific comparison and conclusion.

**What would change this decision:** Evidence that a relevant cohort/platform effect is inseparable from the biological contrast would justify a focused concern.

**Origin:** model-native. **Related engine leads:** `check.batch_platform`.

## Complete disposition of the offline leads

This is an annotated demonstration, not a measured false-positive rate. The following groups cover every engine lead exactly once; these are recommendations, not overrides of the original report.

- **Contextual false positive:** The novelty detector matched temporal sequencing in the methods. Related review: VB-7. Leads: `pattern.novelty_overclaim`.

- **Already reported; do not conflate analyses:** Donor aggregation, threshold selection, endpoint context and batch handling are described. Related review: VB-6, VB-8, VB-11. Leads: `check.pseudobulk`, `check.cutoff`, `check.endpoint`, `check.batch_platform`.

- **Narrowed to a specific inference boundary:** Keep clinical-benefit and architectural-comparison claims proportional to the evidence. Related review: VB-2, VB-4. Leads: `check.treatment_interaction`, `check.clinical_utility`, `check.clinical_use`, `check.baseline_models`.

- **Verify the relevant unit and generalization target:** These are observational associations; inspect shared targets/programs before assuming independent trial evidence or prospective performance. Related review: VB-3. Leads: `check.external_validation`, `check.train_test_split`.

- **Out of scope:** No original pooled perturbation screen or deployed diagnostic classifier is reported. Related review: VB-10, VB-2. Leads: `check.guides`, `check.perturbation_efficiency`, `check.screen_controls`, `check.moi`, `check.perturbation_model`, `check.screen_quality`, `check.calibration`, `check.metric_context`, `check.prevalence_shift`.

- **Verify in unreviewed materials or establish applicability:** Inspect the release, supplement and actual model before elevating these broad reporting cues to findings. Related review: VB-9. Leads: `check.code_availability`, `check.ambient_rna`, `check.annotation_robustness`, `check.cluster_stability`, `check.doublets`, `check.integration`, `check.missingness`, `check.random_seed`, `check.subgroups`, `check.thresholds`.

## Evidence ledger

Short excerpts are attributed to the article above. Source IDs refer to the pinned JATS snapshot; `node-*` IDs are assigned by the converter. [review.json](review.json) retains MAR block IDs and exact character offsets. Reproduction downloads the full context locally for inspection.

### VB-A1

Source `P38`: “providing functional evidence supporting B7-H3 as an checkpoint target in lung cancer”

### VB-A2

Source `P90`: “We excluded the gene of interest (B7-H3) from this workflow to avoid circularity”

### VB-A3

Source `P91`: “a sample-level random intercept to account for slide-to-slide variation”

### VB-A4

Source `P56`: “the Virtual Biotech generated data-driven hypotheses, which must be tested and further validated”

### VB-A5

Source `P48`: “vixarelimab may be particularly effective in targeting”

### VB-A6

Source `P46`: “across all five trials spanning three therapeutic mechanisms”

### VB-A7

Source `P49`: “defining clinically meaningful OSMR expression cutoff levels”

### VB-A8

Source `P79`: “Clinical trial outcomes (phase progression, trial termination, endpoint success) were analyzed with univariate logistic regression”

### VB-A9

Source `P81`: “crossed random intercepts for drug-type combination and therapeutic area combination”

### VB-A10

Source `P80`: “the outcome vector was randomly shuffled while retaining the original feature values”

### VB-A11

Source `P52`: “recommendations unbiased by sociological influences”

### VB-A12

Source `P53`: “took less than one day and cost $46.00 in API fees”

### VB-A13

Source `P55`: “a single mistake can propagate through the virtual organization”

### VB-A14

Source `P17`: “If gaps or unsubstantiated claims are identified by the scientific reviewer agent”

### VB-A15

Source `P38`: “but this was inferred from dissociated single-cell data that inherently lose spatial tissue context”

### VB-A16

Source `P88`: “Raw counts were aggregated by donor and cell type”

### VB-A17

Source `P93`: “each patient was modeled with random effects”

### VB-A18

Source `P90`: “the workflow first trained a negative binomial regression model”

### VB-A19

Source `P84`: “setting the threshold at the midpoint of the two cluster centers (τ = 0.69)”

### VB-A20

Source `P22`: “Agreement between human reviewer and the agent was 89.7% (78/87)”

### VB-A21

Source `P74`: “50 randomly sampled from all Phase II trials, and 50 from all Phase III”

### VB-A22

Source `P18`: “allows users to download the corresponding data, reproducible code, and reports”

### VB-A23

Source `P70`: “Pseudobulked differential expression profiles were procured from Tahoe-100M”

### VB-A24

Source `P23`: “studies with multiple experimental arms in which some arms achieved the primary endpoint while others did not”

### VB-A25

Source `P91`: “top quartile”

### VB-A26

Source `P56`: “our trial analyses are observational and should be interpreted as such”

### VB-A27

Source `P87`: “Batch effects were corrected using Harmony”
