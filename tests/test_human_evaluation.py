from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from unittest.mock import patch

from manuscript_review.cli import main
from manuscript_review.errors import ReviewError
from manuscript_review.evaluation import prepare_evaluation, score_evaluation, DIMENSIONS, render_scores, apply_csv_ratings
from manuscript_review.pipeline import review_manuscript
from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, envelope, finding, response, packet_block, source_block


class HumanEvaluationTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.paper = self.write(PAPER)
        self.baseline, _ = review_manuscript(self.paper)
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"],
            transport=lambda body, timeout: response(envelope([finding(packet_block(body))])))
        self.assisted, _ = review_manuscript(self.paper, provider=provider)
        self.files = prepare_evaluation(self.baseline, self.assisted)
        self.packet = json.loads(self.files["blinded-reviews.json"])
        self.context = json.loads(self.files["manuscript-context.json"])
        self.key = json.loads(self.files["private/key.json"])
        self.form = json.loads(self.files["adjudication.json"])

    def complete(self):
        self.form["completed"] = True
        self.form["rater_id"] = "synthetic-rater"
        for row in self.form["concerns"]:
            row.update(classification="valid_minor_concern", preferred_severity="minor",
                       scores={k: 2 for k in DIMENSIONS}, notes="Constructed test rating, not expert judgment.")
        for arm, rating in self.form["overall"]["arms"].items():
            rating["author_usefulness"] = 3 if self.key["arms"][arm]["source"] == "assisted" else 2
        return self.form

    def score(self):
        return score_evaluation(self.packet, self.context, self.key, self.form)

    def test_blinding_removes_origin_ids_and_model_metadata(self):
        public = self.files["blinded-reviews.json"] + self.files["blinded-reviews.md"]
        for marker in ('"origin"', "test-model", "reviewer.scientific", "provider:openai"):
            self.assertNotIn(marker, public)
        self.assertEqual(set(self.packet["arms"]), {"A", "B"})
        self.assertEqual({r["source"] for r in self.key["arms"].values()}, {"deterministic", "assisted"})

    def test_partial_form_is_not_success_or_missing_issue_verdict(self):
        data = self.score()
        self.assertFalse(data["completed"])
        self.assertIn("Incomplete", data["outcome"])
        for arm in data["arms"].values():
            self.assertEqual(arm["source"], "blinded")
            self.assertIsNone(arm["important_issue_coverage"])
            self.assertIsNone(arm["missed_important_issues"])
        self.assertTrue(all(value is None for value in data["assisted_minus_baseline"].values()))
        self.assertIn("not assessed", render_scores(data))

    def test_individual_important_issues_and_misses_are_counted_by_inventory(self):
        self.complete()
        block = source_block(self.baseline.documents)
        self.form["important_issues"] = [{"id": "I1", "description": "Synthetic important judgment",
            "confidence": "medium", "citations": [{"block_id": block["id"], "quote": block["text"]}]}]
        assisted_arm = next(a for a, v in self.key["arms"].items() if v["source"] == "assisted")
        candidate = next(r for r in self.form["concerns"] if r["id"].startswith(assisted_arm))
        candidate.update(classification="true_important_concern", issue_id="I1")
        self.form["overall"]["preferred_arm"] = assisted_arm
        data = self.score()
        self.assertEqual(data["additional_important_issues"], ["I1"])
        self.assertEqual(data["preferred_source"], "assisted")
        baseline_arm = next(v for v in data["arms"].values() if v["source"] == "deterministic")
        self.assertEqual(baseline_arm["missed_important_issues"], ["I1"])

    def test_multiple_wordings_do_not_double_count_one_important_issue(self):
        self.complete()
        self.form["important_issues"] = [{"id": "I1", "description": "Uncertain synthetic judgment",
                                         "confidence": "low", "citations": []}]
        arm = next(iter(self.packet["arms"]))
        for row in [r for r in self.form["concerns"] if r["id"].startswith(arm)][:2]:
            row.update(classification="true_important_concern", issue_id="I1")
        self.assertEqual(self.score()["arms"][arm]["important_issues_found"], ["I1"])

    def test_cross_arm_concerns_are_not_redundancy_within_one_review(self):
        rows = self.form["concerns"]
        first = rows[0]
        other = next(r for r in rows if r["id"][0] != first["id"][0])
        first.update(classification="redundant_concern", redundant_with=other["id"])
        with self.assertRaisesRegex(ReviewError, "same arm"):
            self.score()

    def test_unknown_concern_or_duplicate_rating_is_rejected(self):
        self.form["concerns"][0]["id"] = "A-C99999"
        with self.assertRaisesRegex(ReviewError, "exactly once"):
            self.score()

    def test_completed_form_cannot_have_missing_scores(self):
        self.form["completed"] = True
        with self.assertRaises(ReviewError):
            self.score()

    def test_invalid_score_is_not_coerced(self):
        self.form["concerns"][0]["scores"]["scientific_correctness"] = True
        with self.assertRaisesRegex(ReviewError, "integers"):
            self.score()

    def test_malformed_form_field_is_a_controlled_error(self):
        self.form["overall"]["preferred_arm"] = ["A"]
        with self.assertRaises(ReviewError):
            self.score()

    def test_csv_roundtrip_keeps_unrated_values_unknown(self):
        merged = apply_csv_ratings(self.form, self.files["concern-ratings.csv"])
        self.assertEqual(merged["concerns"], self.form["concerns"])
        self.assertFalse(score_evaluation(self.packet, self.context, self.key, merged)["completed"])

    def test_csv_fractional_or_out_of_range_scores_are_rejected(self):
        import csv
        buffer = io.StringIO()
        reader = csv.DictReader(io.StringIO(self.files["concern-ratings.csv"]))
        rows = list(reader)
        rows[0]["scientific_correctness"] = "3.5"
        writer = csv.DictWriter(buffer, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        with self.assertRaisesRegex(ReviewError, "integer"):
            apply_csv_ratings(self.form, buffer.getvalue())

    def test_mismatched_manuscript_cannot_be_compared(self):
        changed = deepcopy(self.assisted)
        changed.documents[0].sha256 = "wrong"
        with self.assertRaisesRegex(ReviewError, "same manuscript"):
            prepare_evaluation(self.baseline, changed)

    def test_evaluation_requires_same_tool_version(self):
        changed = deepcopy(self.assisted)
        changed.tool_version = "0.3.0"
        with self.assertRaisesRegex(ReviewError, "same tool version"):
            prepare_evaluation(self.baseline, changed)

    def test_evaluation_requires_identical_deterministic_layer(self):
        changed = deepcopy(self.assisted)
        deterministic = next(f for f in changed.findings if f.origin == "deterministic")
        deterministic.severity = "minor" if deterministic.severity != "minor" else "moderate"
        with self.assertRaisesRegex(ReviewError, "deterministic findings differ"):
            prepare_evaluation(self.baseline, changed)

    def test_dry_run_cannot_stand_in_for_llm_review(self):
        dry = deepcopy(self.assisted)
        dry.llm["dry_run"] = True
        with self.assertRaisesRegex(ReviewError, "dry run"):
            prepare_evaluation(self.baseline, dry)

    def test_optional_expert_arm_has_no_authoritative_status(self):
        block = source_block(self.baseline.documents)
        expert = {"document_hashes": {d.id: d.sha256 for d in self.baseline.documents}, "concerns": [{
            "issue": "A synthetic independent concern.", "severity": "major",
            "citations": [{"block_id": block["id"], "quote": block["text"]}],
            "suggested_action": "Rebuild selection within development data."}]}
        files = prepare_evaluation(self.baseline, self.assisted, expert)
        key = json.loads(files["private/key.json"])
        self.assertEqual(len(key["arms"]), 3)
        self.assertIn("not an objective", files["RUBRIC.md"])

    def test_tampered_blinded_packet_is_rejected(self):
        self.packet["arms"]["A"][0]["issue"] = "Changed after ratings began."
        with self.assertRaisesRegex(ReviewError, "local key"):
            self.score()

    def test_unjudged_dimensions_remain_null_not_zero(self):
        result = self.score()
        for arm in result["arms"].values():
            self.assertIsNone(arm["dimension_scores"]["scientific_correctness"]["mean"])
            self.assertEqual(arm["dimension_scores"]["scientific_correctness"]["rated"], 0)

    def test_cli_prepare_and_score_are_network_free(self):
        baseline = self.write(json.dumps(self.baseline.to_dict()), "baseline.json")
        assisted = self.write(json.dumps(self.assisted.to_dict()), "assisted.json")
        bundle = self.root / "eval"
        with patch("manuscript_review.providers.openai._post") as network, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["evaluate", "prepare", "--baseline", str(baseline), "--assisted", str(assisted), "--out", str(bundle)]), 0)
            self.assertEqual(main(["evaluate", "score", str(bundle), "--out", str(self.root / "scored")]), 0)
        network.assert_not_called()
        self.assertTrue((self.root / "scored/evaluation.json").exists())
