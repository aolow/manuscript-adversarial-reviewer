# Architecture

The project is intentionally local-first. Deterministic review is the baseline, and LLM providers are optional adapters around the same review contract.

## Data flow

```text
manuscript + supplements
  -> ingestion and source blocks
  -> extraction
  -> deterministic checks
  -> prioritization
  -> optional LLM reviewer calls
  -> local schema and source validation
  -> duplicate reconciliation
  -> revision brief + detailed report

old report + revised manuscript
  -> deterministic comparison
  -> optional one-call semantic comparison
  -> comparison report
```

Only an explicit `--llm` operation contacts an external provider.

## Main modules

| Module | Responsibility |
| --- | --- |
| `ingestion/` | Parse PDF, DOCX, Markdown, and text into stable source blocks |
| `extraction.py` | Extract candidate claims, cohorts, methods, statistics, references, and domains |
| `rules/` | Deterministic reporting and scientific-pattern checks |
| `prioritization.py` | Assign ordinal revision priority |
| `reviewers/` | Build role-specific prompts and route provider output |
| `providers/` | OpenAI and Bedrock transport adapters |
| `grounding.py` | Resolve exact quotes, derive locations, quarantine weak support |
| `adversarial.py` | Build claim-centered threats, strengths, and action priorities |
| `comparison.py` | Compare versions without equating text disappearance with scientific resolution |
| `resolution.py` | Add provider-assisted concern resolution in paired mode |
| `reporting.py` | Render Markdown and structured outputs |
| `evaluation.py` | Prepare and score blinded human evaluation |
| `exchange.py` | Export and import compact manual ChatGPT feedback |
| `diagnostics.py` | Summarize provider attempts, failures, usage, and disposition counts |

## Trust boundaries

### Deterministic checks

Deterministic rules are inspectable and reproducible, but deliberately narrow. A matched phrase is evidence for a check, not proof of a scientific defect.

### LLM reviewers

LLM roles receive the same static manuscript context independently. One role's output does not become another role's input.

Provider findings must pass local validation before they can enter the report:

1. The response must satisfy the local schema.
2. Citations must point to supplied source blocks.
3. Quotes must match exact manuscript text.
4. Unsupported or external claims are quarantined or marked for review.
5. Duplicate concerns are grouped without treating agreement as independent confirmation.

Human scientific judgment remains the final authority.

## Providers

### OpenAI

`providers/openai.py` uses the Responses API. Credentials are read from `OPENAI_API_KEY` only at send time. Requests enable no tools or retrieval.

### Amazon Bedrock

`providers/bedrock.py` uses the Converse API and the standard AWS credential chain.

The default Bedrock path defines one Converse tool whose `inputSchema.json` is a normalized JSON Schema object and forces that tool when the selected model supports forced tool choice. The returned `toolUse.input` object is validated again against the stricter full local contract. Nullable `anyOf: [X, null]` fields are flattened for the outbound tool schema and removed from its `required` lists. Tool mode otherwise preserves contract bounds such as `maxItems`, `minLength`, `maxLength`, patterns, and numeric limits so the model sees the intended response limits; the original schema remains authoritative locally.

`--bedrock-json-mode prompt` is the compatibility fallback for models that reject forced tool choice. It places the normalized schema in the system prompt, accepts only JSON text, and still performs the same full local validation. No automatic retry switches modes. Bedrock reasoning effort is only allowed on the prompt path because Anthropic thinking and forced tool choice are incompatible.

Provider choice does not change the scientific review pipeline.

## Provenance

Every input document has a content hash. Parsed text is divided into stable source blocks. Evidence points to exact character spans within those blocks.

The model supplies only a block ID and exact quote. Page, paragraph, line, section, and character locations are derived locally.

Overrides are bound to document hashes so they cannot silently carry over to a changed manuscript.

## Version comparison

Comparison separates three ideas that should not be conflated:

- Text or reporting changed.
- The manuscript describes a corrected design or analysis.
- The underlying analysis was actually executed and is scientifically valid.

The tool can assess the first two from manuscript text. It does not verify the third.

Paired LLM mode makes one comparison request rather than rerunning all reviewer roles on both manuscripts.

## Privacy and persistence

The application has no database, service, telemetry process, or background worker. Outputs are local files.

Real manuscripts and request packets may contain confidential text. Keep them outside source control and review [DATA_SAFETY.md](DATA_SAFETY.md) before live provider use.

## Testing

The repository uses `unittest` plus GitHub Actions on Python 3.10 and 3.12.

Provider tests use mocked responses. They verify request construction, schema validation, grounding behavior, failure handling, and dry-run behavior without making live model calls.

The synthetic benchmark is a regression suite, not evidence of general scientific-review quality.
