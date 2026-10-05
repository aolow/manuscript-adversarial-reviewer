# Does the assisted review help?

Use the same manuscript, supplements, deterministic configuration, and overrides
for both arms. Evaluate a realistically complex paper that you are authorized
to share with any selected provider. Nothing in the evaluation command uploads it.

First make a deterministic review:

    .venv/bin/manuscript-review review manuscripts/pilot-v1.pdf --out reviews/pilot-baseline

Use the LLM-assisted review saved by [PILOT_GUIDE.md](PILOT_GUIDE.md). Then:

    .venv/bin/manuscript-review evaluate prepare --baseline reviews/pilot-baseline/report.json --assisted reviews/pilot-v1/report.json --out evaluations/pilot

A dry run is not an assisted review. At least one provider role must have
completed, or manual feedback must have been imported. Partial provider runs
are permitted but disclosed in the unblinded result. This supports exploratory
failure evaluation; it does not imply the full workflow succeeded.

## What to give the adjudicator

Give the adjudicator the manuscript plus:

- blinded-reviews.md: neutral randomized A/B labels, individually numbered concerns.
- manuscript-context.json: stable source blocks for recording missed issues.
- RUBRIC.md: concise classification and 0–3 rating anchors.
- concern-ratings.csv: one row per concern, fillable in a spreadsheet or text editor.
- adjudication.json: rater identity, issue inventory, overall usefulness, preference, and notes.

Keep private/key.json away from the adjudicator until scoring. Blinding hides
origin labels, provider/model metadata, and rule IDs; style, content, and length
can still reveal the source. An independent person preparing the package makes
blinding more credible. Record source exposure in blinding_notes.

Read the paper and enter important_issues BEFORE reading either review where
possible. This inventory is a rater judgment, not an exhaustive gold standard.
Classify each concern as important, valid minor, redundant, speculative/unsupported,
false positive, or unable to judge. A missed important issue is an inventory
entry not identified by an active concern in that arm.

Score scientific correctness, severity calibration, evidence grounding,
specificity, actionability, novelty/positioning, nonredundancy, and author usefulness.
Higher is better; null/blank means not assessable, not zero. Give overall usefulness
for each arm and optionally the reading time. Use notes to explain disputed
judgments and data/feasibility constraints.

The CSV ratings replace only the concern-rating section of adjudication.json.
Keep important_issues, overall ratings, and blinding notes in the JSON form.
Mark completed=true only after all applicable ratings are filled. Set
preferred_arm to A/B/C, tie, or unclear. You can also fill the JSON alone and
omit --ratings-csv.

## Score and unblind

    .venv/bin/manuscript-review evaluate score evaluations/pilot --ratings-csv evaluations/pilot/concern-ratings.csv --out evaluations/pilot-result

Read evaluation.md and evaluation.json. They show:

- Important issue groups found and missed, including assisted-only discoveries.
- Incorrect/speculative, minor, redundant, and unjudged concern counts.
- Separate counts for quarantined suggestions.
- Per-dimension ordinal means with rated/total denominators and assisted-minus-baseline differences.
- Author usefulness, reading time, preference, blinding notes, and incomplete roles.

No weighted quality score or significance claim is produced. Unfilled forms
produce an explicitly incomplete result; missing scores are never zero-filled.
Incomplete scoring keeps arm identities blinded and withholds comparative deltas.
The saved result includes the original ratings and their digest.
For another adjudicator, copy the blank form and use --adjudication plus a new
output directory. Compare disagreements rather than silently averaging them away.

Before choosing the assisted workflow, weigh additional important insights
against false alarms, redundancy, impractical analyses, and time spent checking
the review. A tiny set of papers or one rater cannot establish general performance.

## Optional human/expert comparison

Add --expert expert-review.json to prepare. The expert review becomes a randomized
third arm; it is not used as an answer key. The concise input format is:

    {
      "document_hashes": {"manuscript": "COPY SHA256 FROM REPORT"},
      "concerns": [{
        "issue": "The proposed scientific concern.",
        "severity": "major",
        "citations": [{"block_id": "COPY BLOCK ID", "quote": "COPY EXACT SOURCE TEXT"}],
        "suggested_action": "A specific corrective analysis or explanation."
      }]
    }

Copy all supplement hashes too. Locations are derived locally. Empty citations
are allowed but the concern is displayed as requiring verification.
An expert's unsupported statement does not become validated engine output.

For local practice, fixtures/pilot_complex_manuscript.md is fictional and
deliberately contains overlapping concerns and safeguards. The stress tests use
constructed responses; they provide no live scientific-quality score.
