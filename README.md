# Manuscript adversarial review

A local-first Python CLI for stress-testing scientific manuscripts before submission or revision.

The default workflow is fully offline. It extracts manuscript structure, runs deterministic reporting and design checks, prioritizes concerns, and produces Markdown and JSON reports. Optional LLM review can use either OpenAI or Amazon Bedrock.

This tool supports scientific judgment. It does not verify that a manuscript is correct, execute analyses, inspect raw data, or replace expert review.

## What it does

- Reads PDF, DOCX, Markdown, and UTF-8 text, with optional supplements.
- Flags reporting gaps and selected design risks such as leakage, pseudoreplication, circularity, confounding, and overclaiming.
- Grounds concerns to exact manuscript excerpts.
- Adds optional LLM reviewers for scientific, methods, computational, novelty, reproducibility, and adversarial review.
- Compares manuscript versions and tracks whether prior concerns appear resolved, persistent, worsened, or out of scope.
- Produces a concise revision brief plus a detailed auditable report.
- Supports blinded local evaluation of assisted versus deterministic review.

## Install

```bash
git clone https://github.com/aolow/manuscript-adversarial-reviewer.git
cd manuscript-adversarial-reviewer

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[pdf,llm,test]"
```

Run the tests:

```bash
python -m unittest discover -s tests -t . -v
```

Amazon Bedrock live mode also needs Python 3.10+ and boto3:

```bash
python -m pip install -e ".[bedrock]"
```

## Quick start

### Offline review

No API key or cloud account is needed.

```bash
manuscript-review review manuscript.pdf --out reviews/manuscript-v1
```

Add supplements as needed:

```bash
manuscript-review review manuscript.pdf \
  --supplement supplement.pdf \
  --out reviews/manuscript-v1
```

The main outputs are:

- `report.md`, the human-readable review.
- `report.json`, the structured audit record.

### Preview an LLM request without sending anything

Use `--dry-run` before a live provider call:

```bash
manuscript-review review manuscript.pdf \
  --llm --provider openai --model MODEL_NAME \
  --dry-run --out reviews/preview
```

The exact provider requests are written under `requests/`. Dry-run mode does not contact the provider.

## LLM providers

LLM use is always explicit through `--llm`. Offline review remains the default even if credentials are present.

### OpenAI

Set `OPENAI_API_KEY` in your environment, then run:

```bash
manuscript-review review manuscript.pdf \
  --llm --provider openai --model MODEL_NAME \
  --out reviews/openai-review
```

### Amazon Bedrock

Authenticate through your normal AWS or corporate SSO workflow. The project uses the standard AWS credential chain and does not store AWS credentials.

```bash
manuscript-review review manuscript.pdf \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --out reviews/bedrock-review
```

Bedrock uses the Converse API with a forced schema tool by default. The tool arguments are the structured review payload, which is then validated against the full local schema. Review responses are bounded to 10 findings and 6 claims; Bedrock defaults to 24,000 output tokens and a 600-second read timeout for full manuscripts. If a model does not support forced tool choice, use `--bedrock-json-mode prompt`; that fallback asks for JSON in the prompt and still rejects malformed or schema-invalid output without retrying.

### Common settings

| Option | Purpose |
| --- | --- |
| `--model` | Required provider model or Bedrock inference-profile ID |
| `--roles` | Comma-separated reviewer roles instead of the default six |
| `--temperature` | Optional sampling temperature |
| `--reasoning-effort` | Optional model reasoning setting when supported; Bedrock requires `--bedrock-json-mode prompt` when effort is enabled |
| `--bedrock-json-mode` | Bedrock only: `tool` (default) or `prompt` fallback |
| `--max-output-tokens` | Output limit per request; defaults to 24,000 for Bedrock and 6,000 for OpenAI |
| `--max-request-chars` | Local request-size guard |
| `--timeout` | Provider timeout; defaults to 600 seconds for Bedrock and 60 seconds for OpenAI |
| `--dry-run` | Build and save exact requests without sending them |

Environment fallbacks include `MANUSCRIPT_REVIEW_MODEL`, `MANUSCRIPT_REVIEW_TEMPERATURE`, `MANUSCRIPT_REVIEW_REASONING_EFFORT`, `MANUSCRIPT_REVIEW_BEDROCK_JSON_MODE`, and `MANUSCRIPT_REVIEW_AWS_REGION`.

The default LLM roles are scientific, methods, computational, novelty, Reviewer 2, and reproducibility. Additional selectable roles include statistics, clinical, editor, and strategist.

## How the reviewer panel works

The LLM mode is a **panel of focused reviewers**, not one model call that repeatedly critiques its own previous answer. Each selected role receives the same static manuscript source blocks, extracted candidate claims, deterministic review leads, target journal name if supplied, and a role-specific mandate. Roles are called independently. Output from the scientific reviewer is not shown to Reviewer 2, for example, and agreement between roles is therefore useful as convergence but is not treated as independent experimental evidence.

The default six-role panel is intended to cover complementary failure modes:

| Role | Main question | Typical focus |
| --- | --- | --- |
| **scientific** | Do the central biological/scientific conclusions follow from the reported evidence? | Central claims, alternative explanations, perturbational support, biological interpretation, mechanism versus association, transferability, biomarker interpretation |
| **methods** | Is the experimental and analytical design capable of answering the question? | Cohorts, independent units, controls, preprocessing, train/test separation, single-cell design, confounding, effective replication, uncertainty |
| **computational** | Could information leakage, representation choice, or computational dependence create the result? | Feature definition, embeddings, atlas/reference dependence, integration, tuning, baselines, nulls, ablations, held-out evaluation |
| **novelty** | What is actually new, and how strongly can that novelty be claimed from the manuscript alone? | Contribution type, comparator choice, scope, positioning, prior-art questions that require later literature verification |
| **reviewer2** | What would a skeptical reviewer attack in the paper's strongest claims? | Falsification tests, competing explanations, hidden selection, circular validation, optimistic metrics, claim-breaking evidence |
| **reproducibility** | Could another group reconstruct the cohort and analysis without private knowledge? | Code/data provenance, software versions, parameters, exclusions, seeds, manual decisions, reference choices, executable procedures |

Optional roles can be selected with `--roles` when they are useful:

| Role | Use it when |
| --- | --- |
| **statistics** | The paper needs a dedicated audit of estimands, dependence, multiplicity, uncertainty, calibration, censoring, grouped/nested validation, or statistical assumptions. Methods already covers some statistics in the default panel, so this role is intentionally extra depth. |
| **clinical** | The manuscript makes translational, biomarker, treatment-prediction, endpoint, external-validation, or clinical-utility claims. |
| **editor** | You want submission-readiness triage: significance, evidential maturity, audience, framing, and likely editorial-confidence blockers. It does not predict acceptance. |
| **strategist** | You want the concerns converted into an ordered revision strategy, separating essential design/reanalysis work from reporting fixes and optional strengthening. |

For example, a computational biomarker manuscript might use:

```bash
manuscript-review review manuscript.md \
  --llm --provider bedrock --model MODEL --region REGION \
  --roles scientific,methods,computational,statistics,clinical,reviewer2 \
  --out reviews/assisted
```

### What happens to a reviewer response

A provider response does **not** enter the report just because the model returned JSON. Validation happens in a strict order:

1. **Whole-response schema validation.** The complete response must match the structured review contract before grounding begins. A normal review is bounded to at most 10 findings and 6 claim analyses per role. This gate is currently atomic: one malformed required field or invalid ID can reject the whole role. Diagnostics record only the safe schema path and validator, not the rejected model text.
2. **Claim grounding.** Claim evidence must resolve to real manuscript excerpts. Reviewer-written claim summaries may be paraphrases. A bad claim is dropped without discarding independently grounded findings from the role.
3. **Finding grounding.** Model citations are checked against the supplied source blocks one citation at a time. Invalid citations are filtered individually. A finding survives if at least one supplied citation resolves; a finding whose supplied citations all fail is dropped without aborting the role.
4. **Claim-link isolation.** Finding-to-claim references are resolved after claim grounding. Links to rejected claims are removed, and truly unknown claim IDs are dropped with a `dangling_claim_ref_dropped` quality flag rather than aborting the finding.
5. **Strength grounding.** Strength citations must resolve to manuscript evidence. An invalid or empty strength is skipped by itself and cannot erase the role's findings, claims, or other valid strengths.
6. **Support audit.** Exact quotation proves only that text exists in the manuscript. It does not prove the reviewer's interpretation. Weakly supported, externally dependent, overly certain, or otherwise questionable interpretations are marked for semantic/human review and given conservative confidence.
7. **Action audit.** Major concerns are expected to propose a concrete analysis, experiment, text change, or reporting action. Vague, incomplete, or apparently infeasible actions are flagged.
8. **Reconciliation.** Similar concerns from different reviewers can be grouped as duplicates. Multiple reviewers making the same criticism does not convert that criticism into verified scientific truth.
9. **Prioritization and report assembly.** The final adversarial summary emphasizes a small number of consequential, source-grounded concerns. The headline section is capped at seven rather than padding the report with weak issues.

### Reading the output

Provider findings have several possible outcomes. **Active/confirmed** findings passed the local grounding gates and are eligible for the main report, but their scientific interpretation still requires human judgment. **Needs review** findings are retained but quarantined because grounding, semantics, action quality, or confidence is insufficient. **Duplicate** findings remain auditable but are grouped under another concern. Findings with unusable supplied citations may be dropped at grounding rather than contaminating the rest of the role.

This distinction is important: `schema_accepted` means the provider returned a structurally valid response. It does **not** mean every returned claim, finding, or strength survived grounding. Conversely, `schema_rejected` means the role never reached the per-item isolation layer, so one malformed element can still zero that role. `llm-run.json` and the pilot diagnostics show provider-call status, safe schema-error metadata, raw finding counts, accepted/quarantined counts, and known rejections.

The deterministic review always remains the baseline. If an LLM role fails, its generated output is not substituted with guesses, and the deterministic findings are preserved.

## Compare revisions

Compare two manuscript versions offline:

```bash
manuscript-review compare manuscript-v1.docx manuscript-v2.docx \
  --out reviews/v1-v2
```

To include the prior assisted review and one semantic comparison call:

```bash
manuscript-review compare manuscript-v1.docx manuscript-v2.docx \
  --prior-review reviews/manuscript-v1/report.json \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --out reviews/v1-v2
```

The comparison distinguishes reported resolution from verified execution. A manuscript saying that an analysis was performed is not proof that it was performed correctly.

## Manual ChatGPT handoff

You can create a compact local package for a normal ChatGPT conversation:

```bash
manuscript-review export-chatgpt reviews/manuscript-v1/report.json \
  --out handoffs/manuscript-v1
```

Nothing is uploaded automatically. See [CHATGPT_WORKFLOW.md](CHATGPT_WORKFLOW.md) for optional structured feedback import.

## Evaluate whether LLM assistance helps

The project can prepare a blinded A/B comparison between deterministic and assisted reviews:

```bash
manuscript-review evaluate prepare \
  --baseline reviews/baseline/report.json \
  --assisted reviews/assisted/report.json \
  --out evaluations/pilot
```

See [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md) for the adjudication and scoring workflow.

## Important limits

The tool does not currently:

- Interpret figure images or scanned PDFs without prior OCR.
- Verify raw data, analysis code, or whether proposed analyses were actually run.
- Search the scientific literature or current journal policies.
- Establish semantic truth merely because a quote exists.
- Treat multiple LLM reviewers as independent scientific confirmation.
- Partially salvage a provider response that fails the top-level JSON Schema gate; per-item isolation begins only after schema acceptance.

Provider output is schema-checked and source-grounded locally, but scientific conclusions still require human judgment.

## Data safety

Real manuscripts, provider request files, credentials, and private review outputs should stay outside source control. A live `--llm` run sends extracted manuscript content to the selected provider.

See [DATA_SAFETY.md](DATA_SAFETY.md) before using confidential or unpublished material.

## Documentation

- [PILOT_GUIDE.md](PILOT_GUIDE.md), recommended end-to-end workflow.
- [ARCHITECTURE.md](ARCHITECTURE.md), implementation and trust boundaries.
- [REVIEW_RUBRIC.md](REVIEW_RUBRIC.md), severity and reviewer logic.
- [SCHEMA.md](SCHEMA.md), report contracts and provenance fields.
- [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md), blinded evaluation.
- [CHATGPT_WORKFLOW.md](CHATGPT_WORKFLOW.md), manual ChatGPT exchange.
- [EXAMPLE_REPORT.md](EXAMPLE_REPORT.md), full generated example.
- [CHANGELOG.md](CHANGELOG.md), release history.

No open-source license is currently granted. Copyright remains with the project owner.
