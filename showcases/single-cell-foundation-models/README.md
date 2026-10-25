# Showcase: single-cell foundation models

Kedzierska et al., [*Zero-shot evaluation reveals limitations of single-cell
foundation models*](https://doi.org/10.1186/s13059-025-03574-x), Genome Biology,
18 April 2025. This case uses the published article, with its limits and
counterarguments intact.

<!-- mar:summary:start -->

## Review at a glance

**Assessment:** A useful, deliberately scoped benchmark. The main revision needs concern interpretation and reporting; the review does not establish that the benchmark is invalid. [SC-1](review.md#sc-1) [SC-2](review.md#sc-2) [SC-3](review.md#sc-3)

**Main contribution:** Demonstrates why frozen single-cell models should be tested against practical, simpler alternatives. [SC-5](review.md#sc-5)

**Focus on these first:**

1. Clarify what the comparison answers: practical performance, with different access to target data and batch labels. [SC-1](review.md#sc-1)
2. Narrow the scaling claim: changing data size and tissue composition together cannot isolate a general data-volume limit. [SC-2](review.md#sc-2)
3. Check the ASW explanation against the implemented normalization before changing any reported results. [SC-3](review.md#sc-3)

**Best next step:** Align the comparison and scaling conclusions with the acknowledged design limits; start with wording before requesting new experiments. [SC-1](review.md#sc-1) [SC-2](review.md#sc-2)

*Scope: Published April 2025 article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and results were not independently checked; no independent human validation of this review.*

<!-- mar:summary:end -->

Read the **[full review and evidence ledger](review.md)** for the reasoning behind
each recommendation, counterevidence and exact source locations.

## Behind the summary

The paper compares frozen Geneformer/scGPT representations with practical
alternatives. MAR's offline run produced 32 reporting/design leads. A separate
model-native evidence challenge turns these into three bounded revision
priorities, two verification tasks, one strength and four rejected concerns.

| Proposed concern | After checking the manuscript |
| --- | --- |
| Target-trained baselines make the comparison unfair | The authors explain this design. Preserve the practical benchmark; limit any controlled claim about pretraining. |
| Larger pretraining sets stop helping beyond a limit | Narrow this interpretation: size and tissue composition vary together, as the authors acknowledge. |
| ASW explanation is confusing | Retain a small reporting check; verify the normalization before alleging a computational error. |
| The paper contradicts itself about code availability | Dismiss: the negative statement is about other methods, not this paper's released analysis. |
| Pretraining overlap is hidden | Dismiss that allegation: overlap and a non-overlapping sensitivity analysis are reported. |

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
