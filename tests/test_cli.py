import json
import os
from pathlib import Path
import subprocess
import sys

from .helpers import WorkspaceTest, FIXTURES, ROOT


class CliTests(WorkspaceTest):
    def cli(self, *args):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        return subprocess.run([sys.executable, "-m", "manuscript_review", *map(str, args)],
                              cwd=self.root, env=env, text=True, capture_output=True)

    def test_end_to_end_review_and_prompts(self):
        output = self.root / "review"
        result = self.cli("review", FIXTURES / "flawed_manuscript.md", "--out", output, "--export-prompts")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((output / "report.json").read_text())
        self.assertEqual(len(list((output / "prompts").glob("*.json"))), 8)
        ids = {f["id"] for f in report["findings"]}
        self.assertIn("pattern.feature_selection_before_split", ids)
        self.assertIn("pattern.cell_pseudoreplication", ids)
        self.assertIn("check.confidence_intervals", ids)
        self.assertIn("pattern.causal_overclaim", ids)
        self.assertIn("pattern.novelty_overclaim", ids)
        self.assertIn("pattern.circular_signature", ids)
        self.assertTrue((output / "report.md").is_file())

    def test_end_to_end_compare(self):
        output = self.root / "comparison"
        result = self.cli("compare", FIXTURES / "flawed_manuscript.md",
                          FIXTURES / "revised_manuscript.md", "--out", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((output / "comparison.json").read_text())
        self.assertTrue(data["concerns_resolved"])
        self.assertTrue((output / "prior-report.json").is_file())
        self.assertTrue((output / "comparison.md").is_file())

    def test_review_prior_equivalent_workflow(self):
        result = self.cli("review", FIXTURES / "revised_manuscript.md", "--prior",
                          FIXTURES / "flawed_manuscript.md", "--out", self.root / "prior")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "prior/comparison.json").exists())

    def test_actionable_error_without_traceback(self):
        result = self.cli("review", self.root / "missing.pdf")
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not exist", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_silent_output_overwrite(self):
        output = self.root / "existing"
        output.mkdir()
        (output / "report.md").write_text("Keep me")
        result = self.cli("review", FIXTURES / "flawed_manuscript.md", "--out", output)
        self.assertEqual(result.returncode, 2)
        self.assertEqual((output / "report.md").read_text(), "Keep me")
        self.assertFalse((output / "report.json").exists())

    def test_input_protected_even_with_force(self):
        paper = self.write("Methods\n\nWe used 12 patients.", "report.md")
        result = self.cli("review", paper, "--out", self.root, "--force")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Refusing to overwrite an input", result.stderr)
        self.assertIn("12 patients", paper.read_text())


    def test_bedrock_json_mode_is_wired_through_cli(self):
        output = self.root / "bedrock-preview"
        result = self.cli(
            "review", FIXTURES / "flawed_manuscript.md",
            "--llm", "--provider", "bedrock", "--model", "test-model",
            "--region", "us-west-2", "--bedrock-json-mode", "prompt",
            "--dry-run", "--out", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        request = json.loads(next((output / "requests").glob("*.json")).read_text())
        self.assertNotIn("toolConfig", request["body"])
        self.assertNotIn("textFormat", request["body"].get("outputConfig", {}))
        self.assertEqual(
            json.loads((output / "llm-run.json").read_text())["json_mode"], "prompt")

    def test_list_rules(self):
        result = self.cli("list-rules")
        self.assertEqual(result.returncode, 0)
        self.assertIn("feature_selection_before_split", result.stdout)
        self.assertIn("perturbation_efficiency", result.stdout)
