import json
from unittest.mock import patch

from manuscript_review.benchmark import evaluate
from manuscript_review.errors import ReviewError
from .helpers import WorkspaceTest, ROOT


class BenchmarkTests(WorkspaceTest):
    def saved_case(self):
        from manuscript_review.pipeline import review_manuscript
        from .llm_helpers import PAPER
        paper = self.write(PAPER, "paper.md")
        manifest = {"synthetic_only": True, "version": "1", "evaluated_rule_ids": [],
                    "cases": [{"id": "paper", "file": "paper.md", "expected": []}]}
        path = self.write(json.dumps(manifest), "manifest.json")
        report, _ = review_manuscript(paper)
        output = self.root / "reports/paper/report.json"
        output.parent.mkdir(parents=True)
        return path, output, report.to_dict()

    def test_saved_report_source_blocks_are_verified_against_fixture(self):
        manifest, output, data = self.saved_case()
        output.write_text(json.dumps(data))
        self.assertEqual(evaluate(manifest, self.root / "reports")["case_count"], 1)
        data["documents"][0]["blocks"][0]["text"] = "# Forged source with original hash"
        output.write_text(json.dumps(data))
        with self.assertRaisesRegex(ReviewError, "source blocks differ"):
            evaluate(manifest, self.root / "reports")

    def test_saved_report_from_different_engine_version_is_rejected(self):
        manifest, output, data = self.saved_case()
        data["tool_version"] = "0.3.0"
        output.write_text(json.dumps(data))
        with self.assertRaisesRegex(ReviewError, "different tool version"):
            evaluate(manifest, self.root / "reports")

    def test_malformed_saved_report_is_a_controlled_error(self):
        manifest, output, _ = self.saved_case()
        output.write_text('{"documents": null}')
        with self.assertRaises(ReviewError):
            evaluate(manifest, self.root / "reports")

    def test_scoped_benchmark_exposes_known_false_negative(self):
        with patch("manuscript_review.providers.openai._post") as network:
            data = evaluate(ROOT / "benchmarks/manifest.json")
        network.assert_not_called()
        self.assertEqual(data["case_count"], 6)
        self.assertEqual(data["counts"]["tp"], 11)
        self.assertEqual(data["counts"]["fn"], 1)
        self.assertEqual(data["counts"]["fp"], 0)
        self.assertGreater(data["counts"]["unscored_findings"], 0)

    def test_private_fixture_manifest_is_refused(self):
        path = self.write('{"synthetic_only": false}', "manifest.json")
        with self.assertRaisesRegex(ReviewError, "synthetic_only"):
            evaluate(path)

    def test_live_llm_evaluation_cannot_happen_implicitly(self):
        with self.assertRaisesRegex(ReviewError, "never calls"):
            evaluate(ROOT / "benchmarks/manifest.json", layer="llm")

    def test_fixture_path_escape_is_refused(self):
        manifest = {"synthetic_only": True, "version": "1", "evaluated_rule_ids": [],
                    "cases": [{"id": "escape", "file": "../private.md", "expected": []}]}
        with self.assertRaisesRegex(ReviewError, "within"):
            evaluate(self.write(json.dumps(manifest), "manifest.json"))
