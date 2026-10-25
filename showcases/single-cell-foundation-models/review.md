# Single-cell foundation models: a review that narrows its own objections

## Review at a glance

**Assessment:** A useful, deliberately scoped benchmark. The main revision needs concern interpretation and reporting; the review does not establish that the benchmark is invalid. [SC-1](#sc-1) [SC-2](#sc-2) [SC-3](#sc-3)

**Main contribution:** Demonstrates why frozen single-cell models should be tested against practical, simpler alternatives. [SC-5](#sc-5)

**Focus on these first:**

1. Clarify what the comparison answers: practical performance, with different access to target data and batch labels. [SC-1](#sc-1)
2. Narrow the scaling claim: changing data size and tissue composition together cannot isolate a general data-volume limit. [SC-2](#sc-2)
3. Check the ASW explanation against the implemented normalization before changing any reported results. [SC-3](#sc-3)

**Best next step:** Align the comparison and scaling conclusions with the acknowledged design limits; start with wording before requesting new experiments. [SC-1](#sc-1) [SC-2](#sc-2)

*Scope: Published April 2025 article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and results were not independently checked; no independent human validation of this review.*

---

> Model-native scientific review with a separately executed offline CLI baseline. No provider panel was run. Not independently human-validated.

Source: [Zero-shot evaluation reveals limitations of single-cell foundation models](https://pmc.ncbi.nlm.nih.gov/articles/PMC12007350/). Kasia Z Kedzierska, Lorin Crawford, Ava P Amini, Alex X Lu. Published article, 18 April 2025.

The central contribution is a useful, explicitly scoped zero-shot benchmark. The strongest revision opportunities concern interpretation and reporting, not evidence that the benchmark is invalid. Preserve the practical comparison; distinguish it from controlled conclusions about pretraining or scaling. Three priorities survive the evidence challenge below, alongside two verification tasks and four rejected leads.

## Coverage

Read: abstract, article body, methods, figure captions, availability statements and supplement descriptions from the published April 2025 article. The actual offline CLI produced 32 leads from 80 source blocks. The scientific synthesis is one model-native review using multiple lenses, not six independent reviewers. Supplement files, figure images, raw data, code execution and published peer-review history were not inspected. Thus neither numerical results nor supplementary sensitivity analyses are independently verified.

All decisions below are model-native interpretations, including the decisions to dismiss a concern. Exact source-span checks do not verify those interpretations. Engine dispositions remain unchanged in [baseline.json](baseline.json).

## Revision priorities

<a id="sc-1"></a>

### SC-1 — Keep practical utility separate from a controlled test of pretraining

**Decision: narrow.** Comparing frozen foundation models with target-trained, batch-aware scVI and Harmony answers a practical deployment question. It does not isolate architecture or pretraining quality under matched adaptation and information. The defensible request is to maintain that distinction wherever results are generalized, not to remove the baselines.

**Evidence:** [SC-A1](#sc-a1).

**Counterevidence / scope:** The authors explicitly explain the asymmetry and motivate it by available compute. Their conclusions also restrict coverage to selected models and tasks. This substantially answers an initial fairness objection. [SC-A2](#sc-a2) [SC-A18](#sc-a18)

**Next step:** Add a compact comparison table showing target-data fitting, batch-label access, feature selection and computational budget for each method. Only if claiming controlled architectural superiority, add an information- and adaptation-matched comparison; that is additional analysis, not a prerequisite for the practical benchmark.

**What would change this decision:** If every headline and interpretation is already restricted to this practical estimand, close this as a presentation check without demanding new experiments.

**Origin:** model-native. **Related engine leads:** `check.batch_platform`.

<a id="sc-2"></a>

### SC-2 — Do not turn confounded model variants into a scaling limit

**Decision: narrow.** The statement about a limit beyond which more data may not help is stronger than a comparison in which data size and tissue composition change together. The observation supports non-monotonic performance among the tested checkpoints; it does not locate a general scaling threshold.

**Evidence:** [SC-A4](#sc-a4).

**Counterevidence / scope:** The paper directly acknowledges the size/composition confound and notes that the larger human collection contains the smaller tissue collections. That makes this a wording issue with a known limitation, not a newly discovered design failure. [SC-A3](#sc-a3)

**Next step:** Describe performance of the tested variants without inferring a data-volume ceiling. To investigate a scaling law later, hold tissue mixture, training recipe and evaluation datasets fixed while varying pretraining size and seeds; those models may need new training.

**What would change this decision:** A controlled scaling experiment showing the same plateau would support a stronger claim. Narrow wording alone resolves the current interpretation concern.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

<a id="sc-3"></a>

### SC-3 — Check the direction of the ASW explanation

**Decision: retain.** The biological-preservation paragraph describes normalized zero as strong within-cluster cohesion, then says higher ASW means better separation. That presentation is internally confusing for readers interpreting model rankings. It warrants a reporting correction, not an allegation that the implementation or rankings are wrong.

**Evidence:** [SC-A5](#sc-a5).

**Counterevidence / scope:** The same paragraph clearly gives the intended higher-is-better direction. A prose error could leave every computed result unchanged. [SC-A6](#sc-a6)

**Next step:** Verify the actual scib transformation and the negative, zero and positive raw-silhouette cases against the archived implementation; correct the explanation to match it. Inspect code before deciding whether any figure needs recomputation.

**What would change this decision:** An explicitly documented alternative normalization consistent with both prose and implementation would remove the concern; a prose-only correction should not be treated as changed scientific results.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Verify before escalating

<a id="sc-4"></a>

### SC-4 — Inspect masked reconstruction sensitivity before escalating

**Decision: verify.** An all-unmasked reconstruction diagnostic differs from the corrupted-input task used during pretraining. Poor performance in that diagnostic alone does not establish that a model failed to learn its training objective. This is an unresolved interpretation check, not a confirmed flaw.

**Evidence:** [SC-A7](#sc-a7).

**Counterevidence / scope:** The supplement description explicitly reports Geneformer results across masking fractions. Those figures were not opened here; claiming that masking sensitivity is absent would be wrong. [SC-A8](#sc-a8)

**Next step:** First inspect Supplementary Figures S8–S9 and the code. Check masking ratio, which tokens are scored, and whether the naive comparator uses the same information. Only if not covered, propose matched-corruption evaluation for each model and dataset, reporting repeated-mask uncertainty.

**What would change this decision:** Equivalent conclusions under the training-like corruption and scoring protocol would substantially weaken this concern.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

<a id="sc-9"></a>

### SC-9 — Keep unretrieved methods details in a verification queue

**Decision: verify.** Donor composition, preprocessing, random seeds, uncertainty and robustness require checking the supplementary tables and archived code. Their absence from a particular text cue is not proof they were omitted from the study. Descriptive benchmark variability should not automatically be turned into a missing-significance-test complaint.

**Evidence:** [SC-A17](#sc-a17).

**Counterevidence / scope:** Supplement descriptions report subsampling, and an executable environment is announced. Neither was tested here. [SC-A16](#sc-a16)

**Next step:** Inspect Tables S1–S7 and the archived environment first. Record donor/dataset units, seeds and whether resampling captures donor or only cell variability. Escalate only a specific unresolved requirement relevant to the claimed generalization.

**What would change this decision:** Locating the relevant settings or showing that an inferential claim is not made closes the corresponding lead; reproducibility failure would warrant a specific issue.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Strengths worth preserving

<a id="sc-5"></a>

### SC-5 — Preserve the benchmark’s useful control structure

**Decision: strength.** Simple baselines, a random-initialization comparison and evaluation of both cell separation and integration make the benchmark informative for practical tool choice. The manuscript also exposes important limits rather than hiding them.

**Evidence:** [SC-A15](#sc-a15), [SC-A19](#sc-a19).

**Counterevidence / scope:** This supports the value of the experimental question and reported comparisons. It does not independently validate numerical results, generalize to later model versions, or establish clinical usefulness. [SC-A18](#sc-a18)

**Next step:** Keep the scoped takeaway and report per-dataset results alongside aggregate rankings.

**What would change this decision:** A code or data audit finding materially different computations could change this assessment; none was performed here.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Concerns that did not survive checking

<a id="sc-6"></a>

### SC-6 — Dismiss the apparent code-availability contradiction

**Decision: dismiss.** The engine combined a statement about other methods not releasing pretraining code with this paper’s own code-release statement. These have different subjects. The resulting contradiction is a contextual false positive.

**Evidence:** [SC-A12](#sc-a12).

**Counterevidence / scope:** The paper explicitly provides its own analysis repository and archived software environment. [SC-A11](#sc-a11) [SC-A16](#sc-a16)

**Next step:** Close the contradiction lead. Repository accessibility and executable reproduction remain separate checks.

**What would change this decision:** Evidence that the cited release lacks the actual analyses would justify a new, more specific reproducibility concern.

**Origin:** model-native. **Related engine leads:** `check.code_availability`.

<a id="sc-7"></a>

### SC-7 — Dismiss undisclosed pretraining overlap as a headline criticism

**Decision: dismiss.** Overlap is explicitly disclosed, and a non-overlapping Pancreas analysis is described. A review should not present this as hidden leakage or claim no sensitivity analysis exists.

**Evidence:** [SC-A10](#sc-a10), [SC-A9](#sc-a9).

**Counterevidence / scope:** The authors still acknowledge that the batch-integration advantage on some scGPT datasets cannot be disentangled from exposure. Disclosure limits the claim; it does not make all results an unseen-data benchmark. [SC-A20](#sc-a20)

**Next step:** Retain the authors’ exposure caveat and check the supplementary per-dataset results before making any generalization claim.

**What would change this decision:** A headline asserting uniformly unseen evaluation, or a mismatch between the reported subset and actual inputs, would reopen a narrower concern.

**Origin:** model-native. **Related engine leads:** `check.external_validation`, `check.train_test_split`.

<a id="sc-8"></a>

### SC-8 — Dismiss perturbation-screen requirements for an embedding benchmark

**Decision: dismiss.** The paper evaluates pretrained embeddings and reconstruction. Its discussion of future perturbation experiments does not make this study a CRISPR screen requiring guides, MOI, perturbation efficiency or toxicity controls. Donor-level differential-expression rules likewise do not automatically apply to descriptive embedding comparisons.

**Evidence:** [SC-A13](#sc-a13).

**Counterevidence / scope:** The experimental-validation passage is expressly a future-research suggestion. [SC-A14](#sc-a14)

**Next step:** Mark these leads out of scope for the reported study. Revisit design-specific checks if a later manuscript actually reports those experiments.

**What would change this decision:** A newly supplied experimental screen or inferential differential-expression analysis would change applicability.

**Origin:** model-native. **Related engine leads:** `check.guides`, `check.moi`, `check.pseudobulk`.

<a id="sc-10"></a>

### SC-10 — Dismiss the missing-baseline cue

**Decision: dismiss.** The engine did not recognize an explicitly described set of baselines. HVG, scVI, Harmony and a randomly initialized scGPT comparison are present; a generic missing-baseline allegation would be misleading.

**Evidence:** [SC-A15](#sc-a15), [SC-A19](#sc-a19).

**Counterevidence / scope:** The fairness and scope of the comparisons remain distinct questions handled in SC-1. [SC-A2](#sc-a2)

**Next step:** Close the missing-baseline and generic absent-null-control leads. Preserve any specifically motivated new comparator as optional strengthening.

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
