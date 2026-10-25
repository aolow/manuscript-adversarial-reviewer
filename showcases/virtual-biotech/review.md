# Virtual Biotech: trace the claim from association to proposed intervention

> Model-native scientific review with a separately executed offline CLI baseline. No provider panel was run. Not independently human-validated.

Source: [The Virtual Biotech: A Multi-Agent AI Framework for Therapeutic Discovery and Development](https://pmc.ncbi.nlm.nih.gov/articles/PMC12970349/). Harrison G. Zhang, Peter Eckmann, Jiacheng Miao, Andrew B. Mahon, James Zou. bioRxiv preprint v1, 23 February 2026; PMC12970349.1.

The preprint demonstrates a substantial computational workflow and useful hypothesis generation. Four priorities concern the reach of its conclusions: mechanistic language, treatment-selection claims, dependence in trial-level evidence, and comparative claims about agent quality. The review also credits safeguards that the manuscript already implements. This is a review of the February preprint only, not of the later Science article.

## Coverage

Read: abstract, main text, Extended Methods, five figure captions and data availability in the 23 February 2026 preprint v1 (PMC12970349.1). The offline CLI produced 30 leads from 150 source blocks. One model-native synthesis followed the MAR evidence-challenge checklist; no provider panel or independent expert assessment was run. Supplementary PDF, figure images, execution logs, source code and raw datasets were not inspected. The September 2026 Science version is outside this review.

All decisions below are model-native interpretations, including the decisions to dismiss a concern. Exact source-span checks do not verify those interpretations. Engine dispositions remain unchanged in [baseline.json](baseline.json).

## Revision priorities

### VB-1 — Keep spatial association separate from B7-H3 mechanism

**Decision: retain.** The spatial analysis adds useful tissue-context evidence, but expression, inferred neighboring cell abundance and observational survival associations do not establish that perturbing B7-H3 causes immune exclusion or reverses it. The phrase “functional evidence” risks overstating what these measurements demonstrate.

**Evidence:** [VB-A1](#vb-a1).

**Counterevidence / scope:** The methods exclude B7-H3 from deconvolution and adjust for spatial composition and sample effects. These directly answer a simplistic circularity or no-sample-adjustment objection. The discussion also labels the case studies as hypotheses requiring validation. [VB-A2](#vb-a2) [VB-A3](#vb-a3) [VB-A4](#vb-a4)

**Next step:** First align the mechanistic wording with the observational evidence. If a causal claim is essential, propose a new intervention study: perturb B7-H3 in matched fibroblast–immune–tumor systems across independent donors, compare with appropriate controls and measure immune exclusion or function while checking viability. No such experimental result is established by this review.

**What would change this decision:** Replicated intervention evidence separating B7-H3 activity from correlated fibroblast state would support stronger mechanistic language. An expression association alone would not.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

### VB-2 — Treat OSMR enrichment as a testable trial-design hypothesis

**Decision: narrow.** Baseline OSMR associations with nonresponse to other biologics do not identify a subgroup with greater benefit from vixarelimab. Nor do they establish the reason MOONGLOW stopped. The proposal is scientifically interesting, but predictive treatment benefit and a retrospective failure explanation remain untested.

**Evidence:** [VB-A5](#vb-a5), [VB-A6](#vb-a6).

**Counterevidence / scope:** The authors use conditional language, explicitly call the case studies hypotheses, and identify assay/cutoff decisions still to be made. The proper review action is to preserve that boundary, not accuse the paper of claiming a validated clinical test. [VB-A4](#vb-a4) [VB-A7](#vb-a7)

**Next step:** Check whether baseline biopsies, treatment assignments and outcomes from MOONGLOW are available. If so, estimate an exploratory randomized treatment-by-biomarker interaction with uncertainty; that cannot retrospectively validate a selected cutoff. A prespecified assay, cutoff and independent prospective evaluation are needed before adopting enrichment as a validated selection strategy.

**What would change this decision:** Treatment-interaction evidence replicated in an independent cohort could justify predictive language. General association with disease severity or other-therapy nonresponse would not.

**Origin:** model-native. **Related engine leads:** `check.treatment_interaction`, `check.clinical_utility`, `check.clinical_use`.

### VB-4 — Bound claims about comparative quality and objectivity

**Decision: narrow.** Illustrative case studies, API expenditure and parallel throughput establish feasibility. They do not by themselves measure superiority to human teams or the incremental scientific benefit of a reviewer agent. Avoid reading inexpensive execution as a validated gain in correctness, unbiased judgment or total project cost.

**Evidence:** [VB-A11](#vb-a11), [VB-A12](#vb-a12).

**Counterevidence / scope:** The workflow is inspectable and the authors explicitly acknowledge propagated agent errors. Those are meaningful strengths, but not a matched comparison or ablation. [VB-A13](#vb-a13) [VB-A14](#vb-a14)

**Next step:** Narrow unqualified comparative language. To evaluate the architecture, use the same held-out questions, information access and budget across full workflow, no-reviewer and simpler-agent conditions, with blinded expert scoring of correct conclusions, unsupported claims, missing key evidence, time and total cost. This is a proposed validation study, not work performed for this showcase.

**What would change this decision:** A controlled assessment showing repeatable quality gains would support a stronger claim about the reviewer loop. Reported case costs alone would not.

**Origin:** model-native. **Related engine leads:** `check.baseline_models`.

## Verify before escalating

### VB-3 — Verify the independent unit behind trial-level precision

**Decision: verify.** Molecular features are shared across trials testing related drugs or targets. The reported random effects describe modality and disease-area combinations; they do not by themselves establish that dependence from repeated drugs, targets or development programs is handled. Shuffling individual outcomes also does not necessarily preserve that dependence. This is a question about uncertainty and generalization, not proof that the associations disappear.

**Evidence:** [VB-A8](#vb-a8), [VB-A10](#vb-a10).

**Counterevidence / scope:** The manuscript includes adjusted mixed models, genetic-evidence adjustment, multiplicity control and an explicit observational limitation. Saying “no confounder adjustment” would ignore these safeguards. [VB-A9](#vb-a9) [VB-A26](#vb-a26)

**Next step:** Inspect the trial–drug–target mapping and scripts; report unique clusters and overlap first. If repeated-program dependence remains, compare the main intervals with an appropriate drug/program/target-aware resampling or variance model, specifying treatment of multi-target overlap. For prospective prediction claims, add a time- and group-held-out evaluation. Required mappings and code were not audited here.

**What would change this decision:** Existing adequate dependence handling in code, or stable effect sizes and uncertainty under the appropriate grouped analysis, would close or narrow this concern.

**Origin:** model-native. **Related engine leads:** `check.external_validation`, `check.train_test_split`.

### VB-9 — Verify reproducibility and annotation error without inventing absence

**Decision: verify.** The source describes downloadable code/reports and human checks, but this review did not execute a pinned release or inspect the full supplementary protocol. Reported agreement on a reviewed subset is not universal annotation accuracy or proof that residual errors cannot affect downstream associations.

**Evidence:** [VB-A20](#vb-a20), [VB-A21](#vb-a21), [VB-A22](#vb-a22).

**Counterevidence / scope:** The article actually includes two human annotators and a separate comparison with the TDC dataset. A claim that there was no human validation would be false; the question is its scope and error consequences. [VB-A21](#vb-a21)

**Next step:** Locate the exact code/data release and supplementary annotation rules; inspect missingness, disagreement strata, seeds, assay/threshold sensitivity and versioned tool inputs. Recompute key results under plausible annotation-error sensitivity. Keep uninspected details in a verification queue rather than treating them as established missing methods.

**What would change this decision:** A reproducible release plus an adequate error/missingness sensitivity analysis could close these checks. A confirmed execution or annotation failure would justify a narrower issue.

**Origin:** model-native. **Related engine leads:** `check.code_availability`, `check.missingness`.

## Strengths worth preserving

### VB-5 — Preserve the concrete critique-to-analysis handoff

**Decision: strength.** A reviewer identifies the loss of spatial context, and the workflow responds with a spatial analysis instead of merely rephrasing its answer. That is a useful operational pattern for MAR: attach a critique to a discriminating next check and re-evaluate the claim afterward.

**Evidence:** [VB-A14](#vb-a14), [VB-A15](#vb-a15).

**Counterevidence / scope:** Spatial triangulation still shares modeling assumptions and is observational. The case demonstrates the pattern, not a measured improvement in scientific review accuracy. [VB-A4](#vb-a4)

**Next step:** Keep the evidence challenge in the final review and measure its contribution in a future blinded evaluation.

**What would change this decision:** If logs showed that the follow-up was unrelated to the critique, the claimed workflow example would weaken; execution logs were not audited.

**Origin:** model-native. **Related engine leads:** none; not an engine-generated finding.

## Concerns that did not survive checking

### VB-6 — Dismiss a blanket donor-unaware inference complaint

**Decision: dismiss.** The generic pseudobulk contradiction mixes descriptions of different analyses. The methods explicitly aggregate counts by donor and cell type, use patient effects for longitudinal UC data, and include a sample intercept for spatial data. A blanket absence-of-donor-control criticism is unsupported.

**Evidence:** [VB-A16](#vb-a16), [VB-A17](#vb-a17).

**Counterevidence / scope:** These safeguards do not resolve every possible dependence problem; trial reuse and within-slide spatial autocorrelation are distinct checks. [VB-A3](#vb-a3)

**Next step:** Close the blanket contradiction. Audit a specific model and its biological unit before raising a new pseudoreplication concern.

**What would change this decision:** A mismatch between the described and executed analysis could justify a specific issue.

**Origin:** model-native. **Related engine leads:** `check.pseudobulk`.

### VB-7 — Dismiss “first trained” as an absolute-novelty claim

**Decision: dismiss.** The deterministic pattern matched an ordering word in a methods description. It describes the first stage of model fitting, not the first-ever scientific achievement. This is a contextual false positive.

**Evidence:** [VB-A18](#vb-a18).

**Counterevidence / scope:** The surrounding paragraph describes reference fitting followed by spatial mapping; there is no novelty assertion in this evidence span. [VB-A2](#vb-a2)

**Next step:** Discard this particular novelty lead. Any actual priority or originality claim needs a separate literature check.

**What would change this decision:** A different passage making an explicit first-ever claim would need its own evidence and review.

**Origin:** model-native. **Related engine leads:** `pattern.novelty_overclaim`.

### VB-8 — Separate reported thresholds and endpoints from proposed ones

**Decision: dismiss.** A tau threshold and within-sample spatial quartiles are reported. Trial endpoint failures and successes refer to different studies and are not a contradiction. The future OSMR enrollment cutoff remains to be developed; that is a different object from the existing analytical thresholds.

**Evidence:** [VB-A19](#vb-a19), [VB-A25](#vb-a25), [VB-A24](#vb-a24).

**Counterevidence / scope:** Reported threshold selection is not the same as demonstrating robustness to that threshold. Multi-arm trial annotation can also remain ambiguous despite a clear ontology. [VB-A7](#vb-a7)

**Next step:** Close the generic missing-cutoff and contradictory-endpoint accusations. Keep sensitivity or annotation questions specific to the relevant analysis.

**What would change this decision:** An inconsistent definition for the same outcome or an unreported threshold used in a main analysis would reopen a specific reporting concern.

**Origin:** model-native. **Related engine leads:** `check.cutoff`, `check.endpoint`.

### VB-10 — Dismiss requirements for an original perturbation screen

**Decision: dismiss.** Reusing Tahoe perturbation profiles and describing tool capabilities does not mean this manuscript performed a new pooled screen. Guide, MOI and perturbation-efficiency requirements cannot be inferred from those keywords alone.

**Evidence:** [VB-A23](#vb-a23).

**Counterevidence / scope:** Dataset provenance and the validity of the reused signatures remain relevant, but must be checked against the original data and the actual analysis. [VB-A23](#vb-a23)

**Next step:** Mark original-screen reporting leads out of scope; route provenance checks to the source dataset and released analysis.

**What would change this decision:** If a new original screen were supplied, the corresponding experimental controls would become applicable.

**Origin:** model-native. **Related engine leads:** `check.guides`, `check.moi`.

### VB-11 — Recognize batch handling without assuming it eliminates confounding

**Decision: dismiss.** Harmony preprocessing and covariate-adjusted models are described. A generic no-batch-handling lead misses that context. Whether correction is adequate for a specific inference still requires inspecting the data and design.

**Evidence:** [VB-A27](#vb-a27).

**Counterevidence / scope:** The authors acknowledge residual confounding in observational trial analysis; a named correction method is not a universal guarantee. [VB-A26](#vb-a26)

**Next step:** Close the reporting-absence allegation and examine an actual residual-confounding contrast if needed.

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
