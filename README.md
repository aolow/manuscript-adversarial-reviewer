# Manuscript adversarial review

A local-first Python CLI for reviewing scientific manuscripts. The original
deterministic system remains independent: 46 reporting checks, 10 pattern checks,
source provenance, manual overrides, and the original 20-section detailed audit.

Version 0.2 added explicitly opt-in OpenAI review, claim-level falsification
analysis, a short **What could kill this paper** section, duplicate/disagreement
handling, scientific concern comparison, and a small synthetic benchmark.
The tool supports scientific judgment; it does not establish scientific truth.

Version 0.3 focuses on pilot usability: a shorter revision brief, local run
diagnostics, blinded human evaluation, and a compact manual ChatGPT handoff with
staged, source-validated feedback import. The deterministic rules and reviewer
roster are unchanged.

**Start here:** [PILOT_GUIDE.md](PILOT_GUIDE.md). For evaluation, use
[EVALUATION_GUIDE.md](EVALUATION_GUIDE.md); for manual exchange, use
[CHATGPT_WORKFLOW.md](CHATGPT_WORKFLOW.md).

## Clone and install

This is a private local project. No remote repository has been created or
published. After the owner approves and creates a private remote:

```bash
git clone <your-approved-private-repository-url> manuscript-review
cd manuscript-review
```

For an existing checkout, start in its root. Python 3.9 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[pdf,llm,test]"
python -m unittest discover -s tests -t . -v
```

Core-only install: `python -m pip install -e .`. The core has no third-party
runtime dependencies. PDF uses optional `pypdf`; LLM schema validation uses
optional `jsonschema`. The OpenAI adapter uses the standard-library HTTPS client.

## Offline review: no API key needed

```bash
manuscript-review review fixtures/flawed_manuscript.md
manuscript-review review manuscript.pdf \
  --supplement supplement.docx \
  --journal "Target journal" \
  --out reviews/manuscript-v1
```

Supported: PDF, DOCX, Markdown, UTF-8 text, and repeatable supplements in those
formats. Scanned PDFs need prior OCR. Images, visual figures, equations, and
underlying data are not interpreted. A journal name does not trigger retrieval.

Without `--out`, each run creates a unique directory under `reviews/`. Existing
outputs are protected unless `--force` is supplied. Inputs are protected even
with `--force`. Writes are atomic per file, not per complete run.

## Inspect exact LLM requests without sending anything

```bash
manuscript-review review manuscript.pdf \
  --llm --provider openai --model MODEL_NAME \
  --dry-run --out reviews/request-preview
```

Replace `MODEL_NAME` with the model you intend to use. There is no hard-coded
model or model fallback. Dry runs require no key and never call the provider.
`requests/ROLE.json` contains the exact request body and its hash, with all
source text, instructions, schema, and settings. No authentication header is
exported. Request inputs are independent of prior reviewer output, so dry-run
and live request bodies match for identical documents, overrides, roles, and
settings. Review the source text and scope before deciding to send it.

`--export-prompts` also exports the role packets. These files contain manuscript
text. Export is local and is not permission to upload them elsewhere.

## Explicitly enable live OpenAI review

Set `OPENAI_API_KEY` in your process environment using your normal secure secret
management. The key is never read from configuration files, stored in reports,
or included in logs. Do not paste real keys into tracked files or shell examples.

```bash
manuscript-review review manuscript.pdf \
  --llm --provider openai --model MODEL_NAME \
  --reasoning-effort high \
  --out reviews/llm-review
```

**Running this command authorizes sending the extracted manuscript, supplements,
and deterministic context to OpenAI and may incur API charges.** Ordinary review
commands remain offline even when a key is present in the environment.

Default LLM roles (six independent requests):

1. Scientific/biological: central claims, biological alternatives, causal
   interpretation, state/lineage confounding, and generalizability.
2. Methods/statistics: design, effective replication, validation, uncertainty,
   confounding, multiplicity, calibration, and sensitivity.
3. Computational: leakage, representations, annotation/reference dependence,
   pipeline sensitivity, nulls, baselines, and ablations.
4. Novelty/positioning: contribution type, buried strengths, framing, and
   prior-art hypotheses explicitly requiring external verification.
5. Reviewer 2: concrete attempts to falsify central conclusions.
6. Reproducibility: executable procedures, parameters, cohort definitions,
   artifacts, versions, seeds, and manual curation.

Additional selectable roles: `statistics`, `clinical`, `editor`, `strategist`.
For example: `--roles scientific,computational,reviewer2`. Clinical review is
skipped if the biomarker applicability domain is absent.

The adapter uses the
[OpenAI Responses API with strict Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
It sends no tools and performs no web or literature searches. `store=false` is
sent; this is not a promise of zero provider retention.

### Settings and limits

| CLI | Environment fallback | Behavior |
| --- | --- | --- |
| `--llm` | None | Required opt-in |
| `--provider openai` | None | OpenAI is the only implementation |
| `--model` | `MANUSCRIPT_REVIEW_MODEL` | Required; no automatic choice |
| `--temperature` | `MANUSCRIPT_REVIEW_TEMPERATURE` | Optional, 0–2 |
| `--reasoning-effort` | `MANUSCRIPT_REVIEW_REASONING_EFFORT` | Optional; must be supported by the chosen model |
| `--max-output-tokens` | None | Default 6,000 per request; 256–32,000 |
| `--max-request-chars` | None | Default 240,000 serialized characters per request |
| `--timeout` | None | Default 60 seconds; maximum 60 |
| `--roles` | None | Six defaults; comma-separated overrides |
| `--config` | `MANUSCRIPT_REVIEW_CONFIG` | Deterministic configuration |
| `--log-level` | `MANUSCRIPT_REVIEW_LOG_LEVEL` | Default WARNING |

Temperature and non-`none` reasoning effort cannot be combined. Unspecified
settings are omitted, not guessed from the model name. Model/API compatibility
is checked by the provider; unsupported settings fail rather than silently
changing your request. This follows the
[official OpenAI deployment guidance](https://developers.openai.com/api/docs/guides/deployment-checklist).

No automatic retries, chunk dropping, context truncation, or hidden follow-up
calls occur. Large inputs fail before reviewer calls; raise the explicit limit
or use a smaller input. A character limit is not an exact token or dollar budget.
Refusals, incomplete responses, schema failures, or fabricated citations reject
that reviewer's output. Other roles and the deterministic report remain available.
Failed or rejected responses may still incur charges. The `completed_calls` count
tracks responses accepted by the local schema, not a billing ledger.
Exit status `3` denotes an incomplete LLM run; inspect warnings and request files.
Exit `2` is an input/configuration/output error; exit `0` is successful processing,
not scientific validation.

`.env.example` contains names with empty values only. The application does not
automatically load `.env`.

## Evidence grounding and prioritization

The model cites only an existing block ID and an exact, uniquely locating quote.
The application derives page, section, paragraph, line, and character offsets.
Fabricated quotes, invented blocks, model-supplied locations, malformed schemas,
and unsupported fatal/established verdicts are rejected.

Findings distinguish direct manuscript premises, cross-chunk inference, external
scientific claims, and reviewer recommendations. Ungrounded or suspicious
findings are retained at low confidence with `needs_review` disposition and
excluded from headline concerns. External claims remain unverified. Heuristic
support checks catch obvious unrelated passages, unsupported numeric/design
premises, some contradictions, and excessive certainty. **Exact quotation and
these checks do not prove semantic entailment.**

Duplicate provider concerns are grouped conservatively. Original records and
severity ratings remain visible; disagreements use the less severe rating
pending human review. Deterministic findings are not overwritten by model votes.

The main report prioritizes at most seven consequential issues, major strengths,
ranked claims/evidence, high-priority and secondary analyses, framing, novelty,
reproducibility, and lower-priority reporting. It never pads the headline list.
The full 20-section deterministic-compatible audit remains in a collapsible
appendix and JSON. Computational actions specify input, comparison, held-out
unit, metric, and interpretation; text actions identify the existing section
and claim. These are proposals, not invented completed work.

## Compare scientific concerns across versions

Offline:

```bash
manuscript-review compare manuscript-v1.docx manuscript-v2.docx \
  --old-supplement supplement-v1.pdf \
  --new-supplement supplement-v2.pdf
```

Opt-in semantic comparison, with a saved prior LLM review when available:

```bash
manuscript-review compare manuscript-v1.docx manuscript-v2.docx \
  --prior-review reviews/llm-v1/report.json \
  --llm --model MODEL_NAME \
  --out reviews/scientific-comparison
```

`--dry-run` exports the exact paired request without sending it. Paired mode
(`compare` or `review --prior`) performs **one comparison request**, not six fresh
reviews per version. It includes both full source registries and prior concerns.
`--prior-review` imports current-schema prior scientific/LLM concerns only when
all old document hashes match; without it, prior concerns come from the
independent deterministic audit. There is no automatic prior-report discovery.

Every prior active concern receives a status: `resolved`, `partially_resolved`,
`unresolved`, `worsened`, `no_longer_applicable`, or `cannot_determine`, with
separate old/new evidence and a resolution scope. Missing evidence prevents
resolution. Softer wording cannot override a persistent detected design problem.
Resolution refers to manuscript descriptions/reporting; analysis execution is
never claimed verified. Unassessed LLM items retain explicit deterministic
fallbacks and mark the paired run incomplete.

## Manual configuration and overrides

```bash
manuscript-review list-rules
manuscript-review review manuscript.md \
  --config config/review.example.json \
  --overrides local-overrides.json
```

Rule/domain controls remain unchanged. Overrides are bound to hashes of all
inputs and require reasons. They can correct section assignments or finding
severity, confidence, disposition, effort/value, and reviewer likelihood.
Provider findings can also be overridden by their IDs. Dismissed findings remain
auditable. See [SCHEMA.md](SCHEMA.md) and the files under [config/](config/).

## Synthetic benchmark

```bash
manuscript-review benchmark --manifest benchmarks/manifest.json
manuscript-review benchmark --manifest benchmarks/manifest.json \
  --reports reviews/benchmark-runs --layer llm
```

The benchmark never calls a provider. Optional saved reports live at
`CASE_ID/report.json` and must match each synthetic fixture's hashes.
Score deterministic, LLM, and combined layers separately. Metrics cover scoped
detection/false positives, exact source grounding, annotated evidence alignment,
severity calibration, and structured action completeness. Unannotated flags are
counted separately. The set deliberately contains a known paraphrase miss.
See [benchmarks/README.md](benchmarks/README.md) and
[examples/benchmark.json](examples/benchmark.json). It is not expert validation.

## Portability, GitHub, and ChatGPT

No runtime path is tied to a particular user or machine. Use relative fixture
paths and keep real manuscripts outside source control. Generated outputs,
request packets, credentials, and common manuscript formats are ignored;
inspect staged files anyway. Only deliberately synthetic examples belong here.
See [PRIVATE_PROJECT.md](PRIVATE_PROJECT.md) before any distribution.

Dry-run packets can be manually used in ChatGPT if you explicitly choose to
upload the manuscript content there. The exported schemas describe expected
output, but a manual ChatGPT response is not automatically imported or trusted.
There is no ChatGPT connector, account authentication, or implicit upload.
Use export-chatgpt for the compact package instead of full request packets.
Use import-chatgpt to validate feedback against the original manuscript and
exact export. Import stages candidates by default; explicit --accept-grounded
can activate eligible findings without bypassing grounding checks.

## Local pilot diagnostics

Each API-assisted run writes diagnostics.json and embeds the same data under
quality.pilot_diagnostics in report.json. It records model/reasoning settings,
request byte/input sizes and elapsed call times (in llm-run.json), attempted
calls, failures, incomplete roles, known token usage, raw/accepted/quarantined
findings, merged duplicates, and headline counts. Raw counts are explicitly
incomplete when an output cannot be parsed. Usage on rejected responses is
retained where available; transport failures leave usage unknown.

The API reports token usage, including non-visible output tokens; see
[official token-counting guidance](https://developers.openai.com/api/docs/guides/token-counting).
Cached input and reasoning output are not added twice. No token-counting API
request or pricing lookup is made. Monetary cost remains null because a verified
price/billed currency is not supplied by these response receipts. No telemetry
is introduced. Manual imports identify inherited API history and make zero calls.

## Limits and next steps

No live OpenAI manuscript call was made during development. API behavior is
covered with mocked Responses payloads and exact-request tests, not a live model
quality evaluation. Model availability and supported settings depend on your
account/model. Semantic grounding remains fallible. Novelty and journal policies
require an explicitly authorized external search; none is implemented.

OCR/layout and visual figures, real cohort identity resolution, raw-data/code
verification, and analysis execution remain out of scope. Next: a consented
synthetic live-model pilot, independent human adjudication of a broader benchmark,
better semantic support verification, and figure/table evidence extraction.

[Architecture](ARCHITECTURE.md) · [Schema](SCHEMA.md) ·
[Rubric](REVIEW_RUBRIC.md) · [Example report](EXAMPLE_REPORT.md) ·
[Self-audit](AUDIT.md) · [Changelog](CHANGELOG.md)
