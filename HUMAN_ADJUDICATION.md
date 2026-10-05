# Human adjudication: one manuscript, one rater

Read the manuscript first. Before opening the blinded reviews, list the important
issues you would expect a useful review to identify. These are your judgments,
not an objective or exhaustive gold standard. Record uncertainty.

Open blinded-reviews.md and fill adjudication.json. Alternatively, fill concern-ratings.csv
for per-concern ratings and use --ratings-csv when scoring; keep the issue inventory
and overall judgments in adjudication.json. Do not open private/key.json
until ratings are complete. Wording and review length may still reveal the source;
record prior exposure or a guessed source in blinding_notes. Use an independent
person to prepare the package when practical.

For each concern, set classification:
- true_important_concern: scientifically sound and consequential to the central claim.
- valid_minor_concern: sound but mainly clarification or limited improvement.
- redundant_concern: repeats another concern in the SAME arm; give redundant_with.
- unsupported_speculative_concern: plausible question but not supported enough to assert.
- false_positive: materially incorrect, contradicted, or inapplicable.
- unable_to_judge: insufficient expertise/evidence; explain rather than forcing a score.

Rate each dimension 0–3; null means not assessable/applicable, never zero:
0 = wrong/unusable; 1 = weak or substantially incomplete; 2 = useful with qualification;
3 = strong and well supported.

Dimension anchors:
- scientific_correctness: sound interpretation of design, units, biology, and inference.
- severity_calibration: claimed importance matches the likely scientific consequence.
- evidence_grounding: excerpts actually support the interpretation, not merely exist.
- specificity: identifies the exact claim, experiment, or analysis boundary.
- actionability: feasible next step, data prerequisites, comparison, and decision criterion.
- novelty_positioning: useful contribution/framing insight; literature claims must be verified separately.
- nonredundancy: 0 repeats existing advice; 3 adds distinct useful information (higher is better).
- author_usefulness: would this materially help you revise the paper?

Set preferred_severity to your judgment, and add a brief rationale for important,
false, speculative, or redundant concerns. Link true important concerns to an
important_issues entry via issue_id; do not count multiple phrasings twice.

important_issues entries:
{"id":"I001","description":"...","confidence":"medium","citations":[{"block_id":"...","quote":"..."}]}
Use manuscript-context.json for stable block IDs. Empty citations are allowed for
an uncertain judgment, but that judgment must have low confidence.
A missed important issue is an entry with no linked true-important concern in an arm.
The missed-issue rate is undefined if you did not establish an issue inventory.
Add overlooked issues after review only with a note; this can favor the reviewed arms.

Give each arm an overall author_usefulness score and optional reading time in
minutes. Set preferred_arm to A/B/C, tie, or unclear. This is your preference,
not an automated validity verdict. Set completed=true only when every concern
has a classification and the applicable scores. Otherwise leave false for a
clearly labeled partial result.

Score only after saving ratings. The score command unblinds the arms and reports
counts, rated-item denominators, important issues found/missed, ordinal score
means, author preference, and assisted-minus-baseline differences. It does not
combine the dimensions into a scientific-quality score or infer significance.
Keep unverified suggestions separate from active review leads in the results.
For another rater, copy the blank form and score separately; inspect disagreements.
