# One paper through one revision

Run these commands from the project folder. Keep the original manuscript as
manuscripts/pilot-v1.pdf and save the revision separately as manuscripts/pilot-v2.pdf.
DOCX and Markdown also work: change the filenames consistently.

For OpenAI review, set OPENAI_API_KEY privately in your process environment and
set MANUSCRIPT_REVIEW_MODEL to your chosen supported model. There is no default
model. See [configuration](README.md#settings-and-limits) if needed.

## 1. Preview what would be sent

    .venv/bin/manuscript-review review manuscripts/pilot-v1.pdf --llm --dry-run --out reviews/pilot-preview

Open the exported requests to check extraction, scope, and included supplements.
This command sends nothing and needs no key. For an entirely offline review,
omit --llm and --dry-run.

## 2. Review and save V1

Run this only when you intend to send the extracted manuscript to OpenAI and
incur charges. The default is six reviewer calls.

    .venv/bin/manuscript-review review manuscripts/pilot-v1.pdf --llm --provider openai --out reviews/pilot-v1

Read reviews/pilot-v1/report.md. Start with the revision brief: claims,
contributions, central threats, decisive analyses, text edits, and Reviewer 2.
Keep report.json; it is the record used for comparison and handoff.

Check diagnostics.json for failed/incomplete roles, accepted versus quarantined
concerns, and known token usage. Exit 3 means incomplete model review; the
deterministic report is still available. Do not interpret an incomplete run as
an all-clear. A quoted passage is not proof that the criticism is scientifically sound.

If supplements matter, add --supplement manuscripts/supplement-v1.pdf.

## 3. Revise the paper

Save V2 as a new file. Keep V1 and its review. Address scientific concerns with
evidence or justified limitations; softer language alone does not repair design.

## 4. Compare V1 and V2

    .venv/bin/manuscript-review compare manuscripts/pilot-v1.pdf manuscripts/pilot-v2.pdf --prior-review reviews/pilot-v1/report.json --llm --out reviews/pilot-v1-v2

This sends both versions in one comparison request. Add --dry-run first to
inspect it. Use --old-supplement and --new-supplement when applicable.

Read reviews/pilot-v1-v2/comparison.md. Its first section groups major concerns
as resolved, partially resolved, persistent, worsened, unclear, or newly detected.
A withdrawn claim is shown separately; it is not a repaired method.

“Resolved” describes what the text supports, not proof that an analysis ran.
New concerns in this paired workflow come from the deterministic V2 audit;
it does not perform six fresh LLM reviews of V2. A newly detected issue may have
been newly disclosed or previously missed.

## 5. Continue in a normal ChatGPT conversation

    .venv/bin/manuscript-review export-chatgpt reviews/pilot-v1-v2/report.json --out handoffs/pilot-v2

Upload **handoffs/pilot-v2/chatgpt-review.json** only. It contains selected
findings, claim analyses, exact excerpts, and comparison state. Paste the short
prompt from handoffs/pilot-v2/CHATGPT_PROMPT.md. Uploading is your decision; the
command only writes local files.

The package is selected context, not the complete manuscript. Do not treat
missing context as missing work. Keep request files, diagnostics, and evaluation
keys locally.

For structured feedback import, see [CHATGPT_WORKFLOW.md](CHATGPT_WORKFLOW.md).
To find out whether the LLM review helps more than the baseline, use the
[blinded evaluation workflow](EVALUATION_GUIDE.md). No human ratings or live
model-quality results are claimed yet.
