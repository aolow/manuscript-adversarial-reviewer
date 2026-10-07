# Structured output

The project writes machine-readable JSON alongside Markdown reports.

The authoritative JSON Schemas live in:

- `src/manuscript_review/report.schema.json`
- `src/manuscript_review/comparison.schema.json`
- `src/manuscript_review/llm-response.schema.json`
- `src/manuscript_review/llm-comparison-response.schema.json`

Use those files for implementation details. This document summarizes the stable concepts.

## Review report

Important top-level fields include:

| Field | Purpose |
| --- | --- |
| `schema_version` | Report contract version |
| `tool_version` | Application version |
| `run_id`, `created_at` | Run identity |
| `documents` | Input hashes, formats, source blocks, warnings |
| `extraction` | Claims, cohorts, methods, statistics, references, domains |
| `findings` | Deterministic and provider concerns |
| `checklist` | Reporting-check outcomes |
| `reviewer_runs` | Reviewer role execution status |
| `claim_analyses` | Ranked claims and falsification-oriented analysis |
| `adversarial` | Headline concerns, strengths, priorities, framing |
| `quality` | Duplicate groups, failed roles, diagnostics |
| `llm` | Provider settings and usage metadata, never credentials |
| `comparison` | Optional version-comparison object |

## Findings

A finding records:

- Stable ID and originating rule or reviewer role.
- Severity, category, issue status, confidence, and disposition.
- The concern and why it matters.
- Exact source evidence.
- Suggested fix and optional analysis.
- Priority and editable effort/value judgments.
- Grounding status, quality flags, and duplicate relationships.
- Provider origin when applicable.

Provider findings remain distinguishable from deterministic findings.

## Evidence

Evidence is tied to a source block and exact text span.

Core fields include:

- `document_id`
- `block_id`
- `section`
- `quote`
- `start`, `end`
- page, paragraph, and line metadata when available

The runtime requires the quoted text to match the normalized source exactly.

LLM providers do not supply trusted page or line locations. They supply a block ID and exact quote; the application derives locations locally.

## Checklist statuses

Checklist entries use:

- `reported`
- `not_established`
- `explicit_negative_statement`
- `conflicting`
- `not_applicable`

A reporting cue is not an adequacy judgment.

## Comparison

Each prior active concern receives a resolution state:

- `resolved`
- `partially_resolved`
- `unresolved`
- `worsened`
- `no_longer_applicable`
- `cannot_determine`

Comparison stores separate old and new evidence and explicitly distinguishes reporting changes from verified execution.

## Provider contracts

OpenAI and Bedrock share the same local review contract.

The API-facing Bedrock schema is simplified because Bedrock structured output supports only a subset of JSON Schema. The returned payload is still validated against the full local contract before use.

The local review schema is strict:

- The top-level review object requires `findings`, `claims`, `strengths`, and `limitations`.
- Finding objects require every declared finding property. Action objects require only `kind`; their other fields are nullable/optional as appropriate.
- Provider finding and claim IDs must match `^[a-z][a-z0-9_-]{0,79}# Structured output

The project writes machine-readable JSON alongside Markdown reports.

The authoritative JSON Schemas live in:

- `src/manuscript_review/report.schema.json`
- `src/manuscript_review/comparison.schema.json`
- `src/manuscript_review/llm-response.schema.json`
- `src/manuscript_review/llm-comparison-response.schema.json`

Use those files for implementation details. This document summarizes the stable concepts.

## Review report

Important top-level fields include:

| Field | Purpose |
| --- | --- |
| `schema_version` | Report contract version |
| `tool_version` | Application version |
| `run_id`, `created_at` | Run identity |
| `documents` | Input hashes, formats, source blocks, warnings |
| `extraction` | Claims, cohorts, methods, statistics, references, domains |
| `findings` | Deterministic and provider concerns |
| `checklist` | Reporting-check outcomes |
| `reviewer_runs` | Reviewer role execution status |
| `claim_analyses` | Ranked claims and falsification-oriented analysis |
| `adversarial` | Headline concerns, strengths, priorities, framing |
| `quality` | Duplicate groups, failed roles, diagnostics |
| `llm` | Provider settings and usage metadata, never credentials |
| `comparison` | Optional version-comparison object |

## Findings

A finding records:

- Stable ID and originating rule or reviewer role.
- Severity, category, issue status, confidence, and disposition.
- The concern and why it matters.
- Exact source evidence.
- Suggested fix and optional analysis.
- Priority and editable effort/value judgments.
- Grounding status, quality flags, and duplicate relationships.
- Provider origin when applicable.

Provider findings remain distinguishable from deterministic findings.

## Evidence

Evidence is tied to a source block and exact text span.

Core fields include:

- `document_id`
- `block_id`
- `section`
- `quote`
- `start`, `end`
- page, paragraph, and line metadata when available

The runtime requires the quoted text to match the normalized source exactly.

LLM providers do not supply trusted page or line locations. They supply a block ID and exact quote; the application derives locations locally.

## Checklist statuses

Checklist entries use:

- `reported`
- `not_established`
- `explicit_negative_statement`
- `conflicting`
- `not_applicable`

A reporting cue is not an adequacy judgment.

## Comparison

Each prior active concern receives a resolution state:

- `resolved`
- `partially_resolved`
- `unresolved`
- `worsened`
- `no_longer_applicable`
- `cannot_determine`

Comparison stores separate old and new evidence and explicitly distinguishes reporting changes from verified execution.

.
- Bedrock may normalize unknown `topic`, `issue_key`, or `category` values to the explicit `other` fallback before local validation. Other schema violations are not silently coerced.

### Validation order and fault isolation

`validate_payload(response, REVIEW_SCHEMA)` currently validates the complete provider response before grounding. This gate is atomic: one malformed finding, claim, strength, or required field can reject the whole role. Safe provider diagnostics record the failing schema path and validator without copying the rejected value or manuscript text.

After schema acceptance, grounding is fault-isolated:

- Invalid claim evidence drops the claim without discarding independent findings.
- Invalid finding citations are filtered one at a time. A finding survives if at least one supplied citation resolves; an all-invalid cited finding is dropped.
- Finding `claim_ids` are resolved against accepted/extracted claims. Links to rejected claims are removed, and truly unknown IDs are dropped with `dangling_claim_ref_dropped`.
- Invalid or empty strengths are skipped individually.

Exact quote/block checks remain strict throughout. Per-item isolation is not a relaxation of evidence validation; it limits the blast radius of one bad model element after the response has passed the schema gate.

## Compatibility

Consumers should branch on `schema_version` and use named fields rather than positional assumptions.

Saved prior reviews used for comparison must match the current input document hashes and source extraction. The tool does not silently migrate incompatible old reports.

When model classes change, regenerate JSON Schemas with:

```bash
PYTHONPATH=src python3 scripts/generate_schema.py
```
