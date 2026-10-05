# Qualified patient response model

## Abstract

Our model predicts response in the studied cohort.
This observational association does not establish a causal mechanism.

## Methods

We studied 80 patients and used grouped patient-level train/test splits.
Gene selection was performed only within each training fold.
We selected prespecified features from prior literature before splitting.
Hyperparameters were chosen using nested cross-validation.
An independent external cohort of 45 patients evaluated the frozen model.
Confidence intervals were computed by patient-level bootstrap.
Benjamini-Hochberg false discovery rate correction was used.
Calibration was assessed with a Brier score and calibration plot.
All responders were measured on platform A and all nonresponders on platform A.

## References

Example title: The first-ever framework proves a causal mechanism.
