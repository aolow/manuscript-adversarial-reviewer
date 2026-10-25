# Single-cell foundation models: a review that narrows its own objections

## Review at a glance

**Assessment:** The benchmark compares frozen single-cell models with methods fitted to the evaluation data. This design assesses practical performance; it does not isolate the effects of architecture or pretraining size. [SC-1](#sc-1) [SC-2](#sc-2)

**Main contribution:** Includes simple baselines and a randomly initialized model, with tests of cell separation and batch integration. [SC-5](#sc-5)

**Review priorities:**

1. State which methods use evaluation data for fitting and which use batch labels when interpreting performance differences. [SC-1](#sc-1)
2. Limit the scaling conclusion to the tested models: pretraining size and tissue composition vary together. [SC-2](#sc-2)
3. Check the average silhouette width (ASW) description against the implemented normalization. [SC-3](#sc-3)

**Next step:** Revise the comparison and scaling conclusions to match the stated design limits. These wording changes do not require new experiments. [SC-1](#sc-1) [SC-2](#sc-2)

*Scope: Published April 2025 article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and results were not independently checked; no independent human validation of this review.*

---

> Model-native scientific review with a separately executed offline CLI baseline. No provider panel was run. Not independently human-validated.

Source: [Zero-shot evaluation reveals limitations of single-cell foundation models](https://pmc.ncbi.nlm.nih.gov/articles/PMC12007350/). Kasia Z Kedzierska, Lorin Crawford, Ava P Amini, Alex X Lu. Published article, 18 April 2025.

The review identifies three revision priorities, two verification questions, one supported strength and four dismissed concerns. The priorities concern the scope of the model comparison, the interpretation of pretraining size, and the metric description. Each assessment below separates the reported evidence from its interpretation.

## Coverage

Read: abstract, article body, methods, figure captions, availability statements and supplement descriptions from the published April 2025 article. The actual offline CLI produced 32 leads from 80 source blocks. The scientific synthesis is one model-native review using multiple lenses, not six independent reviewers. Supplement files, figure images, raw data, code execution and published peer-review history were not inspected. Thus neither numerical results nor supplementary sensitivity analyses are independently verified.

All decisions below are model-native interpretations, including the decisions to dismiss a concern. Exact source-span checks do not verify those interpretations. Engine dispositions remain unchanged in [baseline.json](baseline.json).

## Revision priorities

<a id="sc-1"></a>

### SC-1 — Scope of the model comparison

**Decision: narrow.** The study compares frozen foundation models with scVI and Harmony fitted to the evaluation data using batch labels. This estimates practical performance under different fitting conditions; it does not isolate architecture or pretraining quality. [SC-A1](#sc-a1)

**Counterevidence / scope:** The authors explain these differences in terms of available computing resources and limit their conclusions to selected models and tasks. The review therefore narrows the concern to how the comparison is interpreted. [SC-A2](#sc-a2) [SC-A18](#sc-a18)

**Next step:** List target-data fitting, batch-label access, feature selection and computing budget for each method. A claim about architecture alone would require a comparison with matched information and adaptation; the practical benchmark does not require that additional analysis.

**What would change this decision:** Close this as a presentation check if all conclusions already describe performance under the tested conditions.

**Origin:** model-native. **Related engine leads:** `check.batch_platform`.

<a id="sc-2"></a>

### SC-2 — Pretraining size and tissue composition

**Decision: narrow.** Performance does not increase consistently across the tested model versions. Because pretraining size and tissue composition change together, this result does not identify a general limit beyond which more training data stops improving performance. [SC-A4](#sc-a4)

**Counterevidence / scope:** The paper acknowledges this confounding and states that the larger human collection includes the smaller tissue collections. The remaining concern is the scope of the scaling conclusion. [SC-A3](#sc-a3)

**Next step:** Describe the performance of the tested variants without inferring a data-volume limit. A later scaling study would need to hold tissue mixture, training procedure and evaluation datasets fixed while varying pretraining size and random seeds; this may require new model training.

**What would change this decision:** A controlled scaling experiment showing the same plateau would support a stronger claim. Narrow wording alone resolves the current interpretation concern.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

<a id="sc-3"></a>

### SC-3 — Direction of the ASW metric

**Decision: retain.** The biological-preservation paragraph describes normalized zero as strong within-cluster cohesion, then states that higher average silhouette width (ASW) indicates better separation. These descriptions need reconciliation before readers can interpret the rankings. [SC-A5](#sc-a5)

**Counterevidence / scope:** The paragraph states the intended higher-is-better direction. A wording error could leave the computed results unchanged. [SC-A6](#sc-a6)

**Next step:** Check the scib transformation and the negative, zero and positive raw-silhouette cases against the archived code. Correct the description to match the implementation; determine whether recomputation is needed only after that check.

**What would change this decision:** An explicitly documented alternative normalization consistent with both prose and implementation would remove the concern; a prose-only correction should not be treated as changed scientific results.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Open verification questions

<a id="sc-4"></a>

### SC-4 — Masked reconstruction sensitivity

**Decision: verify.** The reconstruction diagnostic supplies unmasked input, whereas pretraining uses corrupted input. Performance on the diagnostic alone does not establish whether a model learned its training objective. [SC-A7](#sc-a7)

**Counterevidence / scope:** The supplement description reports Geneformer results across masking fractions. Those figures were not inspected, so the adequacy of that sensitivity analysis remains unverified. [SC-A8](#sc-a8)

**Next step:** Inspect Supplementary Figures S8–S9 and the code for the masking ratio, scored tokens and information available to the simple comparator. If these do not address the question, evaluate matched masking and scoring conditions for each model and dataset, with uncertainty across repeated masks.

**What would change this decision:** Equivalent conclusions under the training-like corruption and scoring protocol would substantially weaken this concern.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

<a id="sc-9"></a>

### SC-9 — Methods details requiring supplementary material

**Decision: verify.** The supplement descriptions identify additional sampling and evaluation details. Donor composition, preprocessing, random seeds, uncertainty and robustness require inspection of those materials and the archived code; a text-search omission does not establish a missing method. [SC-A17](#sc-a17)

**Counterevidence / scope:** Subsampling is described and an executable environment is announced. Neither was checked here. [SC-A16](#sc-a16)

**Next step:** Inspect Tables S1–S7 and the archived environment. Record donor and dataset units, random seeds, and whether resampling measures donor or only cell variability. Raise a concern only if a requirement relevant to the stated conclusion remains unmet.

**What would change this decision:** Locating the relevant settings or showing that an inferential claim is not made closes the corresponding lead; reproducibility failure would warrant a specific issue.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Supported strengths

<a id="sc-5"></a>

### SC-5 — Baselines and reported evaluation scope

**Decision: strength.** The study includes simple baselines, a randomly initialized model, and tests of cell separation and batch integration. These comparisons provide context for interpreting the performance of pretrained models. [SC-A15](#sc-a15) [SC-A19](#sc-a19)

**Counterevidence / scope:** The authors limit coverage to selected models and tasks. The reported comparisons do not independently verify the numerical results or establish performance of later model versions. [SC-A18](#sc-a18)

**Next step:** Retain these comparisons and the stated scope; report results for each dataset alongside aggregate rankings.

**What would change this decision:** A code or data audit finding materially different computations could change this assessment; none was performed here.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Dismissed concerns

<a id="sc-6"></a>

### SC-6 — Code-availability statements refer to different studies

**Decision: dismiss.** The engine combined a statement about other methods lacking public pretraining code with this paper’s code-release statement. The statements refer to different studies and do not contradict each other. [SC-A12](#sc-a12)

**Counterevidence / scope:** The paper explicitly provides its own analysis repository and archived software environment. [SC-A11](#sc-a11) [SC-A16](#sc-a16)

**Next step:** Close the contradiction lead. Repository accessibility and executable reproduction remain separate checks.

**What would change this decision:** Evidence that the cited release lacks the actual analyses would justify a new, more specific reproducibility concern.

**Origin:** model-native. **Related engine leads:** `check.code_availability`.

<a id="sc-7"></a>

### SC-7 — Pretraining overlap is disclosed

**Decision: dismiss.** The paper discloses pretraining overlap and describes a Pancreas analysis without overlap. The evidence does not support a concern about undisclosed overlap or absent sensitivity analysis. [SC-A10](#sc-a10) [SC-A9](#sc-a9)

**Counterevidence / scope:** The authors acknowledge that some scGPT batch-integration advantages cannot be separated from prior exposure. Disclosure does not establish performance on unseen data for every comparison. [SC-A20](#sc-a20)

**Next step:** Retain the exposure limitation and inspect the supplementary results for each dataset before assessing generalization.

**What would change this decision:** A headline asserting uniformly unseen evaluation, or a mismatch between the reported subset and actual inputs, would reopen a narrower concern.

**Origin:** model-native. **Related engine leads:** `check.external_validation`, `check.train_test_split`.

<a id="sc-8"></a>

### SC-8 — Perturbation-screen checks are outside the study scope

**Decision: dismiss.** The study evaluates pretrained embeddings and reconstruction. It does not report a new CRISPR screen, so screen-specific control requirements do not apply to this benchmark. Donor-level differential-expression checks also require an applicable inferential analysis. [SC-A13](#sc-a13)

**Counterevidence / scope:** The experimental-validation passage proposes future research. [SC-A14](#sc-a14)

**Next step:** Mark these leads out of scope. Apply experiment-specific checks if a later manuscript reports those experiments.

**What would change this decision:** A newly supplied experimental screen or inferential differential-expression analysis would change applicability.

**Origin:** model-native. **Related engine leads:** `check.guides`, `check.moi`, `check.pseudobulk`.

<a id="sc-10"></a>

### SC-10 — Baseline comparisons are reported

**Decision: dismiss.** The paper includes highly variable gene (HVG), scVI and Harmony baselines, plus a randomly initialized scGPT comparison. The generic missing-baseline lead is unsupported. [SC-A15](#sc-a15) [SC-A19](#sc-a19)

**Counterevidence / scope:** Differences in fitting conditions remain a separate interpretation question in SC-1. [SC-A2](#sc-a2)

**Next step:** Close the missing-baseline and absent-random-control leads. Justify any additional comparator against the specific claim it would test.

**What would change this decision:** A necessary comparator for a stronger, different claim could reopen a narrowly specified request.

**Origin:** model-native. **Related engine leads:** `check.baseline_models`, `check.null_models`.

## Complete disposition of the offline leads

This is an annotated demonstration, not a measured false-positive rate. The following groups cover every engine lead exactly once; these are recommendations, not overrides of the original report.

- **Contextual false positive:** Different subjects were conflated in the code-availability check. Related review: SC-6. Leads: `check.code_availability`.

- **Explicitly reported:** Comparators and a random-initialization control are described. Related review: SC-10. Leads: `check.baseline_models`, `check.null_models`.

- **Already acknowledged; scope retained:** Pretraining overlap and the remaining exposure limitation are disclosed. Related review: SC-7. Leads: `check.external_validation`, `check.train_test_split`.

- **Narrowed interpretation check:** Batch information differs across approaches and is explicitly discussed. Related review: SC-1. Leads: `check.batch_platform`.

- **Out of scope:** No new CRISPR screen, differential-expression inference or deployed clinical classifier is evaluated here. Related review: SC-8, SC-5. Leads: `check.guides`, `check.perturbation_efficiency`, `check.screen_controls`, `check.toxicity`, `check.pseudobulk`, `check.multiple_testing`, `check.calibration`, `check.metric_context`, `check.moi`, `check.off_targets`, `check.perturbation_model`, `check.screen_quality`.

- **Verify in unreviewed materials or establish applicability:** Inspect supplement/code before treating these reporting cues as study defects; several are optional for a descriptive benchmark. Related review: SC-9. Leads: `check.biological_replicates`, `check.sample_sizes`, `check.ambient_rna`, `check.annotation_robustness`, `check.cluster_stability`, `check.composition`, `check.confidence_intervals`, `check.donor_cell_balance`, `check.doublets`, `check.grouped_validation`, `check.integration`, `check.random_seed`, `check.sensitivity`, `check.thresholds`.

## Evidence ledger

Short excerpts are attributed to the article above. Source IDs refer to the pinned JATS snapshot; `node-*` IDs are assigned by the converter. [review.json](review.json) retains MAR block IDs and exact character offsets. Reproduction downloads the full context locally for inspection.

### SC-A1

Source `Par29`: “which we trained on each individual dataset”

### SC-A2

Source `Par29`: “we reason this set-up reflects practical settings”

### SC-A3

Source `Par9`: “confounding if differences in performance are due to size or the composition of dataset”

### SC-A4

Source `Par10`: “beyond a certain limit, larger and more diverse datasets may no longer confer additional benefits”

### SC-A5

Source `Par33`: “0 signifies strong within-cluster cohesion”

### SC-A6

Source `Par33`: “Higher ASW indicates better performance in separating clusters”

### SC-A7

Source `Par35`: “we used all genes unmasked as input”

### SC-A8

Source `node-057`: “Fig. S8: Pearson’s correlation of input and Geneformer’s predicted expression rankings with respect to fraction of masked input tokens.”

### SC-A9

Source `Par31`: “We conducted evaluations using both the complete Pancreas dataset and its non-overlapping subset.”

### SC-A10

Source `Par22`: “some of our evaluation datasets were used in pretraining”

### SC-A11

Source `node-072`: “The code used in our analyses is available at https://github.com/microsoft/zero-shot-scfoundation”

### SC-A12

Source `Par21`: “methods do not make their pretraining code publicly available”

### SC-A13

Source `Par26`: “We evaluated two proposed foundation models for single-cell transcriptomics: Geneformer”

### SC-A14

Source `Par24`: “ideally should be paired with targeted in vitro lab experiments”

### SC-A15

Source `Par29`: “we compared Geneformer and scGPT against selecting highly variable genes”

### SC-A16

Source `node-072`: “we have published a docker image at DockerHub”

### SC-A17

Source `node-056`: “Table S1: Scores for cell embeddings generated by the models. Scores calculated based on the whole dataset, as well in 10 repeats of subsampled for 10% of the dataset.”

### SC-A18

Source `Par20`: “a limited array of datasets that do not exhaustively represent all applications of single-cell analysis”

### SC-A19

Source `Par9`: “randomly initialized scGPT”

### SC-A20

Source `Par12`: “we cannot disentangle if these improvements are potentially because these datasets were seen in pretraining”
