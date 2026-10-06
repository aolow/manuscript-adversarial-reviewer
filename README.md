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
