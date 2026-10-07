# Recommended workflow

This is the shortest path from a manuscript to a reviewed revision.

Examples below use PDF files, but DOCX, Markdown, and text are also supported.

## 1. Run the offline review

```bash
manuscript-review review manuscript-v1.pdf --out reviews/v1-baseline
```

Read `report.md`. This gives you the deterministic review without sending content anywhere.

## 2. Preview the LLM request

Choose the provider you intend to use and add `--dry-run`.

OpenAI:

```bash
manuscript-review review manuscript-v1.pdf \
  --llm --provider openai --model MODEL_NAME \
  --dry-run --out reviews/v1-preview
```

Bedrock:

```bash
manuscript-review review manuscript-v1.pdf \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --dry-run --out reviews/v1-preview
```

Inspect the files under `requests/`. Dry-run mode sends nothing.

## 3. Run the assisted review

Remove `--dry-run` when you are comfortable sending the extracted manuscript to the selected provider.

```bash
manuscript-review review manuscript-v1.pdf \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --out reviews/v1-assisted
```

For OpenAI, substitute `--provider openai --model MODEL_NAME`.

Start with the revision brief in `report.md`. Keep `report.json`, it is the structured record used by comparison and evaluation workflows.

Also inspect the provider diagnostics before interpreting role coverage. A `schema_accepted` role may still lose individual claims, findings, claim links, or strengths during local grounding. Those failures are isolated after schema acceptance so valid role output can survive. By contrast, `schema_rejected` is a whole-role failure because the current response schema gate is atomic; one malformed required field or invalid ID can reject the response before grounding begins.

If the command exits with status 3, some LLM roles failed or were rejected. The deterministic review is still valid, but the assisted review is incomplete. Do not treat missing findings from a failed role as evidence that the manuscript has no issue in that area.

For full-length PDFs, extracted text can be noisier than clean Markdown, especially with two-column order, line annotations, whitespace, or Unicode normalization. Exact quote validation remains strict, but once a role has passed schema validation, a bad claim citation, individual finding citation, dangling claim reference, or strength citation is isolated rather than allowed to erase unrelated grounded output.

## 4. Revise the manuscript

Save the revision as a new file. Do not overwrite V1.

Treat suggested analyses as proposals, not mandatory work. Verify consequential concerns against the manuscript and the underlying science.

## 5. Compare V1 and V2

Offline:

```bash
manuscript-review compare manuscript-v1.pdf manuscript-v2.pdf \
  --out reviews/v1-v2
```

With one provider-assisted comparison:

```bash
manuscript-review compare manuscript-v1.pdf manuscript-v2.pdf \
  --prior-review reviews/v1-assisted/report.json \
  --llm --provider bedrock \
  --model BEDROCK_MODEL_OR_INFERENCE_PROFILE \
  --region us-west-2 \
  --out reviews/v1-v2
```

Use `--dry-run` first if you want to inspect the paired request.

Read `comparison.md` for resolved, partially resolved, persistent, worsened, unclear, and newly detected concerns.

A reported fix is not verified execution. Softer wording also does not repair a design problem.

## Optional next steps

To continue in ChatGPT:

```bash
manuscript-review export-chatgpt reviews/v1-v2/report.json --out handoffs/v2
```

See [CHATGPT_WORKFLOW.md](CHATGPT_WORKFLOW.md).

To test whether assisted review is actually more useful than the deterministic baseline, see [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md).
