# Predictive study with leaked selection

## Abstract

Our model predicts patient response.

## Methods

We studied 24 patients. We selected genes using all samples and outcome labels before splitting into training and test sets.
We tuned hyperparameters on the test set.
The same cohort was used for discovery and validation.
No external validation was performed.
Confidence intervals were computed using a patient bootstrap.
Benjamini-Hochberg false discovery rate correction was used.
