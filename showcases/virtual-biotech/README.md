# Showcase: Virtual Biotech

**A strong review asks what each evidence step actually establishes.**

Zhang et al., [*The Virtual Biotech: A multi-agent AI framework for therapeutic
discovery and development*](https://doi.org/10.64898/2026.02.23.707551), bioRxiv
**23 February 2026, v1**. This review is not an assessment of the
[later Science article](https://doi.org/10.1126/science.aeg6779).

The preprint integrates trial annotations, transcriptomic analyses and therapeutic
hypotheses through a team of agents. MAR's offline run produced 30 leads. A
separate model-native synthesis examines the reach of the conclusions and
explicitly credits the manuscript's safeguards.

| Proposed concern | After checking the manuscript |
| --- | --- |
| Spatial association establishes B7-H3 mechanism | Retain the inference boundary; tissue context adds evidence but does not substitute for intervention. |
| OSMR predicts benefit from vixarelimab | Preserve this as a hypothesis. Nonresponse to other therapies does not establish treatment-specific benefit. |
| Many trials guarantee independent evidence | Verify drug/target/program dependence before interpreting precision or prospective generalization. |
| A reviewer agent guarantees better scientific judgments | The critique-to-spatial-analysis handoff is useful; comparative quality needs controlled evaluation. |
| Donor-aware methods are missing | Dismiss the blanket allegation: donor aggregation and patient/sample effects are described. |
| “First trained” is a novelty overclaim | Dismiss: this is an ordering word in the methods, a clear heuristic false positive. |

Read the **[full review and evidence ledger](review.md)** for eleven review items,
including strengths and rejected leads, plus the complete triage of all 30
engine leads. The [structured review](review.json) retains the exact evidence
spans and counterevidence links.

```bash
python scripts/showcases.py virtual-biotech --download
```

Run from the repository root after installation. See the [reproduction guide](../README.md).

**Coverage:** main text, Extended Methods, captions and availability; no supplementary
PDF, figure-image review, data reanalysis or code execution. No provider panel or
independent human validation was performed. All scientific judgments are
model-native commentary. These observations must not be transferred to a later
manuscript version without checking what changed.

[Offline baseline](baseline.json) · [Pinned source and license](source.json) ·
[Actual run receipt](provenance.json)
