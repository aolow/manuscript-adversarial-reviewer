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

Provider output must pass local validation before it can enter the report:

1. The complete response must satisfy the local schema. This gate is currently atomic.
2. Claims, findings, claim links, and strengths are then grounded separately.
3. Citations must point to supplied source blocks and quotes must match exact manuscript text.
4. Unsupported or external interpretations are quarantined or marked for review.
5. Duplicate concerns are grouped without treating agreement as independent confirmation.

Human scientific judgment remains the final authority.

## Reviewer orchestration

Reviewer roles are implemented as a shared safety/grounding prompt plus a role-specific mandate. The default live panel is `scientific,methods,computational,novelty,reviewer2,reproducibility`. The selectable `statistics`, `clinical`, `editor`, and `strategist` roles use the same response contract and grounding pipeline.

Before any live call, `reviewers.llm_packet()` constructs a static packet containing the source blocks, extracted candidate claims, deterministic-context leads, target journal name when supplied, and the selected mandate. All selected role packets are prepared from the same baseline before provider results are incorporated. This prevents one model role from anchoring later roles to its own generated concerns.

The roles are deliberately overlapping at boundaries but have different centers of gravity:

- **Scientific** owns the central-story and claim-evidence question. It is the primary role expected to return ranked claim analyses.
- **Methods** owns experimental design and provenance and, in the default panel, includes a practical statistics pass so a separate statistics call is not mandatory.
- **Computational** follows information flow through representations, feature construction, references, tuning, and validation boundaries.
- **Novelty** evaluates what contribution is actually being claimed while explicitly treating current prior-art verification as external work.
- **Reviewer 2** attacks the strongest claims through falsification and competing explanations rather than generating a generic second checklist.
- **Reproducibility** asks whether the reported procedure can be reconstructed and rerun without private knowledge.
- **Statistics**, **clinical**, **editor**, and **strategist** provide optional specialist depth rather than silently running in every review.

Provider output then passes through three distinct layers that should not be conflated:

```text
provider response
  -> whole-response schema gate
  -> schema accepted
  -> per-item grounding / fault isolation
  -> support + action audit
  -> Finding objects, claim analyses, and grounded strengths
  -> cross-role duplicate reconciliation
  -> adversarial prioritization and report
```

A provider call can therefore be successful while some of its individual findings are rejected or quarantined. Schema acceptance is a transport/contract result, not a scientific-quality verdict. Grounding establishes provenance of quoted text, not semantic truth. The support audit deliberately leaves scientific entailment unverified for human adjudication.

After schema acceptance, failures are fault-isolated at the smallest useful unit. Bad claim evidence drops that claim without discarding independent findings. Finding citations are resolved independently; bad citations are filtered, a finding with at least one valid supplied citation can continue, and an all-invalid cited finding is dropped. Finding links to rejected claims are removed, while truly unknown claim IDs are dropped with a quality flag. Strengths are also isolated: an invalid or empty strength is skipped without affecting findings, claims, or other strengths.

The boundary is deliberate but not complete. `validate_payload(response, REVIEW_SCHEMA)` still validates the provider response atomically before grounding. A malformed finding ID, missing required finding field, or other schema violation can therefore reject the whole role before any per-item salvage occurs. Safe diagnostics retain the schema path and validator but not the rejected model value or manuscript text.

## Providers

### OpenAI

`providers/openai.py` uses the Responses API. Credentials are read from `OPENAI_API_KEY` only at send time. Requests enable no tools or retrieval.

### Amazon Bedrock

`providers/bedrock.py` uses the Converse API and the standard AWS credential chain.

The default Bedrock path defines one Converse tool whose `inputSchema.json` is a normalized JSON Schema object and forces that tool when the selected model supports forced tool choice. The returned `toolUse.input` object is validated again against the stricter full local contract. Nullable `anyOf: [X, null]` fields are flattened for the outbound tool schema and removed from its `required` lists. Tool mode otherwise preserves contract bounds such as `maxItems`, `minLength`, `maxLength`, patterns, and numeric limits so the model sees the intended response limits; the original schema remains authoritative locally.

`--bedrock-json-mode prompt` is the compatibility fallback for models that reject forced tool choice. It places the normalized schema in the system prompt, accepts only JSON text, and still performs the same full local validation. No automatic retry switches modes. Bedrock reasoning effort is only allowed on the prompt path because Anthropic thinking and forced tool choice are incompatible.

Bedrock review payloads are deliberately bounded to 10 findings and 6 claims. ACTION objects require `kind`; the remaining typed fields are optional because tool-use models commonly omit nonapplicable nullable fields. Unknown Bedrock finding classifications are mapped only to the explicit `other` fallback for topic, issue key, or category, and diagnostics record the coerced field paths without retaining the original model values.

Provider grounding is fault-isolated after schema acceptance. Invalid claim evidence drops only that claim. Invalid finding citations are filtered individually, findings survive when at least one supplied citation resolves, and findings whose supplied citations all fail are dropped. Dangling claim links are removed instead of aborting findings. Invalid strengths are skipped individually. Exact quote and block validation itself remains strict.

Schema rejection is different from grounding rejection: the local `REVIEW_SCHEMA` currently validates the whole provider payload at once, so one malformed element can still reject the role before the grounding layer runs. No automatic provider retry is performed.

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

Provider tests use mocked responses. They verify request construction, atomic schema validation, claim/finding/link/strength fault isolation after schema acceptance, failure handling, and dry-run behavior without making live model calls.

The synthetic benchmark is a regression suite, not evidence of general scientific-review quality.
