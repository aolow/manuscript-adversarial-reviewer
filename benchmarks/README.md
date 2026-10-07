# Synthetic regression benchmark

These six manuscripts are deliberately fictional. Their annotations are
expert-style expectations written for software regression, not independently
adjudicated expert judgments. No real manuscript or live LLM response is used.

| Case | Expected issue families | Purpose |
| --- | --- | --- |
| leakage | Feature selection before splitting, test-set tuning, cohort reuse, absent external validation | Explicit information leakage |
| pseudoreplication | Cell-level pseudoreplication/inappropriate statistical unit | Effective biological replication |
| circular_biology | Circular signature, causal overclaim, unsupported novelty claim | Independence and biological interpretation |
| safe_control | None in the declared rule scope | Negative control with explicit safeguards |
| paraphrased_leakage | Feature selection before splitting | Deliberate known miss of the deterministic language rules |
| missing_reporting | Missing confidence intervals, multiplicity correction, external validation | Separate reporting and validation gaps |

Run from the checkout root:

```bash
manuscript-review benchmark --manifest benchmarks/manifest.json
```

The command never contacts a provider. It evaluates all active findings within
the 12 issue families in `evaluated_rule_ids`. A detected family absent from a
case's expected list is a false positive. A missing expected family is a false
negative. Duplicate instances within a family count once for detection.
The remaining findings are explicitly unscored, not presumed correct.

The checked-in [result](../examples/benchmark.json) was generated from the synthetic deterministic suite and remains a regression reference for the current 0.3.x line:

| Measure | Result |
| --- | ---: |
| Annotated issues detected | 11/12 |
| False positives within annotated scope | 0 |
| Scoped precision / recall | 100% / 91.7% |
| Unscored findings outside scope | 68 |
| Findings with validated exact source evidence | 79/79 |
| Detected issues aligned with annotated evidence phrases | 11/11 |
| Detected issues within acceptable severity categories | 11/11 |
| Detected issues with complete structured action fields | 11/11 |

The paraphrased-leakage case is intentionally retained as a false negative.
Exact source evidence does not establish entailment. Phrase alignment checks
only annotated synthetic text; severity categories are broad; action completeness
does not measure feasibility, expected information gain, or scientific value.
The safe-control case still has eight unscored reporting flags.
These results establish neither expert performance nor live LLM quality.

## Score saved LLM reviews

Only explicitly authorized review commands may create live LLM results. For
example, after inspecting a dry run:

```bash
manuscript-review review benchmarks/fixtures/leakage.md \
  --llm --provider openai --model MODEL_NAME --dry-run \
  --out reviews/benchmark-preview/leakage

# This command sends the synthetic manuscript and may incur API charges.
manuscript-review review benchmarks/fixtures/leakage.md \
  --llm --provider openai --model MODEL_NAME \
  --out reviews/benchmark-runs/leakage
```

Create one saved review per manifest case under `CASE_ID/report.json` before
scoring. Then score layers separately:

```bash
manuscript-review benchmark --manifest benchmarks/manifest.json \
  --reports reviews/benchmark-runs --layer llm
manuscript-review benchmark --manifest benchmarks/manifest.json \
  --reports reviews/benchmark-runs --layer deterministic
manuscript-review benchmark --manifest benchmarks/manifest.json \
  --reports reviews/benchmark-runs --layer combined
```

Saved reports must use the current report contract, match each fixture's
document hashes and freshly extracted source blocks, and pass local provenance
validation. Quarantined, dismissed, and duplicate records are excluded from
active detection scores. LLM findings identify their family through `issue_key`;
manually adjudicate these labels before interpreting scores. The benchmark does
not establish that an uploaded report came from a real model call.

Provider coverage must also be interpreted explicitly. A schema-rejected role contributes no
findings because schema validation is still whole-response atomic. After schema acceptance,
bad claim evidence, individual finding citations, dangling claim links, and strengths are
fault-isolated, so raw provider finding counts can exceed the locally retained count.

## Extend the benchmark

Add only deliberately synthetic or separately approved safe cases. Keep fixture
paths within this directory, declare `synthetic_only: true`, and add annotations
to `manifest.json` with a rule ID, acceptable severity categories, and expected
source phrases. Expand the declared scope before interpreting new false positives.

Independent human review, broader disciplines, adversarial negation, tables,
supplements, imperfect extraction, and model-by-model evaluation remain needed.
Do not tune away all difficult cases or claim generalization from this set.
