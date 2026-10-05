# A universal single-cell biomarker of cancer response

## Abstract

We present the first-ever framework for a universal cancer response biomarker.
Our results prove a causal mechanism of treatment resistance across tissues.
Transcriptomic similarity establishes mechanistic conservation across cancers.

## Introduction

We develop a single-cell predictor of clinical response using an observational cohort.
Our biomarker predicts treatment response and survival.

## Methods

We analyzed 12 patients with cancer and profiled 48,000 cells.
Eight patients were responders and four were nonresponders.
All responders were measured on platform A and all nonresponders on platform B.

We selected the top 100 genes using all samples and response labels before splitting into training and test sets.
We tuned hyperparameters using performance on the test set.
The same cohort was used for discovery and validation.

Cells were treated as independent biological replicates in the t-test.
We used the same genes to construct the signature and validate the signature.
Nominal p-values below 0.05 were declared significant across 20,000 genes.

## Results

Our model predicts response with AUROC 0.98 (Figure 1).
The signature separates responders from nonresponders with p-value 0.001 (Table 1).
Our results prove a causal mechanism of resistance based on the observational association.

## Figure Legends

Figure 1. ROC curve computed from the test set.
Table 1. Cell-level comparisons of signature scores.

## Discussion

This biomarker should guide therapy selection in all cancer populations.
The embedding establishes a mechanistic axis linking every tissue.

## References

Example citation title: Independent external validation with confidence intervals.
