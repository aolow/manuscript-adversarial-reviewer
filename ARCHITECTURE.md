# Architecture

## Data flow

```text
PDF / DOCX / Markdown / UTF-8 text + optional supplements
  -> ingestion and section detection
  -> version-bound section overrides
  -> extraction (claims, cohorts, methods, statistics, references, domains)
  -> independent reporting checks and narrow pattern checks
  -> finding overrides and ordinal prioritization
  -> offline routing OR opt-in independent OpenAI reviewer requests
  -> schema, exact-source, and conservative support validation
  -> duplicate/disagreement reconciliation and claim-centered synthesis
  -> prioritized Markdown + preserved 20-section detailed audit + JSON

old review + new review -> textual/claim/finding comparison -> comparison outputs
  -> optional paired LLM assessment with both source registries and prior issues
```

The core and test runner use the Python standard library. PDF is an optional
`pypdf` extra. Optional LLM validation uses `jsonschema`; the Responses adapter
uses standard-library HTTPS. No infrastructure, database, telemetry, or background
process is required. Only an explicit LLM operation contacts the provider.

## Repository layout

```text
.
├── pyproject.toml
├── .env.example
├── README.md
├── ARCHITECTURE.md
├── SCHEMA.md
├── REVIEW_RUBRIC.md
├── EXAMPLE_REPORT.md
├── CHANGELOG.md
├── AUDIT.md
├── PRIVATE_PROJECT.md
├── benchmarks/
│   ├── manifest.json
│   ├── README.md
│   └── fixtures/
├── config/
│   ├── review.example.json
│   └── overrides.example.json
├── fixtures/
│   ├── README.md
│   ├── flawed_manuscript.md
│   └── revised_manuscript.md
├── examples/
│   ├── flawed-report.json
│   ├── revised-report.json
│   ├── comparison.json
│   └── comparison.md
├── scripts/
│   ├── generate_schema.py
│   └── refresh_examples.py
├── src/manuscript_review/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── configuration.py
│   ├── errors.py
│   ├── models.py
│   ├── adversarial.py
│   ├── grounding.py
│   ├── resolution.py
│   ├── benchmark.py
│   ├── report.schema.json
│   ├── comparison.schema.json
│   ├── llm-response.schema.json
│   ├── llm-comparison-response.schema.json
│   ├── validation.py
│   ├── extraction.py
│   ├── prioritization.py
│   ├── pipeline.py
│   ├── comparison.py
│   ├── reporting.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── sections.py
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── catalogue.py
│   │   └── engine.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── contracts.py
│   │   └── openai.py
│   └── reviewers/
│       ├── __init__.py
│       └── prompts/
│           ├── base.txt, base_v2.txt, comparison.txt
│           └── {scientific,methods,statistics,clinical,reviewer2,
│                novelty,editor,strategist,computational,reproducibility}.txt
└── tests/
    ├── helpers.py
    ├── test_ingestion.py
    ├── test_rules.py
    ├── test_contracts.py
    ├── test_comparison.py
    ├── test_schema.py
    ├── test_llm_grounding.py
    ├── test_openai_provider.py
    ├── test_llm_cli.py
    ├── test_semantic_comparison.py
    ├── test_benchmark.py
    └── test_cli.py
```

## Module boundaries

`ingestion` normalizes source blocks and records document identity, section,
PDF page, text line, or DOCX paragraph/row ordinal. PDF line numbers refer to
extracted page text, not visual layout. DOCX paragraphs and table rows share
one ordinal counter. Unknown styled/Markdown subheadings retain their recognized
parent section.

`extraction` returns candidates with evidence. Cohort mentions are not resolved
identities; sample-size mentions are not inferred independent sample sizes.
Figure/table links use shared labels only. References and acknowledgments are
excluded from substantive extraction and rules.

`rules/catalogue.py` contains the rubric as inspectable data.
`rules/engine.py` applies sentence/clause negation and future-work guards.
Missing reporting carries search scope and contextual anchors, not fabricated
evidence of absence. An affirmative split cue can coexist with a leakage concern
when feature selection happens before that split.

`prioritization` produces editable, explained ordinal tiers.

`reviewers` routes findings into distinct mandates in offline mode. The hostile
role reformulates high-priority findings as questions. It is not eight independent
scientific reviews. Prompt packets separate instructions from untrusted source
text. Legacy injected providers retain their list contract; the OpenAI adapter
uses contract version 2 with strict findings, claims, strengths, and limitations.
Six default LLM roles are distinct; four additional roles remain selectable.
Every role sees the same static baseline, so exact dry-run requests need no
invented upstream responses. No reviewer output becomes another reviewer's input.

`providers/openai.py` sends explicitly configured Responses API requests.
Credentials come only from the environment at send time; request exports contain
no credentials. Requests disable storage and truncation, expose output/context
limits, enable no tools, refuse redirects, and do not retry automatically.
Model-specific settings are never inferred from a hard-coded model name.

`grounding.py` resolves exact, unique excerpts into locally derived locations,
separates factual premises from interpretations, flags obvious support problems,
and quarantines ungrounded/external claims. It is not a general entailment model.
Unknown fields, invented citations, or automatic fatal/established judgments
reject a role's response while retaining the deterministic review. Duplicates
preserve originals and disagreements; deterministic findings remain independent.

`adversarial.py` ranks source-anchored claims and prioritizes up to seven major
threats. LLM scientific assessments take precedence over clearly labeled offline
claim templates. Action templates are conditional proposals, not reported work.

`comparison` matches text within logical source/section groups, aligns similar
claims, compares stable rule-family IDs, and looks for explicit remediation cues.
It never treats disappearing text as verified scientific resolution. Reporting
resolution, described design corrections, and verified execution are separate.
`resolution.py` adds six-state assessments with separate old/new evidence.
Paired LLM mode makes one static comparison request. An explicitly supplied
saved prior review can contribute prior LLM concerns after hash/provenance
validation. A paired run does not silently rerun every reviewer on both versions.

`reporting` presents claim-centered analysis before a collapsible appendix
containing the original 20 sections, all findings, and the deterministic checklist.
Unverified opinions and external claims are kept separate from headline concerns.

## Provenance and repeatability

Documents have logical IDs (`manuscript`, `supplement-1`, etc.) and content hashes.
Block IDs derive from logical document, section, normalized text, and occurrence.
Evidence uses exact `[start, end)` character spans. Findings use stable rule-family
IDs; multiple instances are aggregated (up to eight displayed evidence spans).
Run IDs and timestamps are unique.

Overrides require exact hashes of all inputs. Section corrections precede
extraction; finding corrections precede reviewer routing. Dismissed findings
remain auditable. JSON records configuration and applied overrides.

## Resource and error boundaries

Files are limited to 50 MB, DOCX main XML to 30 MB decompressed, PDFs to 1,000
pages, and normalized text to 5 million characters. Empty extraction, unsupported
types, protected PDFs, invalid XML/ZIP/UTF-8, malformed configuration, and stale
overrides produce actionable errors. Archives are not unpacked onto disk.
DOCX XML entity declarations are rejected.

These limits support ordinary local files; they are not a hardened sandbox for
hostile PDFs. Parsing can consume substantial memory/CPU. Full text and prompt
packets are held in memory and stored locally. Output writes are atomic per file,
not globally transactional.

## Pilot workflow additions (0.3)

The existing pipeline and deterministic catalogue remain in place. Three small
local modules add workflow boundaries without a service or new reviewer role:

- evaluation.py prepares neutral randomized review arms, a separate private
  assignment key, CSV/JSON adjudication forms, and descriptive human-score
  summaries. Inputs must have identical source registries and configuration.
  Only a completed form unblinds the score result.
- exchange.py selects a bounded set of findings/claims/excerpts for a manual
  ChatGPT conversation. Reconstructed package identity, original-file hashes,
  excerpt scope, response schema, and existing grounding checks precede import.
  Candidates remain quarantined by default; explicit acceptance cannot bypass
  failed scientific support checks.
- diagnostics.py summarizes local call/usage records and finding dispositions.
  Response usage is captured before output acceptance, so rejected outputs are
  not mistaken for free calls. No pricing query or telemetry is introduced.

Reporting adds a compact revision brief before collapsible claim details and
the original audit. Comparison rows carry prior severity so a major-concern
summary can separate persistent, unclear, resolved, worsened, scope-withdrawn,
and newly detected issues without changing the underlying six-state contract.

Scientific support guards remain deliberately narrow. New checks catch some
invented design/unit claims, association-to-causation promotion, unsupported
control absence, literature assertions, and analyses requiring explicitly
unavailable data. They do not constitute an entailment or feasibility oracle.

## Future growth

Validate live model behavior on explicitly consented synthetic inputs; broaden
the benchmark with independent human adjudication; improve semantic support
verification, OCR/layout, figure/table provenance, and cohort identity resolution.
