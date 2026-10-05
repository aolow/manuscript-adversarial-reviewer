# SYNTHETIC PILOT MANUSCRIPT — StateMap response atlas

This is a fictional, deliberately mixed-quality manuscript for software stress
testing. People, cohorts, measurements, and results below are invented.

## Abstract

We present a transcriptomic response atlas that predicts treatment resistance
and establishes a lineage mechanism shared across tumor contexts. A fixed
reference representation links a cell state to response in a retrospective
study. We report high discrimination and propose the atlas as a universal
clinical biomarker. The strongest potential contribution is a reusable mapping
procedure, although its independence from the discovery labels remains unclear.

## Introduction

Cell states can reflect lineage, environment, technical processing, or treatment
history. Our aim is to distinguish a transferable response signal from
cohort-specific composition. We claim a new reference-mapping workflow; whether
related workflows already exist requires a literature comparison outside this
fictional manuscript.

## Methods

Discovery cohort A included 24 donors contributing 96 specimens. Three visits
were available for some donors but the released matrix contains only baseline
measurements. Specimen identifiers were retained, whereas donor identifiers
were removed from the released analysis table. The total was 60,000 cells.

The analysis is observational. Treatment was assigned by routine clinical
practice. No random allocation or prospective intervention was performed.
Response status was extracted from clinical records without blinded adjudication.
Site X used platform P and mostly contributed responders. Site Y used platform
Q and contributed only resistant cases. The site-by-response table has empty
strata, limiting identification of response separately from processing.

All labeled specimens contributed to the ranking of transcripts. The shortlist
was frozen before specimens were partitioned into development and evaluation
sets. The downstream classifier did not see evaluation labels during fitting,
but its input coordinates were built using the earlier pooled ranking.
Repeated specimens from the same donor could appear on both sides of the
partition. Scaling parameters were also estimated on the combined matrix.

Model settings were chosen by repeatedly inspecting evaluation-set AUROC.
The configuration with the largest observed value was reported. The same
evaluation data were then used to compute an ordinary confidence interval
without accounting for the preceding configuration search.

For a group comparison we treated every cell as an independent replicate.
The article describes 96 samples but does not claim 96 independent donors.
The released data contain neither a donor key nor the original raw reads.
Raw reads are unavailable. Reconstructing donor-aware resampling from this
release alone would require information that is not currently available.

The reference atlas was annotated with a response-associated panel obtained
from cohort A. Query cells were assigned labels using that panel, and agreement
with those assigned labels was used as the principal accuracy endpoint.
Reference-derived labels were not compared with blinded independent pathology.
Sensitivity to a different reference, annotation system, and feature
representation was not assessed.

The validation collection was named cohort B. It was a later sequencing run
of banked aliquots from 18 donors already in cohort A. This is a technical
replication collection rather than evidence from new patients. No independent
external cohort is available.

No untreated negative-control condition was measured. Protein measurements
were not collected. No longitudinal outcomes are available in the released
data. New controlled perturbations, proteomics, or prospective follow-up would
require new data collection rather than a different computation on this release.

To document reproducibility, the manuscript reports a software environment
lockfile, a fixed seed, and the mapping equation. Several manual annotation
corrections were made after visualization; the cell list and decision criteria
were not recorded. Exclusion of low-quality cells depended on a threshold
selected after examining response separation.

## Results

The selected configuration achieved AUROC 0.94 in the specimen-level evaluation.
The nominal interval was 0.90 to 0.97. Performance declined to 0.73 under a
different reference, although this sensitivity result is described only here.
Calibration and decision utility were not measured.

Agreement with panel-derived labels was 93%. Agreement supports consistency
with the annotation procedure; it does not independently establish biological
identity. The cell-level group test produced a small p-value. No donor-level
uncertainty estimate could be computed from the de-identified release.

Technical replication in cohort B preserved the direction of the score.
That observation does not test transportability to a new patient population.
Exploratory inspection identified a subgroup with stronger separation, and a
post-selection significance test on the same observations was reported without
an independent confirmatory sample.

## Discussion

The mapping equation and documented environment could support a methodological
contribution if the representation can be locked independently of evaluation
labels. A balanced, truly separate cohort would be needed to distinguish
transportability from site, treatment history, and processing effects.

We nevertheless describe the associated state as a causal driver and infer
lineage conversion from similarity in the embedding. The experiments do not
include lineage tracing or controlled perturbation. A plausible alternative is
that cohort composition or reference labels create the apparent axis.

The proposed clinical use exceeds the measured discrimination endpoint. A
narrower framing would describe an exploratory mapping method and specify
which biological and clinical claims remain untested. We propose additional
experiments but do not present them as completed.

## Data and code availability

The processed baseline matrix and mapping code are described as shareable.
No real repository or dataset is linked because this manuscript is fictional.
The donor linkage, raw sequencing reads, and manual annotation change log are
not available in the synthetic release.
