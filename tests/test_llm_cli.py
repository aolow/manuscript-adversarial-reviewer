from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

from manuscript_review.cli import main
from .helpers import WorkspaceTest, FIXTURES
from .llm_helpers import envelope, response, finding, packet_block, PAPER


class LlmCliTests(WorkspaceTest):
    def call(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(map(str, args)))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_deterministic_cli_never_contacts_api_even_with_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post") as network:
            code, _, err = self.call("review", FIXTURES / "flawed_manuscript.md", "--out", self.root / "offline")
        self.assertEqual(code, 0, err)
        network.assert_not_called()

    def test_model_argument_alone_is_not_opt_in(self):
        code, _, err = self.call("review", FIXTURES / "flawed_manuscript.md", "--model", "test-model")
        self.assertEqual(code, 2)
        self.assertIn("opt-in", err)

    def test_dry_run_exports_six_exact_requests_without_key(self):
        with patch.dict(os.environ, {}, clear=True), patch("manuscript_review.providers.openai._post") as network:
            code, output, err = self.call("review", FIXTURES / "flawed_manuscript.md", "--llm",
                                          "--model", "test-model", "--dry-run", "--out", self.root / "dry")
        self.assertEqual(code, 0, err)
        network.assert_not_called()
        self.assertIn("6 exact", output)
        paths = list((self.root / "dry/requests").glob("*.json"))
        self.assertEqual(len(paths), 6)
        for path in paths:
            data = json.loads(path.read_text())
            self.assertNotIn("Authorization", data)
            self.assertEqual(data["body"]["model"], "test-model")

    def test_bedrock_dry_run_exports_converse_request_without_boto3(self):
        with patch.dict(os.environ, {}, clear=True):
            code, output, err = self.call(
                "review", FIXTURES / "flawed_manuscript.md", "--llm",
                "--provider", "bedrock", "--model", "test-bedrock-model",
                "--region", "us-west-2", "--dry-run", "--roles", "scientific",
                "--out", self.root / "bedrock-dry")
        self.assertEqual(code, 0, err)
        self.assertIn("1 exact", output)
        request = json.loads((self.root / "bedrock-dry/requests/scientific.json").read_text())
        self.assertEqual(request["endpoint"], "bedrock-runtime:Converse")
        self.assertEqual(request["region"], "us-west-2")
        self.assertEqual(request["body"]["modelId"], "test-bedrock-model")
        self.assertEqual(request["body"]["toolConfig"]["toolChoice"]["tool"]["name"], "manuscript_scientific")
        self.assertIsInstance(request["body"]["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"], dict)
        self.assertNotIn("outputConfig", request["body"])
        self.assertEqual(request["body"]["inferenceConfig"]["maxTokens"], 24000)
        run = json.loads((self.root / "bedrock-dry/llm-run.json").read_text())
        self.assertEqual(run["settings"]["timeout_seconds"], 600)

    def test_environment_model_and_temperature(self):
        with patch.dict(os.environ, {"MANUSCRIPT_REVIEW_MODEL": "env-model",
                                     "MANUSCRIPT_REVIEW_TEMPERATURE": "0.25"}, clear=True):
            code, _, err = self.call("review", FIXTURES / "flawed_manuscript.md", "--llm",
                                     "--dry-run", "--roles", "scientific", "--out", self.root / "env")
        self.assertEqual(code, 0, err)
        body = json.loads((self.root / "env/requests/scientific.json").read_text())["body"]
        self.assertEqual(body["model"], "env-model")
        self.assertEqual(body["temperature"], 0.25)

    def test_cli_fake_live_output_is_validated_and_labeled(self):
        def fake(body, timeout):
            return response(envelope([finding(packet_block(body))]))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post", side_effect=fake):
            code, _, err = self.call("review", self.write(PAPER), "--llm", "--model", "test-model",
                                     "--roles", "methods,computational", "--out", self.root / "fake")
        self.assertEqual(code, 0, err)
        data = json.loads((self.root / "fake/report.json").read_text())
        self.assertTrue(any(f["origin"] == "provider:openai" for f in data["findings"]))
        self.assertTrue(data["quality"]["duplicate_groups"])
        self.assertIn("What could kill this paper", (self.root / "fake/report.md").read_text())

    def test_cli_provider_failure_returns_partial_status_and_preserves_report(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post", return_value=response({"invalid": True})):
            code, output, _ = self.call("review", self.write(PAPER), "--llm", "--model", "test-model",
                                        "--roles", "scientific", "--out", self.root / "failed")
        self.assertEqual(code, 3)
        self.assertIn("deterministic output preserved", output)
        self.assertIn("schema_rejected", output)
        self.assertTrue((self.root / "failed/report.json").exists())

    def test_paired_dry_run_exports_one_comparison_request(self):
        with patch.dict(os.environ, {}, clear=True), patch("manuscript_review.providers.openai._post") as network:
            code, output, err = self.call("compare", FIXTURES / "flawed_manuscript.md",
                                          FIXTURES / "revised_manuscript.md", "--llm", "--model", "test-model",
                                          "--dry-run", "--out", self.root / "pair")
        self.assertEqual(code, 0, err)
        network.assert_not_called()
        self.assertIn("1 exact", output)
        body = json.loads((self.root / "pair/requests/comparison.json").read_text())["body"]
        data = json.loads(body["input"][0]["content"])
        self.assertTrue(data["old_source_blocks"])
        self.assertTrue(data["new_source_blocks"])

    def test_output_collision_prevents_api_calls(self):
        output = self.root / "collision"
        output.mkdir()
        (output / "report.json").write_text("{}")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"}), patch(
                "manuscript_review.providers.openai._post") as network:
            code, _, err = self.call("review", self.write(PAPER), "--llm", "--model", "test-model", "--out", output)
        self.assertEqual(code, 2)
        self.assertIn("No API calls", err)
        network.assert_not_called()

    def test_saved_prior_llm_concerns_are_in_comparison_request(self):
        from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
        from manuscript_review.pipeline import review_manuscript
        paper = self.write(PAPER)
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"],
                                  transport=lambda b, t: response(envelope([finding(packet_block(b))])))
        prior, _ = review_manuscript(paper, provider=provider)
        provider_id = next(f.id for f in prior.findings if f.origin.startswith("provider:"))
        saved = self.write(json.dumps(prior.to_dict()), "prior.json")
        code, _, err = self.call("compare", paper, paper, "--prior-review", saved,
                                 "--llm", "--model", "test-model", "--dry-run", "--out", self.root / "saved")
        self.assertEqual(code, 0, err)
        request = json.loads((self.root / "saved/requests/comparison.json").read_text())
        payload = json.loads(request["body"]["input"][0]["content"])
        self.assertIn(provider_id, {f["id"] for f in payload["prior_issues"]})

    def test_stale_saved_prior_review_refused_without_upload(self):
        from manuscript_review.pipeline import review_manuscript
        paper = self.write(PAPER)
        prior, _ = review_manuscript(paper)
        saved = self.write(json.dumps(prior.to_dict()), "prior.json")
        paper.write_text(PAPER + "\nA changed manuscript.")
        with patch("manuscript_review.providers.openai._post") as network:
            code, _, err = self.call("compare", paper, paper, "--prior-review", saved,
                                     "--llm", "--model", "test-model", "--dry-run", "--out", self.root / "stale")
        self.assertEqual(code, 2)
        self.assertIn("hashes", err)
        network.assert_not_called()

    def test_forged_saved_source_with_original_hash_is_refused(self):
        from manuscript_review.pipeline import review_manuscript
        paper = self.write(PAPER)
        prior, _ = review_manuscript(paper)
        data = prior.to_dict()
        data["documents"][0]["blocks"][0]["text"] = "# A forged heading"
        saved = self.write(json.dumps(data), "forged.json")
        code, _, err = self.call("compare", paper, paper, "--prior-review", saved, "--out", self.root / "forged")
        self.assertEqual(code, 2)
        self.assertIn("source blocks differ", err)
