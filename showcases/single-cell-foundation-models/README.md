# Showcase: single-cell foundation models

**A useful adversarial review knows when to withdraw an objection.**

Kedzierska et al., [*Zero-shot evaluation reveals limitations of single-cell
foundation models*](https://doi.org/10.1186/s13059-025-03574-x), Genome Biology,
18 April 2025. This case uses the published article, with its limits and
counterarguments intact.

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

Read the **[full review and evidence ledger](review.md)** for the counterarguments,
specific next checks and complete triage of all 32 leads. The [structured
review](review.json) links exact source spans to MAR block IDs.

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
