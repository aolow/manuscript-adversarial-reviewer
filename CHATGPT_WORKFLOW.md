# Manual ChatGPT workflow

This workflow creates a small local package that you can choose to upload into a normal ChatGPT conversation. The project never uploads it automatically.

## Export

```bash
manuscript-review export-chatgpt reviews/v1/report.json --out handoffs/v1
```

The handoff contains:

- Selected active findings.
- Ranked claims and relevant evidence.
- Central threats and proposed analyses.
- Available comparison state.
- A feedback schema for structured return.

By default it includes at most 15 findings and has a size ceiling to avoid accidental large exports.

Upload `handoffs/v1/chatgpt-review.json` only if you are authorized to share its manuscript content. The generated `CHATGPT_PROMPT.md` contains a short companion prompt.

The package is intentionally incomplete. Missing text must not be treated as evidence that a method, control, or analysis is absent.

## Import structured feedback

Ask ChatGPT to return one JSON object matching the embedded `feedback_schema`, then save it locally as `feedback.json`.

```bash
manuscript-review import-chatgpt \
  reviews/v1/report.json \
  feedback.json \
  --context handoffs/v1/chatgpt-review.json \
  --manuscript manuscript-v1.pdf \
  --out reviews/v1-chatgpt
```

Add the original `--supplement` arguments if applicable.

The import checks:

- The original document hashes.
- The exact exported package identity.
- The top-level feedback/package identity and bounded response container.
- Each returned finding, claim, strength, and limitation independently.
- Citations against excerpts that were actually shared.
- The same local grounding and action checks used for provider output.

New findings are staged as `needs_review` by default. They do not enter the headline list automatically.

After manual inspection, eligible feedback can be activated into a fresh output directory:

```bash
manuscript-review import-chatgpt \
  reviews/v1/report.json \
  feedback.json \
  --context handoffs/v1/chatgpt-review.json \
  --manuscript manuscript-v1.pdf \
  --accept-grounded \
  --out reviews/v1-chatgpt-accepted
```

`--accept-grounded` does not override fabricated citations, unsupported external claims, or failed local checks.

Manual ChatGPT feedback is still scientific judgment, not verified fact.

A malformed feedback child is quarantined with diagnostics rather than erasing valid siblings; an invalid package identity or top-level container still rejects the import. This handoff/import path remains separate from live provider-role execution. See the "What happens to a reviewer response" section in [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
