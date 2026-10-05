> Synthetic fixture output. No real scientific results. Example metadata is fixed for reproducibility.

# Manuscript adversarial review

**Run:** example-flawed-v0.3.0  
**Schema:** 1.1.0  
**Mode:** offline deterministic audit

This report supports scientific judgment. Findings are traceable review leads; missing reporting is not proof of missing work.

## Revision brief

**What the paper is trying to claim**

- Our results prove a causal mechanism of treatment resistance across tissues. (claim-009b7a26360c)
- We present the first-ever framework for a universal cancer response biomarker. (claim-ecca1ed06169)
- Transcriptomic similarity establishes mechanistic conservation across cancers. (claim-659f836b89a9)

**Contribution if the claims survive:** predictive or biomarker contribution, methodological contribution, biological interpretation — inferred from claim wording; novelty and impact remain unverified.

## What could kill this paper

Up to seven consequential review leads, not fatal-flaw verdicts. Fewer than three are shown when fewer are justified.

- **[pattern.causal_overclaim](#patterncausal_overclaim)** — Causal or mechanistic wording needs support: review the cited passage.
  - Why central: A strong causal phrase requires a design that identifies the claimed mechanism or causal effect.
  - major; plausible_issue; confidence: medium
- **[pattern.conservation_overclaim](#patternconservation_overclaim)** — Similarity or transferability used to claim conservation: review the cited passage.
  - Why central: Transcriptomic similarity or transfer alone does not establish a conserved regulatory mechanism.
  - major; plausible_issue; confidence: medium
- **[pattern.cell_pseudoreplication](#patterncell_pseudoreplication)** — Cells treated as independent biological replicates: review the cited passage.
  - Why central: Within-donor dependence can understate uncertainty when cells replace donors as independent units.
  - major; established_issue; confidence: high
- **[pattern.cohort_reuse](#patterncohort_reuse)** — Discovery and validation cohort reuse: review the cited passage.
  - Why central: Reuse does not establish independent validation and can repeat discovery biases.
  - major; established_issue; confidence: high
- **[pattern.feature_selection_before_split](#patternfeature_selection_before_split)** — Feature selection before splitting: review the cited passage.
  - Why central: Data-dependent selection using evaluation samples makes the reported evaluation non-independent.
  - major; established_issue; confidence: high
- **[pattern.test_set_tuning](#patterntest_set_tuning)** — Test data used for tuning: review the cited passage.
  - Why central: Choosing model settings on a test set turns it into development data.
  - major; established_issue; confidence: high
- **[pattern.circular_signature](#patterncircular_signature)** — Signature reused for its own validation: review the cited passage.
  - Why central: Reusing defining features as evidence of validity may produce a tautological result.
  - major; plausible_issue; confidence: medium

## Major strengths

- Reported design element; scientific adequacy requires review: Biological replication units (reported_cue_only)
  - manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1

## Analyses most likely to change the story

- **pattern.cell_pseudoreplication**: Report donor nesting and justify the model; distinguish technical observations from biological replicates.
  - **Input:** Cell-level measurements with donor, condition, and batch labels
  - **Comparison:** Original cell-level result versus a justified donor-aware model or pseudobulk analysis
  - **Held-out / biological unit:** Independent donors; preserve within-donor dependence
  - **Metric:** Donor-level effect estimates, uncertainty, multiplicity-adjusted evidence, and sensitivity to cell counts
  - **Interpretation / failure criterion:** A disappearing or reversed donor-level effect would undermine the pooled-cell conclusion.
- **pattern.cohort_reuse**: Label the analysis as internal reuse and identify independent validation if it exists.
  - **Input:** Construction features, validation features, independent phenotypes, and cohort membership
  - **Comparison:** Reported validation versus validation excluding construction/annotation information
  - **Held-out / biological unit:** Independent cohort and independent validation features
  - **Metric:** Prespecified association or predictive performance under an appropriate null
  - **Interpretation / failure criterion:** Loss of support when defining information is withheld would indicate circular validation.
- **pattern.feature_selection_before_split**: Clarify whether selection used outcomes and evaluation samples; fit all learned selection inside training folds.
  - **Input:** Original predictor inputs and participant/cohort labels
  - **Comparison:** Reported pipeline versus all learned steps refit inside nested training folds
  - **Held-out / biological unit:** Patients or donors, grouped by cohort where relevant
  - **Metric:** Held-out discrimination and calibration with biological-unit confidence intervals
  - **Interpretation / failure criterion:** A material loss of performance would weaken the claimed generalization; stability would address this specific concern.

## Text and positioning changes

These address wording; they do not repair an unsupported experiment or design.

- **Abstract**: Connect the wording to identifying evidence; if support is associative, use appropriately limited language. (pattern.causal_overclaim)
- **Abstract**: Separate shared predictive structure from evidence of shared regulation. (pattern.conservation_overclaim)
- **Methods**: Explain design, measurement, cohort, and inference limitations in relation to the main claims. (check.limitations)

## Likely Reviewer 2 attacks

- Causal or mechanistic wording needs support: review the cited passage. — Evaluate perturbation, rescue, temporal ordering, and alternative causal explanations as appropriate.
- Similarity or transferability used to claim conservation: review the cited passage. — Test specific regulatory predictions with orthogonal perturbations across the relevant tissues or cohorts.
- Cells treated as independent biological replicates: review the cited passage. — Reanalyze using donor-level pseudobulk or an appropriate hierarchical model.

<details>
<summary>Full claim analyses and revision plan</summary>

## Central claims and evidence

### Claim 1: central

Our results prove a causal mechanism of treatment resistance across tissues.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Causal or mechanistic wording needs support: review the cited passage.
- Alternative explanation: A strong causal phrase requires a design that identifies the claimed mechanism or causal effect.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1; excerpt: Our results prove a causal mechanism of treatment resistance across tissues.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

**Proposed framing change:**

- **Section:** Abstract
- **Claim to revise:** Our results prove a causal mechanism of treatment resistance across tissues.
- **Framing:** Connect the wording to identifying evidence; if support is associative, use appropriately limited language.

### Claim 2: central

We present the first-ever framework for a universal cancer response biomarker.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Absolute novelty claim: review the cited passage.
- Alternative explanation: Absolute novelty requires a scoped and current literature comparison, which this offline tool cannot verify.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1; excerpt: We present the first-ever framework for a universal cancer response biomarker.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

**Proposed framing change:**

- **Section:** Abstract
- **Claim to revise:** We present the first-ever framework for a universal cancer response biomarker.
- **Framing:** Scope the novelty to a specific contribution and substantiate it with a literature comparison.

### Claim 3: central

Transcriptomic similarity establishes mechanistic conservation across cancers.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Similarity or transferability used to claim conservation: review the cited passage.
- Alternative explanation: Transcriptomic similarity or transfer alone does not establish a conserved regulatory mechanism.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1; excerpt: Transcriptomic similarity establishes mechanistic conservation across cancers.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

**Proposed framing change:**

- **Section:** Abstract
- **Claim to revise:** Transcriptomic similarity establishes mechanistic conservation across cancers.
- **Framing:** Separate shared predictive structure from evidence of shared regulation.

### Claim 4: supporting

Our biomarker predicts treatment response and survival.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Not established by deterministic analysis.
- Alternative explanation: A specific alternative requires scientific review.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Introduction; line 12; block manuscript-5f53f81c8c24-1; excerpt: Our biomarker predicts treatment response and survival.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

### Claim 5: supporting

Our model predicts response with AUROC 0.98 (Figure 1).

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Not established by deterministic analysis.
- Alternative explanation: A specific alternative requires scientific review.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1; excerpt: Our model predicts response with AUROC 0.98 (Figure 1).
- Source: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1; excerpt: Our model predicts response with AUROC 0.98 (Figure 1).
The signature separates responders from nonresponders with p-value 0.001 (Table 1).
Our results prove a causal mechanism of resistance based on the observational association.
- Source: manuscript; Figure Legends; line 36; block manuscript-cf5cfe3b844a-1; excerpt: Figure 1. ROC curve computed from the test set.
Table 1. Cell-level comparisons of signature scores.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

### Claim 6: supporting

The embedding establishes a mechanistic axis linking every tissue.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Not established by deterministic analysis.
- Alternative explanation: A specific alternative requires scientific review.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Discussion; line 42; block manuscript-90a0443af449-1; excerpt: The embedding establishes a mechanistic axis linking every tissue.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

### Claim 7: supporting

We develop a single-cell predictor of clinical response using an observational cohort.

- Importance: Heuristic based on source section; scientific importance is not independently established.
- Strongest reported support: Candidate reference-linked passages only; strongest scientific support is not established.
- Strongest weakness: Not established by deterministic analysis.
- Alternative explanation: A specific alternative requires scientific review.
- Impact if false: Reassess the central interpretation and contribution if this claim fails.
- Confidence in claim: low (deterministic)
- Source: manuscript; Introduction; line 11; block manuscript-5f53f81c8c24-1; excerpt: We develop a single-cell predictor of clinical response using an observational cohort.

**Falsification test:** Not specified by this review.

**Proposed decisive analysis:** Not specified by this review.

## High-priority analyses

- **pattern.cell_pseudoreplication**: Report donor nesting and justify the model; distinguish technical observations from biological replicates.
  - **Input:** Cell-level measurements with donor, condition, and batch labels
  - **Comparison:** Original cell-level result versus a justified donor-aware model or pseudobulk analysis
  - **Held-out / biological unit:** Independent donors; preserve within-donor dependence
  - **Metric:** Donor-level effect estimates, uncertainty, multiplicity-adjusted evidence, and sensitivity to cell counts
  - **Interpretation / failure criterion:** A disappearing or reversed donor-level effect would undermine the pooled-cell conclusion.
- **pattern.cohort_reuse**: Label the analysis as internal reuse and identify independent validation if it exists.
  - **Input:** Construction features, validation features, independent phenotypes, and cohort membership
  - **Comparison:** Reported validation versus validation excluding construction/annotation information
  - **Held-out / biological unit:** Independent cohort and independent validation features
  - **Metric:** Prespecified association or predictive performance under an appropriate null
  - **Interpretation / failure criterion:** Loss of support when defining information is withheld would indicate circular validation.
- **pattern.feature_selection_before_split**: Clarify whether selection used outcomes and evaluation samples; fit all learned selection inside training folds.
  - **Input:** Original predictor inputs and participant/cohort labels
  - **Comparison:** Reported pipeline versus all learned steps refit inside nested training folds
  - **Held-out / biological unit:** Patients or donors, grouped by cohort where relevant
  - **Metric:** Held-out discrimination and calibration with biological-unit confidence intervals
  - **Interpretation / failure criterion:** A material loss of performance would weaken the claimed generalization; stability would address this specific concern.
- **pattern.test_set_tuning**: Use inner validation for tuning and retain an untouched evaluation set.
  - **Input:** Original predictor inputs and participant/cohort labels
  - **Comparison:** Reported pipeline versus all learned steps refit inside nested training folds
  - **Held-out / biological unit:** Patients or donors, grouped by cohort where relevant
  - **Metric:** Held-out discrimination and calibration with biological-unit confidence intervals
  - **Interpretation / failure criterion:** A material loss of performance would weaken the claimed generalization; stability would address this specific concern.
- **pattern.circular_signature**: Separate construction, annotation, and validation features and document any overlap.
  - **Input:** Construction features, validation features, independent phenotypes, and cohort membership
  - **Comparison:** Reported validation versus validation excluding construction/annotation information
  - **Held-out / biological unit:** Independent cohort and independent validation features
  - **Metric:** Prespecified association or predictive performance under an appropriate null
  - **Interpretation / failure criterion:** Loss of support when defining information is withheld would indicate circular validation.

## Secondary analyses

- **check.batch_platform**: Show cross-tabulations of condition with donor, batch, platform, and cancer type.
- **check.cutoff**: State when, where, and how any cutoff was chosen and locked.
- **check.pseudobulk**: Explain the independent unit and donor-aware model for each inferential test.
- **pattern.design_confounding**: Show condition-by-platform/batch tables and bound conclusions to identifiable comparisons.
- **check.ambient_rna**: Explain contamination assessment and whether correction was appropriate.
- **check.annotation_robustness**: State annotation provenance and separate labeling evidence from validation evidence.
- **check.cluster_stability**: Explain how clustering resolution and algorithm dependence were assessed.
- **check.composition**: For abundance claims, justify the donor-level model, denominators, and compositional assumptions.
- Additional items are retained in JSON and the detailed audit.

## Writing and framing changes

- **pattern.causal_overclaim**: Connect the wording to identifying evidence; if support is associative, use appropriately limited language.
  - **Section:** Abstract
  - **Claim to revise:** Our results prove a causal mechanism of treatment resistance across tissues.
  - **Framing:** Connect the wording to identifying evidence; if support is associative, use appropriately limited language.
- **pattern.conservation_overclaim**: Separate shared predictive structure from evidence of shared regulation.
  - **Section:** Abstract
  - **Claim to revise:** Transcriptomic similarity establishes mechanistic conservation across cancers.
  - **Framing:** Separate shared predictive structure from evidence of shared regulation.
- **check.limitations**: Explain design, measurement, cohort, and inference limitations in relation to the main claims.
  - **Section:** Methods
  - **Claim to revise:** We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - **Framing:** Explain design, measurement, cohort, and inference limitations in relation to the main claims.
- **pattern.novelty_overclaim**: Scope the novelty to a specific contribution and substantiate it with a literature comparison.
  - **Section:** Abstract
  - **Claim to revise:** We present the first-ever framework for a universal cancer response biomarker.
  - **Framing:** Scope the novelty to a specific contribution and substantiate it with a literature comparison.

## Novelty and positioning

- **pattern.novelty_overclaim**: Scope the novelty to a specific contribution and substantiate it with a literature comparison.

## Reproducibility gaps

- **check.code_availability**: Provide an accessible versioned repository, environment, and execution instructions.
- **check.data_availability**: Give accessions, cohort provenance, access restrictions, and a realistic access procedure.
- **check.random_seed**: State seeds for stochastic steps or explain why the workflow is deterministic.
- **check.software_versions**: Provide software versions and a pinned environment or container.

## Lower-priority reporting fixes

- **check.batch_platform**: Show cross-tabulations of condition with donor, batch, platform, and cancer type.
- **check.censoring**: Describe censoring, time origin, follow-up, competing risks, and model diagnostics.
- **check.clinical_use**: Define the decision, population, setting, comparator, and consequences of error.
- **check.code_availability**: Provide an accessible versioned repository, environment, and execution instructions.
- **check.cutoff**: State when, where, and how any cutoff was chosen and locked.
- **check.data_availability**: Give accessions, cohort provenance, access restrictions, and a realistic access procedure.
- **check.endpoint**: Define endpoints, measurement windows, adjudication, and follow-up.
- **check.external_validation**: Identify the independent cohort, provenance, overlap checks, and locked model; otherwise bound the claim.
- Additional items are retained in JSON and the detailed audit.

## Unverified reviewer suggestions

No additional item identified in this scope.

</details>

<details>
<summary>Detailed 20-section audit, findings, and deterministic checklist</summary>

## 1. Executive assessment

Text audit: 44 active concerns (major: 16, minor: 3, moderate: 25). These are review leads, not a judgment of scientific validity or submission acceptance. No automatic finding is classified as a fatal flaw.


## 2. Claimed contribution

Heuristic claim candidates; centrality and support require scientific review.

- We present the first-ever framework for a universal cancer response biomarker.
  - Source: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1
- Our results prove a causal mechanism of treatment resistance across tissues.
  - Source: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1
- Transcriptomic similarity establishes mechanistic conservation across cancers.
  - Source: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1
- We develop a single-cell predictor of clinical response using an observational cohort.
  - Source: manuscript; Introduction; line 11; block manuscript-5f53f81c8c24-1
- Our biomarker predicts treatment response and survival.
  - Source: manuscript; Introduction; line 12; block manuscript-5f53f81c8c24-1
- Our model predicts response with AUROC 0.98 (Figure 1).
  - Source: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1
- Our results prove a causal mechanism of resistance based on the observational association.
  - Source: manuscript; Results; line 32; block manuscript-7c9f0797fde7-1
- The embedding establishes a mechanistic axis linking every tissue.
  - Source: manuscript; Discussion; line 42; block manuscript-90a0443af449-1

## 3. Strongest evidence

Scientific strength cannot be ranked by text heuristics. Candidate reported quantitative results are listed below.

- Reported quantitative result (not independently verified): Our model predicts response with AUROC 0.98 (Figure 1).
The signature separates responders from nonresponders with p-value 0.001 (Table 1).
Our results prove a causal mechanism of resistance based on the observational association.
  - Source: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1

## 4. Weakest links

Highest-priority active concerns from the rule rubric.

- [pattern.cell_pseudoreplication](#patterncell_pseudoreplication)
- [pattern.cohort_reuse](#patterncohort_reuse)
- [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- [pattern.test_set_tuning](#patterntest_set_tuning)
- [check.batch_platform](#checkbatch_platform)
- [check.censoring](#checkcensoring)
- [check.clinical_use](#checkclinical_use)
- [check.code_availability](#checkcode_availability)

## 5. Major scientific concerns

- [check.external_validation](#checkexternal_validation)
- [pattern.causal_overclaim](#patterncausal_overclaim)
- [pattern.conservation_overclaim](#patternconservation_overclaim)
- [check.baseline_models](#checkbaseline_models)
- [check.limitations](#checklimitations)
- [check.sensitivity](#checksensitivity)

## 6. Major methods/statistics concerns

- [pattern.cell_pseudoreplication](#patterncell_pseudoreplication)
- [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- [pattern.test_set_tuning](#patterntest_set_tuning)
- [check.batch_platform](#checkbatch_platform)
- [check.censoring](#checkcensoring)
- [check.cutoff](#checkcutoff)
- [check.multiple_testing](#checkmultiple_testing)
- [check.pseudobulk](#checkpseudobulk)
- [pattern.design_confounding](#patterndesign_confounding)
- [check.ambient_rna](#checkambient_rna)
- [check.annotation_robustness](#checkannotation_robustness)
- [check.calibration](#checkcalibration)
- [check.cluster_stability](#checkcluster_stability)
- [check.composition](#checkcomposition)
- [check.confidence_intervals](#checkconfidence_intervals)
- [check.confounding](#checkconfounding)
- [check.donor_cell_balance](#checkdonor_cell_balance)
- [check.doublets](#checkdoublets)
- [check.grouped_validation](#checkgrouped_validation)
- [check.integration](#checkintegration)
- [check.metric_context](#checkmetric_context)
- [check.missingness](#checkmissingness)
- [check.null_models](#checknull_models)
- [check.thresholds](#checkthresholds)

## 7. Biological interpretation concerns

- [pattern.cohort_reuse](#patterncohort_reuse)
- [pattern.causal_overclaim](#patterncausal_overclaim)
- [pattern.circular_signature](#patterncircular_signature)
- [pattern.conservation_overclaim](#patternconservation_overclaim)
- [check.limitations](#checklimitations)

## 8. Claim-to-evidence map

Explicit figure/table links are candidates, not confirmed support. Unlinked claims have unestablished support.

- **claim-ecca1ed06169**: We present the first-ever framework for a universal cancer response biomarker.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1
- **claim-009b7a26360c**: Our results prove a causal mechanism of treatment resistance across tissues.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1
- **claim-659f836b89a9**: Transcriptomic similarity establishes mechanistic conservation across cancers.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1
- **claim-1a9ad9a5cb2d**: We develop a single-cell predictor of clinical response using an observational cohort.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Introduction; line 11; block manuscript-5f53f81c8c24-1
- **claim-e53a37e73774**: Our biomarker predicts treatment response and survival.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Introduction; line 12; block manuscript-5f53f81c8c24-1
- **claim-9ca13ec70fda**: Our model predicts response with AUROC 0.98 (Figure 1).
  - Support: candidate_reference_link. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1
  - Candidate: manuscript; Results; line 30; block manuscript-7c9f0797fde7-1
  - Candidate: manuscript; Figure Legends; line 36; block manuscript-cf5cfe3b844a-1
- **claim-e228425676c6**: Our results prove a causal mechanism of resistance based on the observational association.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Results; line 32; block manuscript-7c9f0797fde7-1
- **claim-718d5b64f692**: The embedding establishes a mechanistic axis linking every tissue.
  - Support: not_established_from_manuscript. A shared reference is a navigation aid, not a verified supporting result.
  - Source: manuscript; Discussion; line 42; block manuscript-90a0443af449-1

## 9. Potential leakage/confounding/circularity

- [pattern.cohort_reuse](#patterncohort_reuse)
- [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- [pattern.test_set_tuning](#patterntest_set_tuning)
- [check.batch_platform](#checkbatch_platform)
- [check.cutoff](#checkcutoff)
- [pattern.circular_signature](#patterncircular_signature)
- [pattern.design_confounding](#patterndesign_confounding)
- [check.confounding](#checkconfounding)
- [check.grouped_validation](#checkgrouped_validation)
- [check.integration](#checkintegration)

## 10. Missing controls or analyses

Reporting gaps require verification of applicability and of work that may exist outside the supplied text.

- [check.batch_platform](#checkbatch_platform)
- [check.censoring](#checkcensoring)
- [check.clinical_use](#checkclinical_use)
- [check.cutoff](#checkcutoff)
- [check.endpoint](#checkendpoint)
- [check.external_validation](#checkexternal_validation)
- [check.multiple_testing](#checkmultiple_testing)
- [check.pseudobulk](#checkpseudobulk)
- [check.ambient_rna](#checkambient_rna)
- [check.annotation_robustness](#checkannotation_robustness)
- [check.ascertainment](#checkascertainment)
- [check.baseline_models](#checkbaseline_models)
- [check.calibration](#checkcalibration)
- [check.clinical_utility](#checkclinical_utility)
- [check.cluster_stability](#checkcluster_stability)
- [check.composition](#checkcomposition)
- [check.confidence_intervals](#checkconfidence_intervals)
- [check.confounding](#checkconfounding)
- [check.donor_cell_balance](#checkdonor_cell_balance)
- [check.doublets](#checkdoublets)
- [check.grouped_validation](#checkgrouped_validation)
- [check.integration](#checkintegration)
- [check.limitations](#checklimitations)
- [check.metric_context](#checkmetric_context)
- [check.missingness](#checkmissingness)
- [check.null_models](#checknull_models)
- [check.prevalence_shift](#checkprevalence_shift)
- [check.sensitivity](#checksensitivity)
- [check.subgroups](#checksubgroups)
- [check.thresholds](#checkthresholds)
- [check.treatment_interaction](#checktreatment_interaction)

## 11. Alternative explanations

Hypotheses to test, not established explanations.

- Could donor, batch, cancer type, platform, or ascertainment explain the reported difference?
  - Findings: [check.batch_platform](#checkbatch_platform), [pattern.design_confounding](#patterndesign_confounding), [check.confounding](#checkconfounding)
- Could evaluation information entering development account for apparent predictive performance?
  - Findings: [pattern.feature_selection_before_split](#patternfeature_selection_before_split), [pattern.test_set_tuning](#patterntest_set_tuning), [check.cutoff](#checkcutoff), [check.grouped_validation](#checkgrouped_validation), [check.integration](#checkintegration)
- Could donor composition, cell counts, annotation, or integration choices explain the signal?
  - Findings: [pattern.cell_pseudoreplication](#patterncell_pseudoreplication), [check.pseudobulk](#checkpseudobulk), [check.ambient_rna](#checkambient_rna), [check.annotation_robustness](#checkannotation_robustness), [check.cluster_stability](#checkcluster_stability), [check.composition](#checkcomposition), [check.donor_cell_balance](#checkdonor_cell_balance), [check.doublets](#checkdoublets), [check.thresholds](#checkthresholds)
- Could construction or annotation choices make the validation result true by definition?
  - Findings: [pattern.cohort_reuse](#patterncohort_reuse), [pattern.circular_signature](#patterncircular_signature)

## 12. Reviewer-2 style objections

- What evidence addresses this concern: Cells treated as independent biological replicates: review the cited passage. Report donor nesting and justify the model; distinguish technical observations from biological replicates.
  - Findings: [pattern.cell_pseudoreplication](#patterncell_pseudoreplication)
- What evidence addresses this concern: Discovery and validation cohort reuse: review the cited passage. Label the analysis as internal reuse and identify independent validation if it exists.
  - Findings: [pattern.cohort_reuse](#patterncohort_reuse)
- What evidence addresses this concern: Feature selection before splitting: review the cited passage. Clarify whether selection used outcomes and evaluation samples; fit all learned selection inside training folds.
  - Findings: [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- What evidence addresses this concern: Test data used for tuning: review the cited passage. Use inner validation for tuning and retain an untouched evaluation set.
  - Findings: [pattern.test_set_tuning](#patterntest_set_tuning)
- What evidence addresses this concern: Batch, platform, and cancer-type confounding: not established from the manuscript. Show cross-tabulations of condition with donor, batch, platform, and cancer type.
  - Findings: [check.batch_platform](#checkbatch_platform)
- What evidence addresses this concern: Time-to-event and censoring methods: not established from the manuscript. Describe censoring, time origin, follow-up, competing risks, and model diagnostics.
  - Findings: [check.censoring](#checkcensoring)

## 13. Writing/clarity problems

Length-based suggestions are stylistic leads, not a comprehensive prose edit.


## 14. Innovation and positioning assessment

The offline tool cannot verify novelty or the current literature. Compare the precise contribution with the closest prior studies.

- [pattern.novelty_overclaim](#patternnovelty_overclaim)

## 15. Reproducibility/reporting gaps

- [check.code_availability](#checkcode_availability)
- [check.data_availability](#checkdata_availability)
- [check.random_seed](#checkrandom_seed)
- [check.software_versions](#checksoftware_versions)

## 16. Prioritized revision plan

- P0_verify_before_submission: Report donor nesting and justify the model; distinguish technical observations from biological replicates.
  - Rationale: The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.cell_pseudoreplication](#patterncell_pseudoreplication)
- P0_verify_before_submission: Label the analysis as internal reuse and identify independent validation if it exists.
  - Rationale: The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.cohort_reuse](#patterncohort_reuse)
- P0_verify_before_submission: Clarify whether selection used outcomes and evaluation samples; fit all learned selection inside training folds.
  - Rationale: The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- P0_verify_before_submission: Use inner validation for tuning and retain an untouched evaluation set.
  - Rationale: The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.test_set_tuning](#patterntest_set_tuning)
- P1_high_value_revision: Show cross-tabulations of condition with donor, batch, platform, and cancer type.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.batch_platform](#checkbatch_platform)
- P1_high_value_revision: Describe censoring, time origin, follow-up, competing risks, and model diagnostics.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.censoring](#checkcensoring)
- P1_high_value_revision: Define the decision, population, setting, comparator, and consequences of error.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.clinical_use](#checkclinical_use)
- P1_high_value_revision: Provide an accessible versioned repository, environment, and execution instructions.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: moderate; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.
  - Findings: [check.code_availability](#checkcode_availability)
- P1_high_value_revision: State when, where, and how any cutoff was chosen and locked.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.cutoff](#checkcutoff)
- P1_high_value_revision: Give accessions, cohort provenance, access restrictions, and a realistic access procedure.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: moderate; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.
  - Findings: [check.data_availability](#checkdata_availability)
- P1_high_value_revision: Define endpoints, measurement windows, adjudication, and follow-up.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.endpoint](#checkendpoint)
- P1_high_value_revision: Identify the independent cohort, provenance, overlap checks, and locked model; otherwise bound the claim.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.external_validation](#checkexternal_validation)
- P1_high_value_revision: State the hypothesis family, correction, threshold, and any unadjusted exploratory analyses.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.multiple_testing](#checkmultiple_testing)
- P1_high_value_revision: Explain the independent unit and donor-aware model for each inferential test.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.pseudobulk](#checkpseudobulk)
- P1_high_value_revision: Connect the wording to identifying evidence; if support is associative, use appropriately limited language.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.causal_overclaim](#patterncausal_overclaim)
- P1_high_value_revision: Separate construction, annotation, and validation features and document any overlap.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.circular_signature](#patterncircular_signature)
- P1_high_value_revision: Separate shared predictive structure from evidence of shared regulation.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.conservation_overclaim](#patternconservation_overclaim)
- P1_high_value_revision: Show condition-by-platform/batch tables and bound conclusions to identifiable comparisons.
  - Rationale: Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.design_confounding](#patterndesign_confounding)
- P2_targeted_clarification: Explain contamination assessment and whether correction was appropriate.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.ambient_rna](#checkambient_rna)
- P2_targeted_clarification: State annotation provenance and separate labeling evidence from validation evidence.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.annotation_robustness](#checkannotation_robustness)
- P2_targeted_clarification: Describe recruitment, inclusion/exclusion, sampling, and cohort flow.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.ascertainment](#checkascertainment)
- P2_targeted_clarification: Describe fair simple and clinical baselines with identical validation boundaries.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.baseline_models](#checkbaseline_models)
- P2_targeted_clarification: If probabilities are used, report calibration; otherwise explain why it is not applicable.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.calibration](#checkcalibration)
- P2_targeted_clarification: Bound clinical claims and distinguish utility evaluation from association.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.clinical_utility](#checkclinical_utility)
- P2_targeted_clarification: Explain how clustering resolution and algorithm dependence were assessed.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.cluster_stability](#checkcluster_stability)
- P2_targeted_clarification: For abundance claims, justify the donor-level model, denominators, and compositional assumptions.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.composition](#checkcomposition)
- P2_targeted_clarification: Report interval estimates for primary effects and predictive metrics, with their construction and sampling unit.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.confidence_intervals](#checkconfidence_intervals)
- P2_targeted_clarification: Identify candidate confounders, including cancer type, treatment, batch, platform, and ascertainment.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.confounding](#checkconfounding)
- P2_targeted_clarification: Report donors and cell counts by condition, batch, and cluster.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.donor_cell_balance](#checkdonor_cell_balance)
- P2_targeted_clarification: Describe doublet detection, rates, thresholds, and limitations.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.doublets](#checkdoublets)
- P2_targeted_clarification: Explain grouping, class balance, patient/cohort separation, and fold construction.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.grouped_validation](#checkgrouped_validation)
- P2_targeted_clarification: Document integration inputs, split timing, and comparisons with unintegrated analyses.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.integration](#checkintegration)
- P2_targeted_clarification: Explain design, measurement, cohort, and inference limitations in relation to the main claims.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.limitations](#checklimitations)
- P2_targeted_clarification: Define the positive class and explain metric choice, prevalence, and uncertainty.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.metric_context](#checkmetric_context)
- P2_targeted_clarification: Describe missingness by variable and cohort, assumptions, and fitting boundaries for imputation.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.missingness](#checkmissingness)
- P2_targeted_clarification: Explain the null hypothesis, preserved structure, exchangeability, and permutation count where applicable.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.null_models](#checknull_models)
- P2_targeted_clarification: Describe plausible prevalence and population shifts for the intended use.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.prevalence_shift](#checkprevalence_shift)
- P2_targeted_clarification: State seeds for stochastic steps or explain why the workflow is deterministic.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.
  - Findings: [check.random_seed](#checkrandom_seed)
- P2_targeted_clarification: Document sensitivity to defensible preprocessing, model, and threshold choices.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.sensitivity](#checksensitivity)
- P2_targeted_clarification: Provide software versions and a pinned environment or container.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.
  - Findings: [check.software_versions](#checksoftware_versions)
- P2_targeted_clarification: Describe justified subgroup analyses, sizes, uncertainty, and exploratory status.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.subgroups](#checksubgroups)
- P2_targeted_clarification: Report thresholds and their rationale, including post hoc changes.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.thresholds](#checkthresholds)
- P2_targeted_clarification: Clarify whether the claim is prognostic or treatment-predictive and justify the distinction.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [check.treatment_interaction](#checktreatment_interaction)
- P2_targeted_clarification: Scope the novelty to a specific contribution and substantiate it with a literature comparison.
  - Rationale: Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.
  - Findings: [pattern.novelty_overclaim](#patternnovelty_overclaim)

## 17. Suggested additional analyses

- Reanalyze using donor-level pseudobulk or an appropriate hierarchical model.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.cell_pseudoreplication](#patterncell_pseudoreplication)
- Validate a locked signature or model in a disjoint cohort with overlap checks.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.cohort_reuse](#patterncohort_reuse)
- Repeat nested evaluation with selection refit using training samples only.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.feature_selection_before_split](#patternfeature_selection_before_split)
- Re-evaluate the locked model in fresh data or a correctly nested design.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.test_set_tuning](#patterntest_set_tuning)
- Test contrasts within comparable strata and assess sensitivity to adjustment and integration.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.batch_platform](#checkbatch_platform)
- Check proportional hazards or relevant assumptions and report follow-up and event counts.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.censoring](#checkcensoring)
- Evaluate the proposed use against a relevant clinical baseline.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.clinical_use](#checkclinical_use)
- Evaluate a training-selected or prespecified threshold in untouched data.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.cutoff](#checkcutoff)
- Assess robustness to clinically justified endpoint definitions.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.endpoint](#checkendpoint)
- Evaluate the locked pipeline in a disjoint external cohort; report uncertainty and population differences.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.external_validation](#checkexternal_validation)
- Recompute adjusted results across the actual tested family and report effect sizes.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.multiple_testing](#checkmultiple_testing)
- Compare donor-level pseudobulk or a justified hierarchical model to the primary analysis.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.pseudobulk](#checkpseudobulk)
- Evaluate perturbation, rescue, temporal ordering, and alternative causal explanations as appropriate.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.causal_overclaim](#patterncausal_overclaim)
- Validate using independent features, phenotypes, perturbations, or held-out evidence.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.circular_signature](#patterncircular_signature)
- Test specific regulatory predictions with orthogonal perturbations across the relevant tissues or cohorts.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.conservation_overclaim](#patternconservation_overclaim)
- Evaluate an independently balanced cohort or within-stratum comparisons where overlap exists; adjustment alone may not identify fully confounded effects.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.design_confounding](#patterndesign_confounding)
- Test whether key markers persist under a defensible contamination correction.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.ambient_rna](#checkambient_rna)
- Repeat key contrasts with alternative annotations or reference atlases and independent markers.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.annotation_robustness](#checkannotation_robustness)
- Compare included and excluded subjects and characterize selection limitations.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.ascertainment](#checkascertainment)
- Compare against prespecified baseline models on the same held-out samples.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.baseline_models](#checkbaseline_models)
- Assess calibration plots, slope/intercept, and an appropriate proper scoring rule externally.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.calibration](#checkcalibration)
- Where appropriate, evaluate net benefit and consequences against standard care.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.clinical_utility](#checkclinical_utility)
- Compare cluster assignments across resolutions, seeds, and plausible preprocessing choices.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.cluster_stability](#checkcluster_stability)
- Use donor-aware differential abundance analysis and evaluate denominator sensitivity.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.composition](#checkcomposition)
- Estimate uncertainty using an appropriate model or resampling at the independent biological unit.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.confidence_intervals](#checkconfidence_intervals)
- Use justified stratification, adjustment, or negative controls; report overlap and residual limitations.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.confounding](#checkconfounding)
- Assess robustness to balanced sampling and donor-level weighting.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.donor_cell_balance](#checkdonor_cell_balance)
- Assess whether candidate states and conclusions survive reasonable doublet filters.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.doublets](#checkdoublets)
- Compare appropriate grouped folds and report fold-level class and cohort composition.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.grouped_validation](#checkgrouped_validation)
- Evaluate held-out donors without joint fitting and compare unintegrated biological contrasts.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.integration](#checkintegration)
- Assess sensitivity to the most consequential limitation where feasible.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.limitations](#checklimitations)
- Report complementary discrimination measures and prevalence-aware baselines.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.metric_context](#checkmetric_context)
- Evaluate sensitivity to plausible missing-data mechanisms and alternative handling.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.missingness](#checkmissingness)
- Use nulls or permutations that respect donor, cohort, batch, and feature dependence.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.null_models](#checknull_models)
- Evaluate discrimination, calibration, and decision thresholds across relevant populations.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.prevalence_shift](#checkprevalence_shift)
- Repeat primary analyses under justified alternatives and report stability of conclusions.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.sensitivity](#checksensitivity)
- Estimate subgroup performance without overstating underpowered differences.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.subgroups](#checksubgroups)
- Assess primary conclusions over a reasonable prespecified threshold range.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.thresholds](#checkthresholds)
- For treatment-benefit claims, assess a justified treatment-by-biomarker interaction in an appropriate design.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [check.treatment_interaction](#checktreatment_interaction)
- Build a comparison table of the closest prior methods, data, evidence, and practical differences.
  - Condition: First verify the concern and applicability; this is a proposal, not a reported result.
  - Findings: [pattern.novelty_overclaim](#patternnovelty_overclaim)

## 18. Suggested text edits

- Conditional edit template: These results are consistent with [specific interpretation]; the proposed mechanism requires independent testing.
  - Original: Our results prove a causal mechanism of treatment resistance across tissues.
  - Condition: Fill placeholders only with supported facts; confirm the revised sentence fits the actual study.
  - Findings: [pattern.causal_overclaim](#patterncausal_overclaim)
- Conditional edit template: These results are consistent with [specific interpretation]; the proposed mechanism requires independent testing.
  - Original: Transcriptomic similarity establishes mechanistic conservation across cancers.
  - Condition: Fill placeholders only with supported facts; confirm the revised sentence fits the actual study.
  - Findings: [pattern.conservation_overclaim](#patternconservation_overclaim)
- Conditional edit template: We present [specific contribution] and evaluate it against [named comparators].
  - Original: We present the first-ever framework for a universal cancer response biomarker.
  - Condition: Fill placeholders only with supported facts; confirm the revised sentence fits the actual study.
  - Findings: [pattern.novelty_overclaim](#patternnovelty_overclaim)

## 19. Journal-fit assessment

Target: not supplied. Current scope, article types, and editorial requirements were not checked. Fit is not established from a journal name alone. Assess audience, contribution type, validation depth, reporting requirements, and the journal's current aims.


## 20. Confidence/uncertainty notes

Confidence describes the text match, not the probability that a scientific conclusion is wrong.

- No underlying data, analysis code, figure images, or external literature were verified.
- Reviewer roles route deterministic findings; no LLM review was performed.
- Extraction is heuristic; false positives and omissions require manual review.
- Figures, causal support, biological validity, and novelty are not independently verified.
- Absence means not established from the supplied text. Reported cues do not establish method adequacy.
- Established issues identify an explicitly described design or wording; they do not verify execution or effect on results.
- Manual overrides are version-bound and retained with reasons. Dismissed findings remain in JSON.

## Finding details

### pattern.cell_pseudoreplication

**major | established_issue | P0_verify_before_submission | confidence: high | active**

Cells treated as independent biological replicates: review the cited passage.

**Why it matters:** Within-donor dependence can understate uncertainty when cells replace donors as independent units.

**Suggested fix:** Report donor nesting and justify the model; distinguish technical observations from biological replicates.

**Suggested analysis:** Reanalyze using donor-level pseudobulk or an appropriate hierarchical model.

**Priority rationale:** The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> Cells were treated as independent biological replicates in the t-test.

Source: manuscript; Methods; line 24; block manuscript-f766920c10f0-1 (trigger)

### pattern.cohort_reuse

**major | established_issue | P0_verify_before_submission | confidence: high | active**

Discovery and validation cohort reuse: review the cited passage.

**Why it matters:** Reuse does not establish independent validation and can repeat discovery biases.

**Suggested fix:** Label the analysis as internal reuse and identify independent validation if it exists.

**Suggested analysis:** Validate a locked signature or model in a disjoint cohort with overlap checks.

**Priority rationale:** The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 22; block manuscript-5237193ee4be-1 (trigger)

### pattern.feature_selection_before_split

**major | established_issue | P0_verify_before_submission | confidence: high | active**

Feature selection before splitting: review the cited passage.

**Why it matters:** Data-dependent selection using evaluation samples makes the reported evaluation non-independent.

**Suggested fix:** Clarify whether selection used outcomes and evaluation samples; fit all learned selection inside training folds.

**Suggested analysis:** Repeat nested evaluation with selection refit using training samples only.

**Priority rationale:** The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (trigger)

### pattern.test_set_tuning

**major | established_issue | P0_verify_before_submission | confidence: high | active**

Test data used for tuning: review the cited passage.

**Why it matters:** Choosing model settings on a test set turns it into development data.

**Suggested fix:** Use inner validation for tuning and retain an untouched evaluation set.

**Suggested analysis:** Re-evaluate the locked model in fresh data or a correctly nested design.

**Priority rationale:** The described design may invalidate a primary inference; verify it before relying on the result. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> We tuned hyperparameters using performance on the test set.

Source: manuscript; Methods; line 21; block manuscript-5237193ee4be-1 (trigger)

### check.batch_platform

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Batch, platform, and cancer-type confounding: not established from the manuscript.

**Why it matters:** Technical or disease composition can align with the biological contrast.

**Suggested fix:** Show cross-tabulations of condition with donor, batch, platform, and cancer type.

**Suggested analysis:** Test contrasts within comparable strata and assess sensitivity to adjustment and integration.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.censoring

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Time-to-event and censoring methods: not established from the manuscript.

**Why it matters:** Time-to-event results depend on follow-up, censoring, and model assumptions.

**Suggested fix:** Describe censoring, time origin, follow-up, competing risks, and model diagnostics.

**Suggested analysis:** Check proportional hazards or relevant assumptions and report follow-up and event counts.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.clinical_use

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Intended clinical use: not established from the manuscript.

**Why it matters:** A predictive association is not yet a clinically actionable use case.

**Suggested fix:** Define the decision, population, setting, comparator, and consequences of error.

**Suggested analysis:** Evaluate the proposed use against a relevant clinical baseline.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.code_availability

**moderate | plausible_issue | P1_high_value_revision | confidence: low | active**

Code availability: not established from the manuscript.

**Why it matters:** Readers need access to the analysis implementation.

**Suggested fix:** Provide an accessible versioned repository, environment, and execution instructions.

**Suggested analysis:** Run the documented pipeline from a clean environment.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: moderate; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.cutoff

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Cutoff selection: not established from the manuscript.

**Why it matters:** Outcome-informed threshold selection can bias reported performance.

**Suggested fix:** State when, where, and how any cutoff was chosen and locked.

**Suggested analysis:** Evaluate a training-selected or prespecified threshold in untouched data.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.data_availability

**moderate | plausible_issue | P1_high_value_revision | confidence: low | active**

Data availability and access: not established from the manuscript.

**Why it matters:** Data provenance and access conditions are necessary for independent evaluation.

**Suggested fix:** Give accessions, cohort provenance, access restrictions, and a realistic access procedure.

**Suggested analysis:** Verify that the stated accessions and derived artifacts support the reported analyses.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: moderate; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.endpoint

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Endpoint definition: not established from the manuscript.

**Why it matters:** Ambiguous outcomes hinder interpretation and transportability.

**Suggested fix:** Define endpoints, measurement windows, adjudication, and follow-up.

**Suggested analysis:** Assess robustness to clinically justified endpoint definitions.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.external_validation

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Independent external validation: not established from the manuscript.

**Why it matters:** Internal reuse can leave transportability and performance optimism unresolved.

**Suggested fix:** Identify the independent cohort, provenance, overlap checks, and locked model; otherwise bound the claim.

**Suggested analysis:** Evaluate the locked pipeline in a disjoint external cohort; report uncertainty and population differences.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.multiple_testing

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Multiplicity correction: not established from the manuscript.

**Why it matters:** Searching many hypotheses can produce false discoveries without a justified error-control strategy.

**Suggested fix:** State the hypothesis family, correction, threshold, and any unadjusted exploratory analyses.

**Suggested analysis:** Recompute adjusted results across the actual tested family and report effect sizes.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.pseudobulk

**major | plausible_issue | P1_high_value_revision | confidence: low | active**

Donor-aware single-cell inference: not established from the manuscript.

**Why it matters:** Cells from the same donor share biological and technical variation.

**Suggested fix:** Explain the independent unit and donor-aware model for each inferential test.

**Suggested analysis:** Compare donor-level pseudobulk or a justified hierarchical model to the primary analysis.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### pattern.causal_overclaim

**major | plausible_issue | P1_high_value_revision | confidence: medium | active**

Causal or mechanistic wording needs support: review the cited passage.

**Why it matters:** A strong causal phrase requires a design that identifies the claimed mechanism or causal effect.

**Suggested fix:** Connect the wording to identifying evidence; if support is associative, use appropriately limited language.

**Suggested analysis:** Evaluate perturbation, rescue, temporal ordering, and alternative causal explanations as appropriate.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> Our results prove a causal mechanism of treatment resistance across tissues.

Source: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1 (trigger)

> Transcriptomic similarity establishes mechanistic conservation across cancers.

Source: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1 (trigger)

> Our results prove a causal mechanism of resistance based on the observational association.

Source: manuscript; Results; line 32; block manuscript-7c9f0797fde7-1 (trigger)

> The embedding establishes a mechanistic axis linking every tissue.

Source: manuscript; Discussion; line 42; block manuscript-90a0443af449-1 (trigger)

### pattern.circular_signature

**major | plausible_issue | P1_high_value_revision | confidence: medium | active**

Signature reused for its own validation: review the cited passage.

**Why it matters:** Reusing defining features as evidence of validity may produce a tautological result.

**Suggested fix:** Separate construction, annotation, and validation features and document any overlap.

**Suggested analysis:** Validate using independent features, phenotypes, perturbations, or held-out evidence.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> We used the same genes to construct the signature and validate the signature.

Source: manuscript; Methods; line 25; block manuscript-f766920c10f0-1 (trigger)

### pattern.conservation_overclaim

**major | plausible_issue | P1_high_value_revision | confidence: medium | active**

Similarity or transferability used to claim conservation: review the cited passage.

**Why it matters:** Transcriptomic similarity or transfer alone does not establish a conserved regulatory mechanism.

**Suggested fix:** Separate shared predictive structure from evidence of shared regulation.

**Suggested analysis:** Test specific regulatory predictions with orthogonal perturbations across the relevant tissues or cohorts.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> Transcriptomic similarity establishes mechanistic conservation across cancers.

Source: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1 (trigger)

### pattern.design_confounding

**major | established_issue | P1_high_value_revision | confidence: high | active**

Condition aligned with batch or platform: review the cited passage.

**Why it matters:** When a biological contrast aligns with a technical stratum, its separate contribution may be unidentifiable.

**Suggested fix:** Show condition-by-platform/batch tables and bound conclusions to identifiable comparisons.

**Suggested analysis:** Evaluate an independently balanced cohort or within-stratum comparisons where overlap exists; adjustment alone may not identify fully confounded effects.

**Priority rationale:** Material scientific risk or a high-value, low-effort improvement likely to attract reviewer attention. Severity: major; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 18; block manuscript-dc3b7f1eb694-1 (trigger)

### check.ambient_rna

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Ambient RNA assessment: not established from the manuscript.

**Why it matters:** Ambient transcripts can distort marker expression and state assignments.

**Suggested fix:** Explain contamination assessment and whether correction was appropriate.

**Suggested analysis:** Test whether key markers persist under a defensible contamination correction.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.annotation_robustness

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Annotation and reference robustness: not established from the manuscript.

**Why it matters:** Reference choice and reused marker genes can predetermine the interpretation.

**Suggested fix:** State annotation provenance and separate labeling evidence from validation evidence.

**Suggested analysis:** Repeat key contrasts with alternative annotations or reference atlases and independent markers.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.ascertainment

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Cohort ascertainment: not established from the manuscript.

**Why it matters:** Selection processes can alter apparent performance and applicability.

**Suggested fix:** Describe recruitment, inclusion/exclusion, sampling, and cohort flow.

**Suggested analysis:** Compare included and excluded subjects and characterize selection limitations.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.baseline_models

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Baseline models: not established from the manuscript.

**Why it matters:** Incremental predictive value is unclear without meaningful comparators.

**Suggested fix:** Describe fair simple and clinical baselines with identical validation boundaries.

**Suggested analysis:** Compare against prespecified baseline models on the same held-out samples.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.calibration

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Predictive calibration: not established from the manuscript.

**Why it matters:** Discrimination does not establish the accuracy of predicted probabilities.

**Suggested fix:** If probabilities are used, report calibration; otherwise explain why it is not applicable.

**Suggested analysis:** Assess calibration plots, slope/intercept, and an appropriate proper scoring rule externally.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.clinical_utility

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Clinical utility: not established from the manuscript.

**Why it matters:** Statistical significance does not establish useful clinical decisions.

**Suggested fix:** Bound clinical claims and distinguish utility evaluation from association.

**Suggested analysis:** Where appropriate, evaluate net benefit and consequences against standard care.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.cluster_stability

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Cluster stability: not established from the manuscript.

**Why it matters:** An unstable clustering can undermine downstream interpretation.

**Suggested fix:** Explain how clustering resolution and algorithm dependence were assessed.

**Suggested analysis:** Compare cluster assignments across resolutions, seeds, and plausible preprocessing choices.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.composition

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Differential abundance and compositional effects: not established from the manuscript.

**Why it matters:** Cell fractions are interdependent and sampled within donors.

**Suggested fix:** For abundance claims, justify the donor-level model, denominators, and compositional assumptions.

**Suggested analysis:** Use donor-aware differential abundance analysis and evaluate denominator sensitivity.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.confidence_intervals

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Confidence intervals or credible intervals: not established from the manuscript.

**Why it matters:** Point estimates alone do not communicate sampling uncertainty.

**Suggested fix:** Report interval estimates for primary effects and predictive metrics, with their construction and sampling unit.

**Suggested analysis:** Estimate uncertainty using an appropriate model or resampling at the independent biological unit.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.confounding

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Confounder assessment: not established from the manuscript.

**Why it matters:** Observed differences may reflect cohort composition rather than the proposed biology.

**Suggested fix:** Identify candidate confounders, including cancer type, treatment, batch, platform, and ascertainment.

**Suggested analysis:** Use justified stratification, adjustment, or negative controls; report overlap and residual limitations.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.donor_cell_balance

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Donor and cell-number balance: not established from the manuscript.

**Why it matters:** Unequal cell contributions can dominate pooled results.

**Suggested fix:** Report donors and cell counts by condition, batch, and cluster.

**Suggested analysis:** Assess robustness to balanced sampling and donor-level weighting.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.doublets

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Doublet handling: not established from the manuscript.

**Why it matters:** Doublets can mimic hybrid states or alter cell abundance.

**Suggested fix:** Describe doublet detection, rates, thresholds, and limitations.

**Suggested analysis:** Assess whether candidate states and conclusions survive reasonable doublet filters.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.grouped_validation

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Grouped or stratified validation: not established from the manuscript.

**Why it matters:** Related samples and imbalanced folds can inflate apparent generalization.

**Suggested fix:** Explain grouping, class balance, patient/cohort separation, and fold construction.

**Suggested analysis:** Compare appropriate grouped folds and report fold-level class and cohort composition.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.integration

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Integration artifacts and leakage: not established from the manuscript.

**Why it matters:** Integration may erase biology or transfer evaluation information into training.

**Suggested fix:** Document integration inputs, split timing, and comparisons with unintegrated analyses.

**Suggested analysis:** Evaluate held-out donors without joint fitting and compare unintegrated biological contrasts.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.limitations

**minor | plausible_issue | P2_targeted_clarification | confidence: low | active**

Acknowledged limitations: not established from the manuscript.

**Why it matters:** Readers need explicit boundaries on what the study establishes.

**Suggested fix:** Explain design, measurement, cohort, and inference limitations in relation to the main claims.

**Suggested analysis:** Assess sensitivity to the most consequential limitation where feasible.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.metric_context

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Discrimination metrics and class prevalence: not established from the manuscript.

**Why it matters:** AUROC and AUPRC answer different questions and depend differently on class distribution.

**Suggested fix:** Define the positive class and explain metric choice, prevalence, and uncertainty.

**Suggested analysis:** Report complementary discrimination measures and prevalence-aware baselines.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.missingness

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Missing data: not established from the manuscript.

**Why it matters:** Missingness and its handling can introduce selection or leakage.

**Suggested fix:** Describe missingness by variable and cohort, assumptions, and fitting boundaries for imputation.

**Suggested analysis:** Evaluate sensitivity to plausible missing-data mechanisms and alternative handling.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.null_models

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Null model or permutation rationale: not established from the manuscript.

**Why it matters:** A poorly specified null can misrepresent the evidence against chance.

**Suggested fix:** Explain the null hypothesis, preserved structure, exchangeability, and permutation count where applicable.

**Suggested analysis:** Use nulls or permutations that respect donor, cohort, batch, and feature dependence.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.prevalence_shift

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Population or prevalence shift: not established from the manuscript.

**Why it matters:** Deployment populations may differ from the development sample.

**Suggested fix:** Describe plausible prevalence and population shifts for the intended use.

**Suggested analysis:** Evaluate discrimination, calibration, and decision thresholds across relevant populations.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.random_seed

**minor | plausible_issue | P2_targeted_clarification | confidence: low | active**

Random seeds: not established from the manuscript.

**Why it matters:** Stochastic procedures may not be reproducible without the random state.

**Suggested fix:** State seeds for stochastic steps or explain why the workflow is deterministic.

**Suggested analysis:** Repeat key stochastic steps across seeds and report material variation.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.sensitivity

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Sensitivity and robustness analyses: not established from the manuscript.

**Why it matters:** A conclusion may depend on one preprocessing or modeling choice.

**Suggested fix:** Document sensitivity to defensible preprocessing, model, and threshold choices.

**Suggested analysis:** Repeat primary analyses under justified alternatives and report stability of conclusions.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.software_versions

**minor | plausible_issue | P2_targeted_clarification | confidence: low | active**

Software and environment versions: not established from the manuscript.

**Why it matters:** Unspecified software versions hinder exact reproduction.

**Suggested fix:** Provide software versions and a pinned environment or container.

**Suggested analysis:** Check that a clean installation reproduces a representative result.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: minor; notice likelihood: high; effort: low; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.subgroups

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Subgroup stability: not established from the manuscript.

**Why it matters:** Aggregate performance can hide clinically important heterogeneity.

**Suggested fix:** Describe justified subgroup analyses, sizes, uncertainty, and exploratory status.

**Suggested analysis:** Estimate subgroup performance without overstating underpowered differences.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.thresholds

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Threshold sensitivity: not established from the manuscript.

**Why it matters:** Filtering and classification thresholds can select the apparent signal.

**Suggested fix:** Report thresholds and their rationale, including post hoc changes.

**Suggested analysis:** Assess primary conclusions over a reasonable prespecified threshold range.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### check.treatment_interaction

**moderate | plausible_issue | P2_targeted_clarification | confidence: low | active**

Predictive versus prognostic interpretation: not established from the manuscript.

**Why it matters:** Prognostic association alone does not demonstrate differential treatment benefit.

**Suggested fix:** Clarify whether the claim is prognostic or treatment-predictive and justify the distinction.

**Suggested analysis:** For treatment-benefit claims, assess a justified treatment-by-biomarker interaction in an appropriate design.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Not established from the manuscript text searched; this does not establish that the work was not done. Section and language heuristics can miss synonymous or implicit descriptions.

> We analyzed 12 patients with cancer and profiled 48,000 cells.
> Eight patients were responders and four were nonresponders.
> All responders were measured on platform A and all nonresponders on platform B.

Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1 (context_only)

> We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
> We tuned hyperparameters using performance on the test set.
> The same cohort was used for discovery and validation.

Source: manuscript; Methods; line 20; block manuscript-5237193ee4be-1 (context_only)

### pattern.novelty_overclaim

**moderate | plausible_issue | P2_targeted_clarification | confidence: medium | active**

Absolute novelty claim: review the cited passage.

**Why it matters:** Absolute novelty requires a scoped and current literature comparison, which this offline tool cannot verify.

**Suggested fix:** Scope the novelty to a specific contribution and substantiate it with a literature comparison.

**Suggested analysis:** Build a comparison table of the closest prior methods, data, evidence, and practical differences.

**Priority rationale:** Targeted reporting or analysis can clarify the concern after primary design risks are addressed. Severity: moderate; notice likelihood: high; effort: medium; value: high. These are editable heuristic judgments.

**Limit:** Text heuristics do not verify the underlying analysis or data.

> We present the first-ever framework for a universal cancer response biomarker.

Source: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1 (trigger)

## Reporting checklist

| Check | Status | Confidence |
| --- | --- | --- |
| Independent external validation | not_established | low |
| Confidence intervals or credible intervals | not_established | low |
| Identifiable sample-size statements | reported | medium |
| Biological replication units | reported | medium |
| Train/test separation | reported | medium |
| Grouped or stratified validation | not_established | low |
| Random seeds | not_established | low |
| Code availability | not_established | low |
| Data availability and access | not_established | low |
| Multiplicity correction | not_established | low |
| Acknowledged limitations | not_established | low |
| Predictive calibration | not_established | low |
| Discrimination metrics and class prevalence | not_established | low |
| Baseline models | not_established | low |
| Confounder assessment | not_established | low |
| Sensitivity and robustness analyses | not_established | low |
| Null model or permutation rationale | not_established | low |
| Software and environment versions | not_established | low |
| Donor-aware single-cell inference | not_established | low |
| Donor and cell-number balance | not_established | low |
| Batch, platform, and cancer-type confounding | not_established | low |
| Cluster stability | not_established | low |
| Annotation and reference robustness | not_established | low |
| Doublet handling | not_established | low |
| Ambient RNA assessment | not_established | low |
| Integration artifacts and leakage | not_established | low |
| Differential abundance and compositional effects | not_established | low |
| Threshold sensitivity | not_established | low |
| Perturbation efficiency | not_applicable | low |
| Multiple guides and guide-level consistency | not_applicable | low |
| MOI assumptions | not_applicable | low |
| Essential-gene and toxicity confounding | not_applicable | low |
| Off-target assessment | not_applicable | low |
| Positive and negative controls | not_applicable | low |
| Screen QC and replicate concordance | not_applicable | low |
| Modality and screen-model assumptions | not_applicable | low |
| Intended clinical use | not_established | low |
| Endpoint definition | not_established | low |
| Cohort ascertainment | not_established | low |
| Population or prevalence shift | not_established | low |
| Cutoff selection | not_established | low |
| Predictive versus prognostic interpretation | not_established | low |
| Subgroup stability | not_established | low |
| Missing data | not_established | low |
| Time-to-event and censoring methods | not_established | low |
| Clinical utility | not_established | low |

</details>


## Input provenance

- manuscript: flawed_manuscript.md; SHA-256 9a1248de91fc89eeb93910fef07175167c06f9054a7755fa184b4b1239dbddef
