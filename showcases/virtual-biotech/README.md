# Showcase: Virtual Biotech

Zhang et al., [*The Virtual Biotech: A multi-agent AI framework for therapeutic
discovery and development*](https://doi.org/10.64898/2026.02.23.707551), bioRxiv
**23 February 2026, v1**. This review is not an assessment of the
[later Science article](https://doi.org/10.1126/science.aeg6779).

<!-- mar:summary:start -->

## Review at a glance

**Assessment:** The preprint reports computational case studies and observational associations. These generate therapeutic hypotheses; causal mechanisms and treatment-specific benefit remain untested. Trial-level uncertainty requires verification. [VB-1](review.md#vb-1) [VB-2](review.md#vb-2) [VB-3](review.md#vb-3)

**Main contribution:** Documents a reviewer critique followed by a spatial analysis addressing the missing tissue context. [VB-5](review.md#vb-5)

**Review priorities:**

1. Describe B7-H3 findings as spatial and survival associations. A causal mechanism requires intervention evidence. [VB-1](review.md#vb-1)
2. Keep enrollment based on oncostatin M receptor (OSMR) expression as a hypothesis: nonresponse to other therapies does not establish benefit from vixarelimab. [VB-2](review.md#vb-2)
3. Check whether uncertainty accounts for drugs, targets and development programs represented in multiple trials. [VB-3](review.md#vb-3)

**Next step:** Align the claims with the observational evidence, then inspect the trial–drug–target mapping to assess dependence. [VB-1](review.md#vb-1) [VB-3](review.md#vb-3)

*Scope: February 2026 preprint v1, not the later journal article. Offline CLI plus model-native synthesis; text, methods and captions reviewed. Supplements, code and data were not inspected; no independent human validation of this review.*

<!-- mar:summary:end -->

Read the **[full review and evidence ledger](review.md)** for the reasoning behind
each recommendation, counterevidence and exact source locations.

## Behind the summary

The preprint integrates trial annotations, transcriptomic analyses and therapeutic
hypotheses through a team of agents. MAR's offline run produced 30 leads. A
separate model-native review assesses the conclusions in the context of the
reported methods and limitations.

| Review question | Assessment after source checking |
| --- | --- |
| What do the B7-H3 associations establish? | Spatial and survival associations support an observational hypothesis; intervention evidence is needed for a causal conclusion. [VB-1](review.md#vb-1) |
| Does OSMR identify benefit from vixarelimab? | Nonresponse to other therapies does not establish treatment-specific benefit. [VB-2](review.md#vb-2) |
| How independent are the trials? | Check shared drugs, targets and programs before interpreting uncertainty or generalization. [VB-3](review.md#vb-3) |
| Does the reviewer improve scientific accuracy? | A critique prompted spatial analysis; comparative accuracy requires controlled evaluation. [VB-4](review.md#vb-4) [VB-5](review.md#vb-5) |
| Are donor effects accounted for? | Donor aggregation and patient/sample effects are described. [VB-6](review.md#vb-6) |
| Does “first trained” assert novelty? | It describes the order of analysis steps. [VB-7](review.md#vb-7) |

The [structured review](review.json) retains all eleven review items, including
strengths and rejected leads, plus the complete triage of all 30 engine leads.

## Reproduce this showcase

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
