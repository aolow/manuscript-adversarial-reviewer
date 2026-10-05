# A single-cell biomarker associated with cancer response

## Abstract

We present a framework for a cancer response biomarker in the studied population.
Our results suggest an association with treatment resistance across tissues.
Transcriptomic similarity suggests shared expression patterns across cancers.

## Introduction

We develop a single-cell predictor of clinical response using an observational cohort.
Our biomarker predicts treatment response and survival.

## Methods

We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.

We used grouped nested cross-validation with patient-level train/test splits.
Feature selection was performed only within each training fold using training samples.
Hyperparameters were chosen in inner validation, followed by evaluation on an untouched test set.
An independent external cohort of 30 patients was used to evaluate the locked model.

We aggregated counts into donor-level pseudobulk for differential expression.
Independent marker genes were used for signature validation.
P-values were adjusted with the Benjamini-Hochberg false discovery rate procedure.
Random seed 42 was used for splitting and model fitting.
The analysis used Python version 3.11 and a pinned requirements.txt.

## Results

Our model predicts response with AUROC 0.72 and a 95% confidence interval of 0.55 to 0.86 (Figure 1).
The signature separates responders from nonresponders with an adjusted p-value of 0.04 (Table 1).
Our results suggest an association with resistance based on the observational association.
Sensitivity analyses used alternative preprocessing and alternative annotations.
A clinical-only baseline model reached AUROC 0.69.

## Figure Legends

Figure 1. ROC curve computed in the independent external cohort.
Table 1. Donor-level comparisons of signature scores.

## Discussion

The intended clinical use would be risk stratification, pending further evaluation.
The findings describe a prognostic association rather than differential treatment benefit.

## Limitations

Platform and response remain confounded in the discovery cohort.
This observational design cannot establish causality or conserved regulation.
Clinical utility, calibration, and subgroup stability require further study.

## Code and Data Availability

Code is available at https://example.org/synthetic-code.
Synthetic data are available at https://example.org/synthetic-data.

## References

Example reference for the fixture only.
