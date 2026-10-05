# Development report: 0.2.0

Historical baseline record. The current pilot-readiness pass is documented in
[PILOT_READINESS_REPORT.md](PILOT_READINESS_REPORT.md).

The existing local CLI now has an explicitly opt-in OpenAI review layer,
claim-level adversarial analysis, evidence validation, prioritized improvement
plans, and scientific concern comparison. The deterministic core remains an
independent baseline. No source rebuild, real manuscript upload, Git commit,
remote creation, or publication occurred.

## 1. Files changed

Paths below are relative to the checkout. No baseline source file was removed.
The full rule catalogue/engine, extraction, prioritization, configuration, and
the original ingestion/CLI/rules/comparison/contracts tests remain unchanged.

New implementation files:

- `src/manuscript_review/providers/__init__.py`
- `src/manuscript_review/providers/contracts.py`
- `src/manuscript_review/providers/openai.py`
- `src/manuscript_review/grounding.py`
- `src/manuscript_review/adversarial.py`
- `src/manuscript_review/resolution.py`
- `src/manuscript_review/benchmark.py`
- `src/manuscript_review/llm-response.schema.json`
- `src/manuscript_review/llm-comparison-response.schema.json`
- `src/manuscript_review/reviewers/prompts/base_v2.txt`
- `src/manuscript_review/reviewers/prompts/comparison.txt`
- `src/manuscript_review/reviewers/prompts/computational.txt`
- `src/manuscript_review/reviewers/prompts/reproducibility.txt`

Updated implementation and generator files:

- `src/manuscript_review/__init__.py`
- `src/manuscript_review/cli.py`
- `src/manuscript_review/models.py`
- `src/manuscript_review/pipeline.py`
- `src/manuscript_review/comparison.py`
- `src/manuscript_review/reporting.py`
- `src/manuscript_review/validation.py`
- `src/manuscript_review/ingestion/__init__.py`
- `src/manuscript_review/reviewers/__init__.py`
- `src/manuscript_review/reviewers/prompts/scientific.txt`
- `src/manuscript_review/reviewers/prompts/methods.txt`
- `src/manuscript_review/reviewers/prompts/novelty.txt`
- `src/manuscript_review/reviewers/prompts/reviewer2.txt`
- `src/manuscript_review/report.schema.json`
- `src/manuscript_review/comparison.schema.json`
- `scripts/generate_schema.py`
- `scripts/refresh_examples.py`
- `pyproject.toml`

Tests added: `tests/llm_helpers.py`, `tests/test_llm_grounding.py`,
`tests/test_openai_provider.py`, `tests/test_semantic_comparison.py`,
`tests/test_llm_cli.py`, and `tests/test_benchmark.py`.
`tests/test_schema.py` was extended while retaining its original test.

Documentation/configuration added or updated: `README.md`, `ARCHITECTURE.md`,
`SCHEMA.md`, `REVIEW_RUBRIC.md`, `CHANGELOG.md`, `AUDIT.md`,
`DEVELOPMENT_REPORT.md`, `PRIVATE_PROJECT.md`, `.env.example`, and `.gitignore`.

New benchmark files: `benchmarks/README.md`, `benchmarks/manifest.json`, and
`benchmarks/fixtures/{leakage,pseudoreplication,circular_biology,safe_control,missing_reporting,paraphrased_leakage}.md`.

Deliberately synthetic examples regenerated: `EXAMPLE_REPORT.md`,
`examples/flawed-report.json`, `examples/revised-report.json`,
`examples/comparison.json`, and `examples/comparison.md`.
`examples/benchmark.json` is new.

## 2. Architecture

Ingestion, extraction, deterministic rules, and manual overrides run locally.
An explicitly supplied provider receives an independent static packet per role.
The Responses adapter sends a strict JSON Schema, then local validation checks
the response before it can join the report. Failures preserve the deterministic
results and produce an incomplete-run status.

The grounding module resolves citations, applies heuristic support checks, and
quarantines unsupported criticism. Conservative duplicate reconciliation keeps
original ratings and flags disagreements. Claim analyses and central-story
threats precede the collapsible 20-section detailed audit. The headline has at
most seven issues and is never padded to reach a quota.

Paired mode uses one request containing both source registries and prior issues.
A saved prior review can supply earlier LLM concerns after source integrity
checks. Every prior active issue receives one of six resolution states with
separate old/new evidence. Described methods never imply verified execution.

The report contract is now 1.1.0; provider envelopes have separate strict
schemas. Regenerate older 1.0 reports before importing them as prior reviews.

## 3. CLI examples

Activate the installed environment and run these from the checkout root:

```bash
# Local review; no key or network use.
manuscript-review review fixtures/flawed_manuscript.md \
  --out reviews/offline

# Exact six-role requests, exported locally without an API key.
manuscript-review review fixtures/flawed_manuscript.md \
  --llm --provider openai --model MODEL_NAME \
  --dry-run --out reviews/preview

# Explicit opt-in: sends source text and may incur charges.
# OPENAI_API_KEY must already be in the process environment.
manuscript-review review manuscript-v1.docx \
  --llm --provider openai --model MODEL_NAME \
  --reasoning-effort high --out reviews/llm-v1

# Inspect a paired request, including earlier LLM concerns if available.
manuscript-review compare manuscript-v1.docx manuscript-v2.docx \
  --prior-review reviews/llm-v1/report.json \
  --llm --model MODEL_NAME --dry-run \
  --out reviews/comparison-preview

# Local synthetic scoring; never starts a model review.
manuscript-review benchmark --manifest benchmarks/manifest.json
```

For the prior-review example, the supplied old manuscript and supplements must
exactly match the inputs used to produce `reviews/llm-v1/report.json`; use the
same input format. Remove `--prior-review` when no matching saved review exists.
Choose fresh output directories for each run.

Model selection has no default. Temperature and reasoning are optional, subject
to model support; temperature cannot accompany non-none reasoning. All six
request bodies are prepared before calls so oversized inputs fail early.
There are no automatic retries or hidden retrieval calls. See
[README.md](README.md) for settings, environment names, limits, and exit codes.

## 4. Exact verification

The final full command was:

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

**118 tests passed in 2.749 seconds, with no failures or skips: 54 baseline tests
plus 64 additions.**

| Test module | Tests |
| --- | ---: |
| test_ingestion | 12 |
| test_rules | 20 |
| test_contracts | 9 |
| test_comparison | 5 |
| test_cli | 7 |
| test_schema | 3 |
| test_llm_grounding | 23 |
| test_openai_provider | 14 |
| test_llm_cli | 11 |
| test_semantic_comparison | 8 |
| test_benchmark | 6 |
| Total | 118 |

`pip check` found no broken requirements. The 0.2.0 wheel installed offline in
a separate temporary location and ran from a different working directory.
Network-blocked smoke checks passed for dependency-free core review, a six-role
dry run, and a paired dry run with an imported prior report. All four schemas
and 13 prompt files were present in the package. No live provider was contacted.

## 5. LLM-enabled reviewers

| Default role | Distinct emphasis |
| --- | --- |
| Scientific/biological | Ranked claims, causality, state/lineage/context, biological alternatives, generalizability |
| Methods/statistics | Design, effective replication, held-out validation, confounding, multiplicity, uncertainty, calibration |
| Computational | Leakage, circularity, representation/reference/annotation dependence, robustness, nulls, baselines, ablations |
| Novelty/positioning | Contribution type, prior-art hypotheses requiring search, buried strengths, framing |
| Reviewer 2 | Competing explanations, explicit failure criteria, decisive falsification analyses |
| Reproducibility | Cohort definitions, software/parameters/seeds, exclusions, manual curation, code/data availability |

Additional selectable roles: `statistics`, `clinical`, `editor`, and `strategist`.
The clinical role requires the biomarker applicability domain. Paired comparison
uses its own single reviewer. These roles are implemented and mock-tested;
their real scientific quality has not been measured.

## 6. Evidence grounding

Models supply block IDs and exact uniquely locating quotations. Local code
derives section, page when available, paragraph, line, and character offsets.
Direct factual premises must occur within their cited excerpts. Cross-manuscript
inference needs multiple chunks and an explicit rationale. External scientific
claims and reviewer opinions have distinct basis labels.

Unsupported or unlocated findings are retained at low confidence for human
review and excluded from headline concerns. High-confidence subjective
judgments are capped. Major actions require concrete analysis fields or an
identified source section/claim for editing. Claim objects include support,
weakness, alternatives, falsification, decisive action, impact, and importance.

## 7. Hallucination checks

Regression tests reject fabricated quotes, unknown blocks, nonexistent model
page/section fields, unsupported claim links, and invalid response schemas.
Tests also exercise unrelated but real source passages, invented numeric/design
premises, protective/negated methods, unsupported certainty, external claims,
missing actions, duplicate findings, and severity conflicts. Imported reports
must agree with freshly extracted source text and locators.

Exact source validation is deterministic. Scientific support checking is
heuristic and can miss persuasive hallucinations or flag valid interpretations.
`source_verified` means the citation exists, not that the scientific judgment
is correct. Model ratings and resolution judgments remain unverified.

## 8. Benchmark

Six fictional cases contain 12 expected issues. The deterministic layer detects
11, misses the deliberately paraphrased leakage case, and produces zero false
positives within the 12 declared issue families: scoped precision 100%, recall
91.7%. There are 68 unscored findings outside that scope. Exact source grounding
is 79/79; annotated evidence alignment, acceptable severity, and structured action
completeness are each 11/11 for detected annotated issues.

These are small, author-designed regression results, not expert validation.
Action completeness is not scientific usefulness. There is no live LLM score.
Saved, source-validated reports can be scored by deterministic, LLM, or combined
layer. See [benchmark methods](benchmarks/README.md) and the
[machine-readable result](examples/benchmark.json).

## 9. Remaining limitations

- Model/account compatibility, cost, latency, and real review quality need a live pilot.
- Semantic entailment, severity, claim ranking, and proposed analyses need human adjudication.
- No scientific literature or journal-policy retrieval; novelty claims remain provisional.
- No OCR, visual figure interpretation, raw-data/code auditing, or verified analysis execution.
- Whole-manuscript requests have explicit size/output limits, but no exact dollar budget.
- Claim/cohort matching and deterministic language coverage remain incomplete.
- Prior current-schema reports can be imported; old-schema reports need regeneration.
- ChatGPT use is manual packet upload only; no connector or automatic response import exists.
- `store=false` is not a provider-retention guarantee. Failed calls may still be billed.

## 10. Next-phase approvals

No approval is needed for local offline review or dry-run inspection. A live
pilot requires your explicit opt-in command, selected model, environment key,
and willingness to incur charges. Real manuscript uploads require the same
explicit opt-in and suitable permission to share that content.

Creating any remote repository, publishing, changing visibility, or distributing
this private project requires separate approval. No such action was taken.
External literature retrieval and future figure/data execution would be new
scope; none is silently enabled.
