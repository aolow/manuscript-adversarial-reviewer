# Changelog

## Unreleased

- Simplified the documentation around a concise README and focused workflow,
  architecture, rubric, schema, evaluation, ChatGPT, and data-safety guides.
- Removed historical development, readiness, adjudication, and self-audit documents
  from the repository root; their history remains available in Git.
- Added Amazon Bedrock Converse as a second explicit LLM provider, using JSON
  Schema structured output and the standard AWS credential chain.
- Added provider-specific region, timeout, temperature, dry-run, usage, and
  failure handling without changing the offline deterministic review path.
- Updated repository publication guidance now that the source repository is public.

## 0.3.0 — 2026-10-04

- Preserved the v0.2.0 deterministic engine and reviewer roster.
- Added a short pilot guide and a compact report opening focused on revision decisions.
- Added local blinded evaluation with optional expert arm, individual concern
  classifications, CSV/JSON human forms, missed-issue inventory, and descriptive scoring.
- Added compact export-chatgpt and locally validated import-chatgpt commands;
  imports stage candidates until explicitly accepted where eligible.
- Added diagnostics for attempts, failures, known usage, incomplete roles, raw
  findings, accepted/quarantined concerns, duplicates, and headline counts.
- Added a realistic fictional manuscript and scientific failure-mode tests.
- No real OpenAI review, human-quality adjudication, telemetry, connector, remote,
  commit, or publication occurred.

## 0.2.0 — 2026-10-04

- Explicit opt-in OpenAI Responses reviewer with configurable model, optional
  temperature/reasoning settings, bounded requests, no retries/tools, and exact
  no-network dry-run exports.
- Six default adversarial roles, plus four optional roles; existing offline
  routing and legacy provider contract retained.
- Strict provider schemas, exact quote resolution, locally derived locations,
  premise/interpretation separation, support flags, and low-confidence quarantine.
- Claim-level alternatives, falsification plans, decisive analyses, strengths,
  and a short central-story report ahead of the original detailed audit.
- Provider duplicate grouping with preserved ratings and severity disagreements.
- Six-state concern resolution, two-version evidence validation, and hash-bound
  import of prior scientific/LLM review findings.
- Six-case synthetic benchmark with separate deterministic/LLM scoring and an
  explicitly retained paraphrased-leakage false negative.
- Portable paths, private-project notice, stricter ignored output/secret paths,
  and credential-free environment-variable examples.
- Report schema 1.1.0; no live manuscript API calls made during development.

## 0.1.0 — 2026-10-04

- Local PDF, DOCX, Markdown, and text ingestion with section/source provenance.
- Candidate claims, methods, cohorts, statistics, and figure/table references.
- 46 reporting checks and 10 narrow scientific/design pattern rules.
- Separate severity, issue status, confidence, and ordinal priority.
- Version-bound overrides and strict configuration validation.
- Eight reviewer mandates, reusable prompts, local export, and provider protocol.
- Twenty-section Markdown/JSON reports with stable finding-family IDs.
- Version comparison separating reporting updates, described corrections, and
  disappearing flags without resolution evidence.
- Synthetic fixtures, unit/end-to-end regressions, schemas, examples, self-audit.

Version 0.1.0 included no live API client, OCR, visual figure analysis, raw-data
analysis, literature retrieval, or cloud infrastructure.
