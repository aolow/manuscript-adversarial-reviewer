# Evaluate assisted review

Use this workflow to compare the deterministic review with an LLM-assisted review without showing the rater which is which.

This is an exploratory evaluation, not a validated benchmark of scientific quality.

## 1. Create both reviews

Baseline:

```bash
manuscript-review review manuscript.pdf --out reviews/baseline
```

Assisted:

```bash
manuscript-review review manuscript.pdf \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --out reviews/assisted
```

Use the same manuscript, supplements, configuration, and overrides for both arms.

## 2. Prepare a blinded package

```bash
manuscript-review evaluate prepare \
  --baseline reviews/baseline/report.json \
  --assisted reviews/assisted/report.json \
  --out evaluations/pilot
```

Give the adjudicator:

- `blinded-reviews.md`
- `manuscript-context.json`
- `RUBRIC.md`
- `concern-ratings.csv`
- `adjudication.json`

Keep `private/key.json` hidden until scoring.

Blinding removes explicit source labels and provider metadata, but writing style or review length may still reveal the source.

## 3. Rate the reviews

Before reading the blinded reviews, list the important issues you think a good review should identify when practical.

For each concern, classify it as one of:

- `true_important_concern`
- `valid_minor_concern`
- `redundant_concern`
- `unsupported_speculative_concern`
- `false_positive`
- `unable_to_judge`

Rate applicable dimensions from 0 to 3:

| Dimension | Question |
| --- | --- |
| Scientific correctness | Is the concern scientifically sound? |
| Severity calibration | Is its importance rated appropriately? |
| Evidence grounding | Does the cited text actually support it? |
| Specificity | Does it identify the exact problem? |
| Actionability | Is the proposed next step useful and feasible? |
| Novelty positioning | Is the framing useful, with literature claims kept provisional? |
| Nonredundancy | Does it add distinct information? |
| Author usefulness | Would it materially improve revision decisions? |

Use blank or null when a dimension cannot be judged. Do not convert missing ratings to zero.

Record an overall usefulness score for each arm and an optional preferred arm. Explain disputed, speculative, or false-positive concerns briefly.

## 4. Score and unblind

```bash
manuscript-review evaluate score evaluations/pilot \
  --ratings-csv evaluations/pilot/concern-ratings.csv \
  --out evaluations/pilot-result
```

The result reports:

- Important issues found and missed.
- False, speculative, minor, redundant, and unjudged concerns.
- Per-dimension ordinal means and denominators.
- Assisted-minus-baseline differences.
- Overall usefulness, preference, and blinding notes.
- Incomplete provider roles.

It does not produce a single weighted scientific-quality score or claim statistical significance.

One manuscript and one rater are useful for debugging the workflow, not for establishing general performance.

## Optional expert arm

Add `--expert expert-review.json` to `evaluate prepare` for a randomized third arm. The expert review is treated as another comparison arm, not as ground truth.
