# Manual ChatGPT handoff

Export a saved review locally:

    .venv/bin/manuscript-review export-chatgpt reviews/pilot-v1/report.json --out handoffs/pilot-v1

Upload only handoffs/pilot-v1/chatgpt-review.json in the conversation where you
want to continue. The accompanying CHATGPT_PROMPT.md gives a short prompt to
paste. No upload, connector, or external service is started by this project.

The package includes at most 15 active findings by default, five ranked claims,
selected exact evidence excerpts with stable IDs, central threats, analysis
plans, and available revision state. It excludes credentials, model request
logs, usage receipts, full source registries, and discarded/quarantined findings.
Omission counts and excerpt truncation are explicit. Use --max-findings N to
include up to 50 concerns. A 250 KB ceiling prevents an accidental large dump.

The model must not infer absence from omitted text. Old-version quotations are
omitted; comparison state is supplied for discussion, not fresh adjudication.
A package ID and source-review digest bind feedback to this exact export.

## Bring structured feedback back locally

Ask ChatGPT to return one JSON object following feedback_schema in the package,
without Markdown fences. Save it locally as feedback.json. The wrapper contains
package_id and review; review uses the existing finding/claim/strength contract.
The schema is embedded, so there is no second schema attachment.

    .venv/bin/manuscript-review import-chatgpt reviews/pilot-v1/report.json feedback.json --context handoffs/pilot-v1/chatgpt-review.json --manuscript manuscripts/pilot-v1.pdf --out reviews/pilot-v1-feedback

Include the original --supplement arguments where needed. Import verifies the
original source hashes and extracted text, reconstructs the expected export,
validates the feedback schema, checks citations against the excerpts actually
shared, and applies the same grounding and action checks as API output.

Default import stages all new findings with needs_review disposition and low
confidence. They do not enter the headline list. Proposed claims and strengths
are retained for inspection without replacing the active analysis.
The original review and manuscript are never modified.

After inspecting the candidate report, you may explicitly activate eligible
feedback by rerunning from the ORIGINAL review into a fresh directory:

    .venv/bin/manuscript-review import-chatgpt reviews/pilot-v1/report.json feedback.json --context handoffs/pilot-v1/chatgpt-review.json --manuscript manuscripts/pilot-v1.pdf --accept-grounded --out reviews/pilot-v1-feedback-accepted

This flag does not override fabricated citations, unsupported claims, impossible
actions, or unverified external claims. Source-valid opinions are still judgments,
not scientific facts. Imports are identified as manual ChatGPT feedback using
the existing Reviewer 2 role; no persona or API call is added.

For a V2 comparison export, substitute the comparison report, V2 context path,
and original V2 manuscript. Imported feedback can add concerns; it cannot edit
the manuscript, silently modify previous findings, or declare prior issues resolved.
Re-export after changing a source review. An old package cannot be replayed into
a different report, even when much of the text is unchanged.

The package may contain unpublished manuscript content. The local export is
not permission for any automatic upload. There is no authorship, source, or
model-authenticity verification for a manually supplied ChatGPT response.
