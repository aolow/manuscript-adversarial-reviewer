# Data safety

The source repository is public. Real manuscript content should not be committed here.

Keep the following outside source control:

- Unpublished or confidential manuscripts and supplements.
- Generated provider request packets.
- Review outputs that contain manuscript text.
- API keys, AWS credentials, tokens, and private configuration.
- Human evaluation keys or private adjudication material.

A normal offline review does not contact an external provider.

A live command using `--llm` sends extracted manuscript content to the provider you selected. Use it only when you are authorized to share that material with that provider and account.

`--dry-run` is the safest way to inspect the exact request before any upload:

```bash
manuscript-review review manuscript.pdf \
  --llm --provider bedrock \
  --model MODEL_OR_PROFILE \
  --region us-west-2 \
  --dry-run --out reviews/preview
```

Bedrock uses the standard AWS credential chain. OpenAI reads `OPENAI_API_KEY` from the process environment. Credentials are not written into request exports or reports.

Provider validation diagnostics are intentionally narrow. Container/schema failures and per-item rejections record safe paths, validator/rejection categories, and normalized field names, not rejected model values or manuscript text. This does **not** make provider artifacts non-sensitive: request exports, grounded evidence, reports, and other review outputs can still contain manuscript content.

Bedrock transport is configured without automatic retry. A timeout or provider failure therefore does not silently trigger a duplicate long-running manuscript submission from this tool.

Ignore rules reduce accidental commits but cannot recognize every confidential file. Always inspect staged files before pushing.
