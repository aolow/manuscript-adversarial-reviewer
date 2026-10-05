# Manuscript version comparison

The revision contains candidate improvements in reporting or design description. Material improvement in scientific rigor is not established without inspecting the actual analyses.

Some matched claims use more qualified wording, which may make positioning more defensible; novelty and evidential adequacy remain unverified.

## Major concerns at a glance

Newly detected concerns may reflect new disclosure or prior detection gaps. Resolution does not verify execution.

- **Resolved (4)**
  - check.batch_platform: Batch, platform, and cancer-type confounding: not established from the manuscript.
  - check.external_validation: Independent external validation: not established from the manuscript.
  - check.multiple_testing: Multiplicity correction: not established from the manuscript.
  - check.pseudobulk: Donor-aware single-cell inference: not established from the manuscript.
- **Partially resolved (5)**
  - pattern.cell_pseudoreplication: Cells treated as independent biological replicates: review the cited passage.
  - pattern.cohort_reuse: Discovery and validation cohort reuse: review the cited passage.
  - pattern.feature_selection_before_split: Feature selection before splitting: review the cited passage.
  - pattern.test_set_tuning: Test data used for tuning: review the cited passage.
  - pattern.circular_signature: Signature reused for its own validation: review the cited passage.
- **Persistent (5)**
  - check.censoring: Time-to-event and censoring methods: not established from the manuscript.
  - check.clinical_use: Intended clinical use: not established from the manuscript.
  - check.cutoff: Cutoff selection: not established from the manuscript.
  - check.endpoint: Endpoint definition: not established from the manuscript.
  - pattern.design_confounding: Condition aligned with batch or platform: review the cited passage.
- **Worsened (0)**
- **Unclear (2)**
  - pattern.causal_overclaim: Causal or mechanistic wording needs support: review the cited passage.
  - pattern.conservation_overclaim: Similarity or transferability used to claim conservation: review the cited passage.
- **Newly introduced / detected (0)**
- **Scope withdrawn (not a methodological repair) (0)**

## Scientific concern resolution

Resolution is assessed from supplied manuscript descriptions; execution is not independently verified.

- **pattern.cell_pseudoreplication: partially_resolved** — A corrective design is described, but sufficiency and execution have not been verified.
  - Scope: reported_design_only
  - old: manuscript; Methods; line 24; block manuscript-f766920c10f0-1; Cells were treated as independent biological replicates in the t-test.
  - new: manuscript; Methods; line 25; block manuscript-4d207a9e595d-1; We aggregated counts into donor-level pseudobulk for differential expression.
  - new: manuscript; Figure Legends; line 42; block manuscript-6c8685ac7be6-1; Donor-level comparisons of signature scores.
- **pattern.cohort_reuse: partially_resolved** — A corrective design is described, but sufficiency and execution have not been verified.
  - Scope: reported_design_only
  - old: manuscript; Methods; line 22; block manuscript-5237193ee4be-1; The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 23; block manuscript-2e5ecd201a97-1; An independent external cohort of 30 patients was used to evaluate the locked model.
  - new: manuscript; Figure Legends; line 41; block manuscript-6c8685ac7be6-1; ROC curve computed in the independent external cohort.
- **pattern.feature_selection_before_split: partially_resolved** — A corrective design is described, but sufficiency and execution have not been verified.
  - Scope: reported_design_only
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
  - new: manuscript; Methods; line 21; block manuscript-2e5ecd201a97-1; Feature selection was performed only within each training fold using training samples.
- **pattern.test_set_tuning: partially_resolved** — A corrective design is described, but sufficiency and execution have not been verified.
  - Scope: reported_design_only
  - old: manuscript; Methods; line 21; block manuscript-5237193ee4be-1; We tuned hyperparameters using performance on the test set.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
  - new: manuscript; Methods; line 22; block manuscript-2e5ecd201a97-1; Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
- **check.batch_platform: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1; Platform and response remain confounded in the discovery cohort.
- **check.censoring: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.clinical_use: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Discussion; line 46; block manuscript-339b97a05091-1; The intended clinical use would be risk stratification, pending further evaluation.
- **check.code_availability: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Availability; line 57; block manuscript-d12ce0d980c9-1; Code is available at https://example.org/synthetic-code.
- **check.cutoff: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.data_availability: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Availability; line 58; block manuscript-d12ce0d980c9-1; Synthetic data are available at https://example.org/synthetic-data.
- **check.endpoint: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.external_validation: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 23; block manuscript-2e5ecd201a97-1; An independent external cohort of 30 patients was used to evaluate the locked model.
  - new: manuscript; Figure Legends; line 41; block manuscript-6c8685ac7be6-1; ROC curve computed in the independent external cohort.
- **check.multiple_testing: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 27; block manuscript-4d207a9e595d-1; P-values were adjusted with the Benjamini-Hochberg false discovery rate procedure.
  - new: manuscript; Results; line 34; block manuscript-7e7ce94cfc8d-1; The signature separates responders from nonresponders with an adjusted p-value of 0.04 (Table 1).
- **check.pseudobulk: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
  - new: manuscript; Methods; line 25; block manuscript-4d207a9e595d-1; We aggregated counts into donor-level pseudobulk for differential expression.
  - new: manuscript; Figure Legends; line 42; block manuscript-6c8685ac7be6-1; Donor-level comparisons of signature scores.
- **pattern.causal_overclaim: cannot_determine** — No sufficient evidence establishes resolution; a disappearing flag is not a fix.
  - Scope: not_verified
  - old: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1; Our results prove a causal mechanism of treatment resistance across tissues.
  - old: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1; Transcriptomic similarity establishes mechanistic conservation across cancers.
  - old: manuscript; Results; line 32; block manuscript-7c9f0797fde7-1; Our results prove a causal mechanism of resistance based on the observational association.
  - old: manuscript; Discussion; line 42; block manuscript-90a0443af449-1; The embedding establishes a mechanistic axis linking every tissue.
  - new: manuscript; Abstract; line 5; block manuscript-93de9f537e1c-1; We present a framework for a cancer response biomarker in the studied population.
Our results suggest an association with treatment resistance across tissues.
Transcriptomic similarity suggests shared expression patterns across cancers.
- **pattern.circular_signature: partially_resolved** — A corrective design is described, but sufficiency and execution have not been verified.
  - Scope: reported_design_only
  - old: manuscript; Methods; line 25; block manuscript-f766920c10f0-1; We used the same genes to construct the signature and validate the signature.
  - new: manuscript; Methods; line 26; block manuscript-4d207a9e595d-1; Independent marker genes were used for signature validation.
- **pattern.conservation_overclaim: cannot_determine** — No sufficient evidence establishes resolution; a disappearing flag is not a fix.
  - Scope: not_verified
  - old: manuscript; Abstract; line 7; block manuscript-48a71d89af2c-1; Transcriptomic similarity establishes mechanistic conservation across cancers.
  - new: manuscript; Abstract; line 5; block manuscript-93de9f537e1c-1; We present a framework for a cancer response biomarker in the studied population.
Our results suggest an association with treatment resistance across tissues.
Transcriptomic similarity suggests shared expression patterns across cancers.
- **pattern.design_confounding: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 18; block manuscript-dc3b7f1eb694-1; All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 18; block manuscript-dc3b7f1eb694-1; All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1; Platform and response remain confounded in the discovery cohort.
- **check.ambient_rna: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.annotation_robustness: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Results; line 36; block manuscript-7e7ce94cfc8d-1; Sensitivity analyses used alternative preprocessing and alternative annotations.
- **check.ascertainment: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.baseline_models: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Results; line 37; block manuscript-7e7ce94cfc8d-1; A clinical-only baseline model reached AUROC 0.69.
- **check.calibration: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1; Clinical utility, calibration, and subgroup stability require further study.
- **check.clinical_utility: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1; Clinical utility, calibration, and subgroup stability require further study.
- **check.cluster_stability: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.composition: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.confidence_intervals: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Results; line 33; block manuscript-7e7ce94cfc8d-1; Our model predicts response with AUROC 0.72 and a 95% confidence interval of 0.55 to 0.86 (Figure 1).
- **check.confounding: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1; Platform and response remain confounded in the discovery cohort.
- **check.donor_cell_balance: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.doublets: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.grouped_validation: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
- **check.integration: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.limitations: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 52; block manuscript-f79ee62de01a-1; This observational design cannot establish causality or conserved regulation.
- **check.metric_context: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.missingness: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.null_models: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.prevalence_shift: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.random_seed: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 28; block manuscript-4d207a9e595d-1; Random seed 42 was used for splitting and model fitting.
- **check.sensitivity: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Results; line 36; block manuscript-7e7ce94cfc8d-1; Sensitivity analyses used alternative preprocessing and alternative annotations.
- **check.software_versions: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 29; block manuscript-4d207a9e595d-1; The analysis used Python version 3.11 and a pinned requirements.txt.
- **check.subgroups: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1; Clinical utility, calibration, and subgroup stability require further study.
- **check.thresholds: unresolved** — The concern is still supported by detected passages in the revised manuscript.
  - Scope: not_verified
  - Wording softened while the methodological concern remains.
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - new: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1; We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.
- **check.treatment_interaction: resolved** — A previously missing description is now reported; adequacy and execution remain unverified.
  - Scope: reporting_only
  - old: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1; We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.
  - old: manuscript; Methods; line 20; block manuscript-5237193ee4be-1; We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.
  - new: manuscript; Discussion; line 47; block manuscript-339b97a05091-1; The findings describe a prognostic association rather than differential treatment benefit.
- **pattern.novelty_overclaim: cannot_determine** — No sufficient evidence establishes resolution; a disappearing flag is not a fix.
  - Scope: not_verified
  - old: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1; We present the first-ever framework for a universal cancer response biomarker.
  - new: manuscript; Abstract; line 5; block manuscript-93de9f537e1c-1; We present a framework for a cancer response biomarker in the studied population.
Our results suggest an association with treatment resistance across tissues.
Transcriptomic similarity suggests shared expression patterns across cancers.

## Textual changes in substantive sections

- manuscript / Abstract: replace
  - Before: We present the first-ever framework for a universal cancer response biomarker.
Our results prove a causal mechanism of treatment resistance across tissues.
Transcriptomic similarity establishes mechanistic conservation across cancers.
  - After: We present a framework for a cancer response biomarker in the studied population.
Our results suggest an association with treatment resistance across tissues.
Transcriptomic similarity suggests shared expression patterns across cancers.
- manuscript / Availability: insert
  - Before: 
  - After: Code is available at https://example.org/synthetic-code.
Synthetic data are available at https://example.org/synthetic-data.
- manuscript / Discussion: replace
  - Before: This biomarker should guide therapy selection in all cancer populations.
The embedding establishes a mechanistic axis linking every tissue.
  - After: The intended clinical use would be risk stratification, pending further evaluation.
The findings describe a prognostic association rather than differential treatment benefit.
- manuscript / Figure Legends: replace
  - Before: Figure 1. ROC curve computed from the test set.
Table 1. Cell-level comparisons of signature scores.
  - After: Figure 1. ROC curve computed in the independent external cohort.
Table 1. Donor-level comparisons of signature scores.
- manuscript / Limitations: insert
  - Before: 
  - After: Platform and response remain confounded in the discovery cohort.
This observational design cannot establish causality or conserved regulation.
Clinical utility, calibration, and subgroup stability require further study.
- manuscript / Methods: replace
  - Before: We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.

Cells were treated as independent biological replicates in the t-test.
We used the same genes to construct the signature and validate the signature.
Nominal p-values below 0.05 were declared significant across 20,000 genes.
  - After: We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.

We aggregated counts into donor-level pseudobulk for differential expression.
Independent marker genes were used for signature validation.
P-values were adjusted with the Benjamini-Hochberg false discovery rate procedure.
Random seed 42 was used for splitting and model fitting.
The analysis used Python version 3.11 and a pinned requirements.txt.
- manuscript / Results: replace
  - Before: Our model predicts response with AUROC 0.98 (Figure 1).
The signature separates responders from nonresponders with p-value 0.001 (Table 1).
Our results prove a causal mechanism of resistance based on the observational association.
  - After: Our model predicts response with AUROC 0.72 and a 95% confidence interval of 0.55 to 0.86 (Figure 1).
The signature separates responders from nonresponders with an adjusted p-value of 0.04 (Table 1).
Our results suggest an association with resistance based on the observational association.
Sensitivity analyses used alternative preprocessing and alternative annotations.
A clinical-only baseline model reached AUROC 0.69.

## Claims strengthened in wording

None detected.


## Claims weakened in wording

- Matched claim has more qualified wording.
  - Before: We present the first-ever framework for a universal cancer response biomarker.
  - After: We present a framework for a cancer response biomarker in the studied population.
  - Source: manuscript; Abstract; line 5; block manuscript-48a71d89af2c-1
  - Source: manuscript; Abstract; line 5; block manuscript-93de9f537e1c-1
- Matched claim has more qualified wording.
  - Before: Our results prove a causal mechanism of treatment resistance across tissues.
  - After: Our results suggest an association with treatment resistance across tissues.
  - Source: manuscript; Abstract; line 6; block manuscript-48a71d89af2c-1
  - Source: manuscript; Abstract; line 6; block manuscript-93de9f537e1c-1
- Matched claim has more qualified wording.
  - Before: Our results prove a causal mechanism of resistance based on the observational association.
  - After: Our results suggest an association with resistance based on the observational association.
  - Source: manuscript; Results; line 32; block manuscript-7c9f0797fde7-1
  - Source: manuscript; Results; line 35; block manuscript-7e7ce94cfc8d-1

## Reporting concerns with new affirmative cues

- check.batch_platform: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1
- check.code_availability: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Availability; line 57; block manuscript-d12ce0d980c9-1
- check.data_availability: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Availability; line 58; block manuscript-d12ce0d980c9-1
- check.external_validation: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 23; block manuscript-2e5ecd201a97-1
  - Source: manuscript; Figure Legends; line 41; block manuscript-6c8685ac7be6-1
- check.multiple_testing: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 27; block manuscript-4d207a9e595d-1
  - Source: manuscript; Results; line 34; block manuscript-7e7ce94cfc8d-1
- check.pseudobulk: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
  - Source: manuscript; Methods; line 25; block manuscript-4d207a9e595d-1
  - Source: manuscript; Figure Legends; line 42; block manuscript-6c8685ac7be6-1
- check.annotation_robustness: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Results; line 36; block manuscript-7e7ce94cfc8d-1
- check.baseline_models: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Results; line 37; block manuscript-7e7ce94cfc8d-1
- check.confidence_intervals: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Results; line 33; block manuscript-7e7ce94cfc8d-1
- check.confounding: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1
- check.grouped_validation: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.limitations: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Limitations; line 52; block manuscript-f79ee62de01a-1
- check.random_seed: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 28; block manuscript-4d207a9e595d-1
- check.sensitivity: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Results; line 36; block manuscript-7e7ce94cfc8d-1
- check.software_versions: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Methods; line 29; block manuscript-4d207a9e595d-1
- check.treatment_interaction: a new affirmative reporting cue was found; adequacy is unverified.
  - Source: manuscript; Discussion; line 47; block manuscript-339b97a05091-1

## Explicit design concerns with candidate remediation

- pattern.cell_pseudoreplication: candidate corrective design is now described; execution and adequacy unverified.
  - Source: manuscript; Methods; line 25; block manuscript-4d207a9e595d-1
  - Source: manuscript; Figure Legends; line 42; block manuscript-6c8685ac7be6-1
- pattern.cohort_reuse: candidate corrective design is now described; execution and adequacy unverified.
  - Source: manuscript; Methods; line 23; block manuscript-2e5ecd201a97-1
  - Source: manuscript; Figure Legends; line 41; block manuscript-6c8685ac7be6-1
- pattern.feature_selection_before_split: candidate corrective design is now described; execution and adequacy unverified.
  - Source: manuscript; Methods; line 21; block manuscript-2e5ecd201a97-1
- pattern.test_set_tuning: candidate corrective design is now described; execution and adequacy unverified.
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
  - Source: manuscript; Methods; line 22; block manuscript-2e5ecd201a97-1
- pattern.circular_signature: candidate corrective design is now described; execution and adequacy unverified.
  - Source: manuscript; Methods; line 26; block manuscript-4d207a9e595d-1

## Concerns still detected

- check.censoring: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.clinical_use: still detected; compare individual passages.
  - Source: manuscript; Discussion; line 46; block manuscript-339b97a05091-1
- check.cutoff: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.endpoint: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- pattern.design_confounding: still detected; compare individual passages.
  - Source: manuscript; Methods; line 18; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Limitations; line 51; block manuscript-f79ee62de01a-1
- check.ambient_rna: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.ascertainment: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.calibration: still detected; compare individual passages.
  - Source: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1
- check.clinical_utility: still detected; compare individual passages.
  - Source: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1
- check.cluster_stability: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.composition: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.donor_cell_balance: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.doublets: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.integration: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.metric_context: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.missingness: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.null_models: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.prevalence_shift: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1
- check.subgroups: still detected; compare individual passages.
  - Source: manuscript; Limitations; line 53; block manuscript-f79ee62de01a-1
- check.thresholds: still detected; compare individual passages.
  - Source: manuscript; Methods; line 16; block manuscript-dc3b7f1eb694-1
  - Source: manuscript; Methods; line 20; block manuscript-2e5ecd201a97-1

## Newly detected concerns

None detected.


## Concerns no longer detected without resolution evidence

- pattern.causal_overclaim: no longer detected; resolution is not established.
- pattern.conservation_overclaim: no longer detected; resolution is not established.
- pattern.novelty_overclaim: no longer detected; resolution is not established.

## Comparison limits

- Resolution refers to reporting cues only; no analysis execution or scientific correctness was verified.
- Disappearing findings can reflect removed text, changed vocabulary, or changed applicability.
- Claim-strength changes measure wording, not increased or decreased evidential support.
- Text matching may miss paraphrases, reorderings, or moved sections.
- Each rule aggregates a concern family; one repaired instance does not prove all instances are resolved.
