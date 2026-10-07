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

1. The top-level response container must have the expected bounded arrays.
2. Claims, findings, strengths, and comparison assessments are schema-validated independently.
3. Citations must resolve uniquely to supplied substantive source blocks; exact matching is preferred, with conservative Unicode/whitespace normalization as a fallback.
4. Unsupported or external interpretations are quarantined or marked for review.
5. Duplicate concerns are grouped without treating agreement as independent confirmation, and explicit human overrides remain authoritative.

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
  -> bounded container validation
  -> per-item schema validation / safe normalization
  -> per-item source grounding / fault isolation
  -> support + action audit
  -> Finding objects, claim analyses, and grounded strengths
  -> cross-role duplicate reconciliation
  -> version-bound human overrides
  -> adversarial prioritization and report
```

A provider call can therefore be successful while some of its individual findings, claims, strengths, or limitations are rejected or quarantined. Container acceptance is a transport/contract result, not a scientific-quality verdict. Grounding establishes provenance of quoted text, not semantic truth. The support audit deliberately leaves scientific entailment unverified for human adjudication.

Failures are fault-isolated at the smallest useful unit. Cosmetic model IDs are normalized because report finding IDs are generated locally from role, issue family, basis, and source-block anchors. Missing substantive fields reject only that item. Bad claim evidence drops the claim without discarding independent findings. Finding citations are resolved independently; bad citations are filtered, a finding with at least one valid supplied citation can continue, and an all-invalid cited finding is dropped. Finding links to rejected claims are removed, while truly unknown claim IDs are dropped with a quality flag. Invalid strengths and limitations are skipped individually.

Only a malformed top-level container remains role-fatal. Safe diagnostics retain schema paths, validators, normalizations, and rejection categories without retaining rejected model values.

## Providers

### OpenAI

`providers/openai.py` uses the Responses API. Credentials are read from `OPENAI_API_KEY` only at send time. Requests enable no tools or retrieval.

### Amazon Bedrock

`providers/bedrock.py` uses the Converse API and the standard AWS credential chain.

The default Bedrock path defines one Converse tool whose `inputSchema.json` is a normalized JSON Schema object and forces that tool when the selected model supports forced tool choice. The full item contract is still supplied to the model, but local acceptance first validates the response container and then validates each child independently. Nullable `anyOf: [X, null]` fields are flattened for the outbound tool schema and removed from its `required` lists. Tool mode otherwise preserves contract bounds such as `maxItems`, `minLength`, `maxLength`, patterns, and numeric limits so the model sees the intended response limits.

`--bedrock-json-mode prompt` is the compatibility fallback for models that reject forced tool choice. It places the normalized schema in the system prompt, accepts only JSON text, and uses the same two-stage local validation. No automatic retry switches modes. Bedrock reasoning effort is only allowed on the prompt path because Anthropic thinking and forced tool choice are incompatible.

Bedrock review payloads are deliberately bounded to 10 findings and 6 claims. ACTION objects require `kind`; the remaining typed fields are optional because tool-use models commonly omit nonapplicable nullable fields. Unknown Bedrock finding classifications are mapped only to the explicit `other` fallback for topic, issue key, or category, and diagnostics record the coerced field paths without retaining the original model values.

Provider processing is fault-isolated after container acceptance. Invalid child schemas, claim evidence, finding citations, dangling claim links, strengths, and limitations are handled per item. Exact quote/block provenance remains strict; conservative normalization only accepts a unique source match and maps evidence back to the original extracted span.

Request preparation is also role-isolated. A role that exceeds the local request-size guard is marked failed without sending a network request, while other roles and the deterministic baseline continue. No automatic provider retry is performed.

Provider choice does not change the scientific review pipeline.

## Provenance

Every input document has a content hash. Parsed text is divided into stable source blocks. Evidence points to exact character spans within those blocks.

The model supplies only a block ID and quote. Exact quotes are preferred; harmless Unicode/whitespace drift may be normalized only when it maps uniquely back to the original block. Page, paragraph, line, section, and character locations are always derived locally.

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

Provider tests use mocked responses. They verify request construction, strict container validation, per-item schema/source isolation, stable local IDs, comparison fallbacks, artifact cleanup, failure handling, and dry-run behavior without making live model calls.

The synthetic benchmark is a regression suite, not evidence of general scientific-review quality.
