# Report schema 1.1.0

The package includes `report.schema.json` and `comparison.schema.json` (JSON
Schema draft 2020-12). Regenerate after model changes with
`PYTHONPATH=src python3 scripts/generate_schema.py`.
`validation.validate_report` additionally checks exact source spans, unique
finding/block IDs, classifications, and finding references.

## Stable top-level review fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Semantic version of the report contract |
| `tool_version` | Implementation version |
| `run_id`, `created_at` | Unique identity and UTC ISO timestamp |
| `target_journal` | Supplied name or null; no inferred policies |
| `documents` | Logical IDs, role, name, path, hash, format, blocks, warnings |
| `extraction` | Claims, methods, cohorts, statistics, references, domains, links, limits |
| `findings` | All concerns, including dismissed findings |
| `checklist` | Check outcomes, evidence, and searched scope |
| `reviewer_runs` | Mandates, mode, routed findings, questions, limits |
| `sections` | Exactly 20 ordered report sections |
| `warnings` | Extraction, coverage, and interpretation warnings |
| `configuration` | Rule/domain configuration and applied overrides |
| `comparison` | Optional comparison object; otherwise null |
| `claim_analyses` | Ranked claims, exact evidence, alternatives, falsification and decisive analyses |
| `adversarial` | Headline concerns, strengths, analysis priorities, framing, and quarantined suggestions |
| `quality` | Failed roles, duplicate groups, and explicit semantic-verification limit |
| `llm` | Provider settings, request counts, receipts, dry-run mode; never credentials |

Extraction's stable keys are `domains`, `claims`, `methods`, `cohorts`,
`statistical_methods`, `figure_table_references`, `claim_evidence_map`, and
`limitations`. A cohort record includes `sample_size_mentions`, not a claim of
unique participants. Full normalized source text remains in `documents`.

## Finding contract

| Field | Meaning |
| --- | --- |
| `id` | Stable family ID, e.g. `pattern.cell_pseudoreplication` |
| `rule_id` | Catalogue ID or provider role ID |
| `severity` | `fatal_flaw`, `major`, `moderate`, `minor`, `optional_strengthening` |
| `category` | Scientific/design/reporting category |
| `manuscript_section` | Section of the first anchor |
| `claim` | Exact first quoted context; may be a methods passage |
| `issue`, `why_it_matters` | Concern and rationale |
| `evidence` | Exact source spans |
| `suggested_fix`, `suggested_analysis` | Conditional proposed actions |
| `confidence` | `low`, `medium`, `high`: text-match confidence |
| `issue_status` | `established_issue`, `plausible_issue`, `speculative_concern` |
| `reviewer_roles` | Relevant reviewer mandates |
| `origin` | `deterministic` or `provider:<name>` |
| `priority`, `priority_rationale` | Ordinal tier and explanation |
| `reviewer_likelihood`, `effort`, `value` | Editable ordinal estimates |
| `disposition` | `active`, `dismissed`, `confirmed`, `needs_review`, `duplicate` |
| `manual_note` | Rationale for a manual change; otherwise null |
| `limitation` | Scope and uncertainty |
| `basis` | `manuscript_direct`, `manuscript_inference`, `external_claim`, `reviewer_opinion` |
| `grounding_status` | `source_verified`, `needs_semantic_review`, `ungrounded`, `external_unverified` |
| `evidence_statement`, `support_rationale` | Factual premise and connection from source to interpretation |
| `topic`, `claim_ids` | Concern topic and linked claims; heuristic links are labeled |
| `action` | Input/comparison/held-out unit/metric/interpretation or section/claim/framing |
| `quality_flags` | Specific support, action, certainty, and disagreement flags |
| `duplicate_of`, `reviewer_assessments` | Canonical finding and retained original reviewer ratings |

IDs aggregate a concern family, not a unique experiment. A flag can persist while
some instances are repaired. Do not repurpose IDs for materially different checks.

## Evidence contract

Every evidence object has `document_id`, `block_id`, `section`, `quote`,
`start`, `end`, `relation`, `page`, `line_start`, and `paragraph`. Offsets use
Python character indices into the normalized block; `end` is exclusive.
The runtime validator requires `quote == block.text[start:end]`.
It also checks section, page, paragraph, and line against the source. The model
supplies only `block_id` and a unique exact `quote`; all other locations are
derived locally. Empty evidence is allowed only for appropriately low-confidence,
quarantined provider output; it is not filled with invented contextual quotes.

Relations are `trigger`, `context_only`, `candidate_support`, or
`reported_result`. A contextual quote for a gap is not proof of absence.
Page/line/paragraph fields are nullable. Blocks also include `line_end`, `kind`,
and `extraction_confidence`. Hashes identify original bytes; quotes can reflect
reader normalization.

## Checklist statuses

- `reported`: affirmative text detected; adequacy unverified.
- `not_established`: no affirmative or explicit negative cue.
- `explicit_negative_statement`: negative cue matched.
- `conflicting`: affirmative and negative cues coexist.
- `not_applicable`: applicability domain not detected.

Entries record searched document IDs, block count, evidence, confidence, domain,
and interpretation.

## Comparison contract

Fields include old/new run IDs and document hashes, `substantive_changes`,
`claims_strengthened`, `claims_weakened`, `concerns_resolved`,
`reported_remediation`, `concerns_unresolved`, `new_concerns`,
`no_longer_detected`, `rigor_assessment`, `positioning_assessment`, and
`limitations`, plus its own `schema_version`.
Version 1.1 adds `issue_assessments` and `llm`. Every prior active issue receives
exactly one assessment with `prior_issue_id`, `status`, `rationale`,
`old_evidence`, `new_evidence`, `resolution_scope`, `execution_verified`,
`wording_softened_only`, `remaining_action`, `confidence`, `origin`, and
`quality_flags`. Status is resolved, partially_resolved, unresolved, worsened,
no_longer_applicable, or cannot_determine. `execution_verified` is always false.

`concerns_resolved` means a **reporting** concern gained an affirmative cue:
`resolution_scope` is `reporting_only` and `scientific_resolution` is
`not_verified`. `reported_remediation` uses `reported_design_only`.
Neither verifies underlying analyses. Claim changes measure wording, not evidence.

Comparison citations can refer to either input review; resolve them against
`prior-report.json` and the new `report.json`.

## LLM contracts and backward compatibility

`llm-response.schema.json` and `llm-comparison-response.schema.json` are strict
provider-output contracts. Every object rejects extra fields. They are used both
in the API's structured-output request and in independent local validation.
API schema conformance is not trusted without the local check.

Provider `issue_key` maps a concern to a known deterministic rubric ID for
benchmarking, or `other`; it does not turn a model judgment into a deterministic
result. `origin` always preserves the distinction.

The original 20-section `sections` array and original field meanings remain.
Version 1.1 adds fields and disposition values; consumers should branch on schema
version. Saved prior review import requires 1.1 and exact input hashes. Regenerate
older 1.0 reports with the current CLI before importing; no silent migration is
performed. Original legacy provider implementations retain their list contract.

## Compatibility

Version 0.3 of the application keeps report schema 1.1.0. Pilot additions live
inside existing extensible objects:

- quality.pilot_diagnostics: call/failure/usage and finding-disposition counts.
- llm.calls: per-attempt role, status, request hash/size, elapsed seconds, and
  raw count when parseable. Receipts include known usage even after rejection.
- Comparison assessment rows add prior_severity and issue; newly detected rows
  add severity and issue. Legacy rows remain readable but cannot supply a
  complete major-only summary without regeneration.
- reviewer_runs may record manual_import using the existing Reviewer 2 role.
  Proposed claims/strengths are separate from accepted ones. Manual findings
  retain provider:chatgpt_manual origin and explicit staging/acceptance metadata.

ChatGPT package_version 1.0 is a separate compact exchange envelope, not a new
report schema. Feedback requires its exact package_id and the existing strict
REVIEW_SCHEMA. Evaluation artifacts are local, randomly assigned and bound by
digests; the adjudication form records subjective ratings, not engine findings.

Keep field and enum meanings stable within schema major version 1. New rules
can generate new concerns; compare `tool_version`, configuration, and hashes
before interpreting count changes. Consumers should use IDs and named fields.
Incompatible field/meaning changes require a schema major version bump.
