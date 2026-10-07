"""Local blinded, concern-level human evaluation. Judgments are not ground truth."""
from collections import Counter
from dataclasses import asdict
import csv
import io
import json
import secrets
from uuid import uuid4

from .errors import ReviewError
from .exchange import canonical_hash, verify_same_sources
from .grounding import resolve_citations

DIMENSIONS = (
    "scientific_correctness", "severity_calibration", "evidence_grounding",
    "specificity", "actionability", "novelty_positioning", "nonredundancy", "author_usefulness")
CLASSES = ("true_important_concern", "valid_minor_concern", "redundant_concern",
           "unsupported_speculative_concern", "false_positive", "unable_to_judge")

RUBRIC = """# Human adjudication: one manuscript, one rater

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
"""


def _json(data):
    return json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def _deterministic_signature(review):
    rows = []
    for finding in review.findings:
        if finding.origin != "deterministic":
            continue
        rows.append({
            "id": finding.id, "rule_id": finding.rule_id, "severity": finding.severity,
            "issue_status": finding.issue_status, "disposition": finding.disposition,
            "evidence": [(ev.block_id, ev.start, ev.end, ev.quote) for ev in finding.evidence],
        })
    return canonical_hash(sorted(rows, key=lambda row: row["id"]))


def _neutral_findings(review):
    return [{"original_id": f.id, "issue": f.issue, "why_it_matters": f.why_it_matters,
             "severity": f.severity, "evidence": [asdict(e) for e in f.evidence],
             "suggested_action": f.suggested_fix, "analysis": f.suggested_analysis,
             "action": f.action,
             "presentation": "requires_verification" if f.disposition == "needs_review" else "active_lead"}
            for f in review.findings if f.disposition in ("active", "confirmed", "needs_review")]


def _expert_findings(expert, baseline):
    if (not isinstance(expert, dict) or set(expert) != {"document_hashes", "concerns"}
            or expert["document_hashes"] != {d.id: d.sha256 for d in baseline.documents}
            or not isinstance(expert["concerns"], list)):
        raise ReviewError("Expert review needs matching document_hashes and a concerns list.")
    rows = []
    for n, row in enumerate(expert["concerns"], 1):
        if (not isinstance(row, dict) or set(row) != {"issue", "severity", "citations", "suggested_action"}
                or row["severity"] not in ("major", "moderate", "minor", "optional_strengthening")
                or any(not isinstance(row[k], str) or not row[k].strip() for k in ("issue", "suggested_action"))
                or not isinstance(row["citations"], list)):
            raise ReviewError("Invalid expert concern; use the documented concise expert-review format.")
        ev = resolve_citations(row["citations"], baseline.documents)
        rows.append({"original_id": "expert-%d" % n, "issue": row["issue"], "why_it_matters": "",
                     "severity": row["severity"], "evidence": [asdict(e) for e in ev],
                     "suggested_action": row["suggested_action"], "analysis": "", "action": {},
                     "presentation": "active_lead" if ev else "requires_verification"})
    return rows


def prepare_evaluation(baseline, assisted, expert=None):
    verify_same_sources(baseline, assisted)
    if baseline.configuration != assisted.configuration:
        raise ReviewError("Blinded comparison requires the same deterministic configuration and overrides.")
    if baseline.tool_version != assisted.tool_version:
        raise ReviewError("Blinded comparison requires baseline and assisted reviews from the same tool version.")
    if _deterministic_signature(baseline) != _deterministic_signature(assisted):
        raise ReviewError("Baseline and assisted deterministic findings differ; regenerate both arms before evaluation.")
    if any(r["mode"] in ("provider", "manual_import") for r in baseline.reviewer_runs):
        raise ReviewError("Baseline must be deterministic-only.")
    if assisted.llm.get("dry_run") or not any(r["mode"] in ("provider", "manual_import") for r in assisted.reviewer_runs):
        raise ReviewError("Assisted review must contain a completed provider role or manual feedback; a dry run is not a review.")
    sources = [("deterministic", _neutral_findings(baseline)),
               ("assisted", _neutral_findings(assisted))]
    if expert is not None:
        sources.append(("expert", _expert_findings(expert, baseline)))
    rng = secrets.SystemRandom()
    rng.shuffle(sources)
    evaluation_id = "evaluation-" + uuid4().hex
    public, mapping, form_rows = {}, {}, []
    for index, (source, rows) in enumerate(sources):
        arm = chr(65 + index)
        rng.shuffle(rows)
        public[arm] = []
        mapping[arm] = {"source": source, "concerns": {}}
        for number, row in enumerate(rows, 1):
            identifier = arm + "-C%03d" % number
            mapping[arm]["concerns"][identifier] = row.pop("original_id")
            public[arm].append({"id": identifier, **row})
            form_rows.append({"id": identifier, "classification": None, "issue_id": None,
                              "redundant_with": None, "preferred_severity": None,
                              "scores": {key: None for key in DIMENSIONS}, "notes": ""})
    context = {"document_hashes": {d.id: d.sha256 for d in baseline.documents},
               "source_blocks": [asdict(b) for d in baseline.documents for b in d.blocks]}
    public_packet = {"evaluation_id": evaluation_id, "arms": public}
    form = {"evaluation_id": evaluation_id, "rater_id": "", "completed": False,
            "blinding_notes": "", "concerns": form_rows, "important_issues": [],
            "overall": {"preferred_arm": None, "notes": "",
                        "arms": {a: {"author_usefulness": None, "reading_minutes": None} for a in public}}}
    key = {"evaluation_id": evaluation_id, "arms": mapping,
           "public_packet_sha256": canonical_hash(public_packet), "context_sha256": canonical_hash(context),
           "baseline_sha256": canonical_hash(baseline.to_dict()),
           "assisted_sha256": canonical_hash(assisted.to_dict()),
           "assisted_incomplete_roles": assisted.quality.get("failed_roles", [])}
    lines = ["# Blinded review comparison", "", "Read the manuscript first; follow RUBRIC.md. Do not open private/key.json.", ""]
    for arm, rows in public.items():
        lines.extend(["## Arm " + arm, ""])
        for row in rows:
            lines.extend(["### " + row["id"], "", row["issue"], "",
                          "Severity: " + row["severity"] + "; presentation: " + row["presentation"],
                          "", "Action: " + row["suggested_action"], ""])
            if row["why_it_matters"]:
                lines.extend(["Why it matters: " + row["why_it_matters"], ""])
            if row["analysis"]:
                lines.extend(["Analysis: " + row["analysis"], ""])
            for field, value in row["action"].items():
                if field != "kind" and value:
                    lines.append("- " + field.replace("_", " ").capitalize() + ": " + str(value))
            lines.append("")
            for ev in row["evidence"]:
                lines.extend(["> " + ev["quote"].replace("\n", "\n> "), "",
                              "Source: " + ev["block_id"] + "; " + ev["section"], ""])
    csv_buffer = io.StringIO(newline="")
    columns = ["id", "classification", "issue_id", "redundant_with", "preferred_severity", *DIMENSIONS, "notes"]
    writer = csv.DictWriter(csv_buffer, fieldnames=columns)
    writer.writeheader()
    for row in form_rows:
        writer.writerow({k: row["id"] if k == "id" else "" for k in columns})
    return {"blinded-reviews.md": "\n".join(lines), "blinded-reviews.json": _json(public_packet),
            "manuscript-context.json": _json(context), "adjudication.json": _json(form),
            "concern-ratings.csv": csv_buffer.getvalue(),
            "RUBRIC.md": RUBRIC, "private/key.json": _json(key)}


def apply_csv_ratings(form, text):
    from copy import deepcopy
    try:
        reader = csv.DictReader(io.StringIO(text))
        columns = ["id", "classification", "issue_id", "redundant_with", "preferred_severity", *DIMENSIONS, "notes"]
        if reader.fieldnames != columns:
            raise ReviewError("Concern ratings CSV columns differ from the generated form.")
        rows = []
        for raw in reader:
            if set(raw) != set(columns) or any(v is None for v in raw.values()):
                raise ReviewError("Malformed concern ratings CSV row.")
            row = {k: raw[k].strip() or None for k in
                   ("id", "classification", "issue_id", "redundant_with", "preferred_severity")}
            row["scores"] = {}
            for dimension in DIMENSIONS:
                value = raw[dimension].strip()
                if value not in ("", "0", "1", "2", "3"):
                    raise ReviewError("CSV scores must be blank or an integer from 0 to 3.")
                row["scores"][dimension] = int(value) if value else None
            row["notes"] = raw["notes"]
            rows.append(row)
        result = deepcopy(form)
        result["concerns"] = rows
        return result
    except (csv.Error, TypeError, AttributeError):
        raise ReviewError("Malformed concern ratings CSV.") from None


def _rating(value):
    return value is None or (type(value) is int and 0 <= value <= 3)


def score_evaluation(packet, context, key, form):
    try:
        return _score_evaluation(packet, context, key, form)
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ReviewError("Malformed evaluation files; preserve the generated structure and use rubric values.") from None


def _score_evaluation(packet, context, key, form):
    if (canonical_hash(packet) != key.get("public_packet_sha256")
            or canonical_hash(context) != key.get("context_sha256")
            or not isinstance(form, dict) or form.get("evaluation_id") != key.get("evaluation_id")
            or packet.get("evaluation_id") != key.get("evaluation_id")):
        raise ReviewError("Evaluation package or adjudication does not match its local key.")
    expected_fields = {"evaluation_id", "rater_id", "completed", "blinding_notes", "concerns", "important_issues", "overall"}
    if set(form) != expected_fields or type(form["completed"]) is not bool or not isinstance(form["rater_id"], str):
        raise ReviewError("Invalid adjudication form.")
    originals = {r["id"]: (arm, r) for arm, rows in packet["arms"].items() for r in rows}
    arms = set(packet["arms"])
    if (not isinstance(form["concerns"], list)
            or any(not isinstance(r, dict) for r in form["concerns"])
            or {r.get("id") for r in form["concerns"]} != set(originals)
            or len(form["concerns"]) != len(originals)):
        raise ReviewError("Adjudication must retain every blinded concern exactly once.")
    important = {}
    if not isinstance(form["important_issues"], list):
        raise ReviewError("important_issues must be a list.")
    blocks = {b["id"]: b for b in context["source_blocks"]}
    for issue in form["important_issues"]:
        if (not isinstance(issue, dict) or set(issue) != {"id", "description", "confidence", "citations"}
                or not isinstance(issue["id"], str) or not issue["id"] or issue["id"] in important
                or not isinstance(issue["description"], str) or not issue["description"].strip()
                or issue["confidence"] not in ("low", "medium", "high") or not isinstance(issue["citations"], list)):
            raise ReviewError("Invalid or duplicate important-issue judgment.")
        if not issue["citations"] and issue["confidence"] != "low":
            raise ReviewError("Unlocated important-issue judgments require low confidence.")
        for cite in issue["citations"]:
            if (not isinstance(cite, dict) or set(cite) != {"block_id", "quote"}
                    or cite["block_id"] not in blocks or not isinstance(cite["quote"], str)
                    or not cite["quote"].strip() or cite["quote"] not in blocks[cite["block_id"]]["text"]):
                raise ReviewError("Important-issue evidence does not match the manuscript.")
        important[issue["id"]] = issue
    rows = form["concerns"]
    for row in rows:
        if (set(row) != {"id", "classification", "issue_id", "redundant_with", "preferred_severity", "scores", "notes"}
                or row["classification"] not in CLASSES + (None,)
                or not isinstance(row["scores"], dict) or set(row["scores"]) != set(DIMENSIONS)
                or not all(_rating(v) for v in row["scores"].values())
                or row["preferred_severity"] not in (None, "major", "moderate", "minor", "optional_strengthening")
                or not isinstance(row["notes"], str)):
            raise ReviewError("Invalid concern rating; scores must be integers 0-3 or null.")
        if row["issue_id"] is not None and row["issue_id"] not in important:
            raise ReviewError("Concern refers to an unknown important-issue ID.")
        if row["classification"] == "true_important_concern" and row["issue_id"] is None:
            raise ReviewError("Link each important concern to an important_issues entry to avoid double counting.")
        if row["classification"] == "redundant_concern":
            other = row["redundant_with"]
            if other not in originals or other == row["id"] or originals[other][0] != originals[row["id"]][0]:
                raise ReviewError("Redundant concerns must reference a different concern in the same arm.")
        if form["completed"]:
            if row["classification"] is None:
                raise ReviewError("Completed form contains an unclassified concern.")
            if row["classification"] != "unable_to_judge" and any(row["scores"][k] is None for k in
                    ("scientific_correctness", "evidence_grounding", "specificity", "actionability", "author_usefulness")):
                raise ReviewError("Completed form needs core scores or unable_to_judge.")
    overall = form["overall"]
    if (not isinstance(overall, dict) or set(overall) != {"preferred_arm", "notes", "arms"}
            or not isinstance(overall["arms"], dict) or set(overall["arms"]) != arms
            or overall["preferred_arm"] not in arms | {None, "tie", "unclear"}):
        raise ReviewError("Invalid overall arm ratings.")
    if form["completed"] and not form["rater_id"].strip():
        raise ReviewError("Completed adjudication requires a rater identifier.")
    summaries = {}
    for arm in sorted(arms):
        rating = overall["arms"][arm]
        if (not isinstance(rating, dict) or set(rating) != {"author_usefulness", "reading_minutes"}
                or not _rating(rating["author_usefulness"])
                or (rating["reading_minutes"] is not None and
                    (type(rating["reading_minutes"]) not in (int, float) or
                     not 0 <= rating["reading_minutes"] <= 100000))):
            raise ReviewError("Invalid overall usefulness or reading time.")
        if form["completed"] and rating["author_usefulness"] is None:
            raise ReviewError("Completed form needs an overall usefulness rating for each arm.")
        arm_rows = [r for r in rows if originals[r["id"]][0] == arm]
        primary = [r for r in arm_rows if originals[r["id"]][1]["presentation"] == "active_lead"]
        found = {r["issue_id"] for r in primary if r["classification"] == "true_important_concern"}
        classifications = Counter(r["classification"] or "unjudged" for r in primary)
        means = {}
        for dimension in DIMENSIONS:
            values = [r["scores"][dimension] for r in primary if r["scores"][dimension] is not None]
            means[dimension] = {"mean": sum(values) / len(values) if values else None, "rated": len(values), "total": len(primary)}
        summaries[arm] = {
            "source": key["arms"][arm]["source"], "active_concerns": len(primary),
            "classification_counts": dict(classifications), "dimension_scores": means,
            "important_issues_found": sorted(found),
            "missed_important_issues": sorted(set(important) - found) if form["completed"] else None,
            "important_issue_coverage": len(found) / len(important) if important and form["completed"] else None,
            "requires_verification_count": len(arm_rows) - len(primary),
            "requires_verification_classifications": dict(Counter(
                r["classification"] or "unjudged" for r in arm_rows if r not in primary)),
            "overall": rating,
        }
    by_source = {v["source"]: v for v in summaries.values()}
    baseline, assisted = by_source["deterministic"], by_source["assisted"]
    deltas = {}
    for dimension in DIMENSIONS:
        a, b = assisted["dimension_scores"][dimension]["mean"], baseline["dimension_scores"][dimension]["mean"]
        deltas[dimension] = a - b if a is not None and b is not None else None
    preference = overall["preferred_arm"]
    preferred_source = key["arms"][preference]["source"] if preference in arms else preference
    outcome = ("Incomplete adjudication; no comparative conclusion." if not form["completed"] else
               "This rater preferred " + str(preferred_source or "no arm") + ". Inspect important-issue coverage and error burden before choosing a workflow.")
    additional = sorted(set(assisted["important_issues_found"]) - set(baseline["important_issues_found"]))
    lost = sorted(set(baseline["important_issues_found"]) - set(assisted["important_issues_found"]))
    if not form["completed"]:
        for summary in summaries.values():
            summary["source"] = "blinded"
        deltas = {dimension: None for dimension in DIMENSIONS}
        additional, lost, preferred_source = [], [], None
    return {"evaluation_id": key["evaluation_id"], "rater_id": form["rater_id"],
            "adjudication_sha256": canonical_hash(form), "concern_ratings": rows,
            "completed": form["completed"], "blinding_notes": form["blinding_notes"], "arms": summaries,
            "important_issue_inventory": list(important.values()), "assisted_minus_baseline": deltas,
            "additional_important_issues": additional, "important_issues_lost": lost,
            "preferred_source": preferred_source, "outcome": outcome, "rater_notes": overall["notes"],
            "assisted_incomplete_roles": key["assisted_incomplete_roles"] if form["completed"] else None,
            "limitations": [
                "One manuscript and one subjective rater; no objective gold standard or statistical significance.",
                "Scores are ordinal judgments; means are descriptive, not a combined scientific-quality score.",
                "Missed issues are relative to the rater's non-exhaustive inventory; low-confidence judgments remain included.",
                "Style and content can reveal source despite randomized labels. Original identities stay in the local private key.",
                "Primary scores use active review leads. Quarantined suggestions are counted separately; pipeline-merged duplicates are excluded.",
                "Expert review is a third opinion, not an authoritative answer key.",
            ]}


def render_scores(result):
    lines = ["# Pilot adjudication result", "", result["outcome"], "",
             "| Arm | Source | Active concerns | Important issues found | Missed from inventory | Author usefulness |",
             "| --- | --- | ---: | ---: | ---: | ---: |"]
    for arm, row in result["arms"].items():
        lines.append("| %s | %s | %d | %d | %s | %s |" % (
            arm, row["source"], row["active_concerns"], len(row["important_issues_found"]),
            len(row["missed_important_issues"]) if result["important_issue_inventory"] and row["missed_important_issues"] is not None else "not assessed",
            row["overall"]["author_usefulness"]))
    lines += ["", "Additional important issues in assisted review: " + ", ".join(result["additional_important_issues"] or ["none judged"]),
              "Important issues lost: " + ", ".join(result["important_issues_lost"] or ["none judged"]), "",
              "## Concern classifications", ""]
    for arm, row in result["arms"].items():
        lines.append("- " + arm + " active: " + json.dumps(row["classification_counts"], sort_keys=True))
        lines.append("- " + arm + " requires verification: " + json.dumps(row["requires_verification_classifications"], sort_keys=True))
    lines += ["", "## Scores (assisted minus deterministic)", ""]
    for dimension, delta in result["assisted_minus_baseline"].items():
        lines.append("- " + dimension + ": " + ("not assessed" if delta is None else "%+.2f" % delta))
    lines += ["", "Rated-item denominators, all arm means, and individual judgments are retained in JSON and the adjudication form.",
              "", "## Interpretation limits", ""] + ["- " + x for x in result["limitations"]]
    return "\n".join(lines) + "\n"
