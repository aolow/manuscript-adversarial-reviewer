# Showcase: single-cell foundation models

Kedzierska et al., [*Zero-shot evaluation reveals limitations of single-cell
foundation models*](https://doi.org/10.1186/s13059-025-03574-x), Genome Biology,
18 April 2025. This case reviews the published article.

<!-- mar:summary:start -->

## Review at a glance

**Assessment:** The benchmark compares frozen single-cell models with methods fitted to the evaluation data. This design assesses practical performance; it does not isolate the effects of architecture or pretraining size. [SC-1](review.md#sc-1) [SC-2](review.md#sc-2)

**Main contribution:** Includes simple baselines and a randomly initialized model, with tests of cell separation and batch integration. [SC-5](review.md#sc-5)

**Review priorities:**

1. State which methods use evaluation data for fitting and which use batch labels when interpreting performance differences. [SC-1](review.md#sc-1)
2. Limit the scaling conclusion to the tested models: pretraining size and tissue composition vary together. [SC-2](review.md#sc-2)
3. Check the average silhouette width (ASW) description against the implemented normalization. [SC-3](review.md#sc-3)

**Next step:** Revise the comparison and scaling conclusions to match the stated design limits. These wording changes do not require new experiments. [SC-1](review.md#sc-1) [SC-2](review.md#sc-2)

*Scope: Published April 2025 article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and results were not independently checked; no independent human validation of this review.*

<!-- mar:summary:end -->

Read the **[full review and evidence ledger](review.md)** for the reasoning behind
each recommendation, counterevidence and exact source locations.

## Behind the summary

The paper compares frozen Geneformer/scGPT representations with practical
alternatives. MAR's offline run produced 32 reporting/design leads. A separate
model-native review identifies three revision
priorities, two verification tasks, one strength and four rejected concerns.

| Review question | Assessment after source checking |
| --- | --- |
| What does the model comparison estimate? | Practical performance under different fitting conditions. The authors explain those differences. [SC-1](review.md#sc-1) |
| Does performance identify a limit to pretraining size? | Size and tissue composition vary together, so the comparison does not isolate a size effect. [SC-2](review.md#sc-2) |
| Is the ASW description consistent? | Check the normalization against the code before deciding whether any result changes. [SC-3](review.md#sc-3) |
| Do the code-availability statements conflict? | They refer to different studies. The paper reports its own analysis release. [SC-6](review.md#sc-6) |
| Is pretraining overlap disclosed? | Overlap and a sensitivity analysis without overlap are reported. [SC-7](review.md#sc-7) |

The [structured review](review.json) retains the complete triage of all 32 leads
and links exact source spans to MAR block IDs.

## Reproduce this showcase

```bash
python scripts/showcases.py single-cell-foundation-models --download
```

Run from the repository root after installation. See the [reproduction guide](../README.md)
for the exact scope, local outputs and verification process.

**Coverage:** text, methods and captions; supplement descriptions only. Numerical
results, figure images, supplements, analysis code and review history were not
independently inspected. No provider panel or independent human validation was
performed. The final scientific judgments are model-native commentary, not
accepted CLI findings.

[Offline baseline](baseline.json) · [Pinned source and license](source.json) ·
[Actual run receipt](provenance.json)
