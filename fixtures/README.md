# Synthetic fixtures

The files in this directory are invented testing artifacts, not scientific evidence. Their
results, cohorts, code links, and data links are fictitious.

- `flawed_manuscript.md` plants feature-selection leakage, test-set tuning, cohort reuse,
  cell-level pseudoreplication, circular feature validation, causal and conservation
  overclaims, absolute novelty, missing intervals, and uncorrected multiplicity. Its
  reference title contains misleading reporting keywords to test reference exclusion.
- `revised_manuscript.md` is a partial revision fixture. It intentionally retains concerns,
  including platform/response confounding, so a lower flag count must never be interpreted
  as a scientifically valid study.
- `pilot_complex_manuscript.md` is a longer mixed-quality stress-test manuscript used to
  exercise reviewer-role behavior, feasibility checks, grounding, and incomplete-evidence
  cases without exposing real manuscript content.

These fixtures are designed for regression testing. Passing them demonstrates expected
software behavior on declared synthetic cases, not general scientific-review accuracy.
