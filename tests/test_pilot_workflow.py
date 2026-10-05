from contextlib import redirect_stdout, redirect_stderr
import io
import json
from unittest.mock import patch

from manuscript_review.cli import main
from manuscript_review.comparison import compare_reviews
from manuscript_review.pipeline import review_manuscript
from manuscript_review.reporting import render_markdown, render_comparison
from manuscript_review.resolution import major_progress
from .helpers import WorkspaceTest, FIXTURES
from .llm_helpers import envelope, response, finding, packet_block


class PilotWorkflowTests(WorkspaceTest):
    def test_report_opening_answers_revision_questions_and_preserves_audit(self):
        review, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        text = render_markdown(review)
        opening = text.split("<details>", 1)[0]
        for label in ("What the paper is trying to claim", "Contribution if the claims survive",
                      "What could kill this paper", "Major strengths", "Analyses most likely",
                      "Text and positioning", "Likely Reviewer 2"):
            self.assertIn(label, opening)
        self.assertLess(len(opening.split()), 1300)
        self.assertEqual(len(review.sections), 20)
        self.assertIn("Detailed 20-section audit", text)
        self.assertIn("## Finding details", text)

    def test_major_progress_separates_scope_withdrawal_and_new_detection(self):
        rows = [{"prior_issue_id": str(n), "prior_severity": "major", "status": status}
                for n, status in enumerate(("resolved", "partially_resolved", "unresolved", "worsened",
                                           "cannot_determine", "no_longer_applicable"))]
        rows.append({"prior_issue_id": "minor", "prior_severity": "minor", "status": "unresolved"})
        data = major_progress({"issue_assessments": rows, "new_concerns": [
            {"id": "new", "severity": "major"}, {"id": "minor-new", "severity": "minor"}]})
        self.assertTrue(all(len(v) == 1 for v in data.values()))
        self.assertEqual(data["scope_withdrawn"][0]["status"], "no_longer_applicable")

    def test_revision_summary_cannot_call_wording_a_verified_repair(self):
        old, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        new, _ = review_manuscript(FIXTURES / "revised_manuscript.md")
        comparison = compare_reviews(old, new)
        text = render_comparison(comparison)
        self.assertIn("Major concerns at a glance", text)
        self.assertIn("does not verify execution", text)
        for row in comparison["issue_assessments"]:
            self.assertIn("prior_severity", row)
            if row["wording_softened_only"]:
                self.assertEqual(row["status"], "unresolved")

    def test_review_save_revise_compare_export_workflow_without_network(self):
        v1 = FIXTURES / "flawed_manuscript.md"
        v2 = FIXTURES / "revised_manuscript.md"
        old_dir, new_dir = self.root / "v1", self.root / "comparison"
        def fake(body, timeout):
            return response(envelope([finding(packet_block(body, "We selected"))]))
        with patch.dict("os.environ", {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post", side_effect=fake) as network, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["review", str(v1), "--llm", "--model", "test-model", "--roles", "scientific",
                                   "--out", str(old_dir)]), 0)
            self.assertEqual(network.call_count, 1)
            self.assertEqual(main(["compare", str(v1), str(v2), "--prior-review", str(old_dir / "report.json"),
                                   "--llm", "--model", "test-model", "--dry-run", "--out", str(new_dir)]), 0)
            self.assertEqual(network.call_count, 1)
            self.assertEqual(main(["export-chatgpt", str(new_dir / "report.json"),
                                   "--out", str(self.root / "handoff")]), 0)
        context = json.loads((self.root / "handoff/chatgpt-review.json").read_text())
        self.assertIsNotNone(context["comparison"])
        self.assertTrue((new_dir / "diagnostics.json").exists())

    def test_existing_diagnostics_prevents_charge_before_output_collision(self):
        output = self.root / "existing"
        output.mkdir()
        (output / "diagnostics.json").write_text("{}")
        with patch.dict("os.environ", {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post") as network, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["review", str(FIXTURES / "flawed_manuscript.md"), "--llm",
                                   "--model", "test-model", "--out", str(output)]), 2)
        network.assert_not_called()
