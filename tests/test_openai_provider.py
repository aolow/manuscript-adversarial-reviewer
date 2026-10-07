from copy import deepcopy
import json
import os
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from manuscript_review.errors import ReviewError
from manuscript_review.pipeline import review_manuscript
from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings, _post
from manuscript_review.providers.contracts import REVIEW_SCHEMA
from manuscript_review.reviewers import llm_packet
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, envelope, finding, response, packet_block


class OpenAIProviderTests(WorkspaceTest):
    def packet(self):
        report = self.review_text(PAPER)
        return llm_packet("scientific", report.documents, report.extraction, report.findings, None)

    def test_dry_run_never_reads_key_or_calls_transport(self):
        transport = Mock(side_effect=AssertionError("network attempted"))
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIReviewer(OpenAISettings("test-model"), dry_run=True, transport=transport)
            result = provider.review("scientific", self.packet())
        self.assertEqual(result, envelope())
        transport.assert_not_called()
        self.assertEqual(provider.metadata()["completed_calls"], 0)

    def test_exact_dry_run_request_matches_live_request(self):
        packet = self.packet()
        dry = OpenAIReviewer(OpenAISettings("test-model"), dry_run=True)
        transport = Mock(return_value=response(envelope()))
        live = OpenAIReviewer(OpenAISettings("test-model"), transport=transport)
        dry.review("scientific", packet)
        live.review("scientific", packet)
        self.assertEqual(dry.requests[0]["body"], transport.call_args.args[0])
        self.assertEqual(dry.requests[0]["sha256"], live.requests[0]["sha256"])
        self.assertFalse(dry.requests[0]["body"]["store"])
        self.assertNotIn("tools", dry.requests[0]["body"])

    def test_all_role_requests_are_static_even_after_a_model_finding(self):
        captured = []
        def transport(body, timeout):
            captured.append(deepcopy(body))
            return response(envelope([finding(packet_block(body))]))
        live = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific", "methods"], transport=transport)
        dry = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific", "methods"], dry_run=True)
        path = self.write(PAPER)
        review_manuscript(path, provider=live)
        review_manuscript(path, provider=dry)
        self.assertEqual(captured, [r["body"] for r in dry.requests])

    def test_no_default_model(self):
        with self.assertRaisesRegex(ReviewError, "requires --model"):
            OpenAIReviewer(OpenAISettings(""), dry_run=True)

    def test_live_mode_requires_environment_key(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ReviewError, "OPENAI_API_KEY"):
            OpenAIReviewer(OpenAISettings("test-model"))

    def test_temperature_reasoning_validation(self):
        for settings in (
            OpenAISettings("test-model", temperature=float("nan")),
            OpenAISettings("test-model", temperature=3),
            OpenAISettings("test-model", temperature=0.3, reasoning_effort="high"),
            OpenAISettings("test-model", max_output_tokens=-1),
        ):
            with self.subTest(settings=settings), self.assertRaises(ReviewError):
                OpenAIReviewer(settings, dry_run=True)

    def test_supported_settings_are_explicit_only(self):
        provider = OpenAIReviewer(OpenAISettings("test-model", reasoning_effort="high"), dry_run=True)
        body = provider.prepare("scientific", self.packet())
        self.assertEqual(body["reasoning"], {"effort": "high"})
        self.assertNotIn("temperature", body)

    def test_large_context_failure_is_isolated_to_role_without_network_call(self):
        transport = Mock()
        provider = OpenAIReviewer(
            OpenAISettings("test-model", max_request_chars=1000),
            roles=["scientific"], transport=transport)
        report, _ = review_manuscript(self.write(PAPER), provider=provider)
        transport.assert_not_called()
        self.assertEqual(report.quality["failed_roles"], ["scientific"])
        failure = report.quality["pilot_diagnostics"]["failures"][0]
        self.assertEqual(failure["status"], "request_preparation_rejected")
        self.assertIn("silently truncated", failure["reason"])

    def test_refusal_and_incomplete_outputs_are_rejected(self):
        cases = [
            {"status": "incomplete", "output": []},
            {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]},
        ]
        for raw in cases:
            provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=raw))
            with self.subTest(raw=raw), self.assertRaises(ReviewError):
                provider.review("scientific", self.packet())

    def test_invalid_json_and_invalid_schema_are_rejected(self):
        for raw in (
            {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": "not JSON"}]}]},
            response({"findings": "wrong"}),
        ):
            with self.subTest(raw=raw), self.assertRaises(ReviewError):
                OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=raw)).review("scientific", self.packet())

    def test_openai_envelope_schema_error_metadata_matches_bedrock_shape(self):
        payload = envelope()
        payload["findings"] = "wrong"
        provider = OpenAIReviewer(
            OpenAISettings("test-model"), transport=Mock(return_value=response(payload)))
        with self.assertRaises(ReviewError):
            provider.review("scientific", self.packet())
        error = provider.metadata()["calls"][0]["schema_error"]
        self.assertEqual(error, {"path": "findings", "validator": "type"})

    def test_explicit_clinical_role_runs_even_without_biomarker_domain(self):
        transport = Mock(return_value=response(envelope()))
        provider = OpenAIReviewer(
            OpenAISettings("test-model"), roles=["clinical"], transport=transport)
        report, _ = review_manuscript(
            self.write("Methods\n\nWe used 12 samples for a descriptive experiment."),
            provider=provider)
        self.assertEqual(transport.call_count, 1)
        run = next(r for r in report.reviewer_runs if r["role"] == "clinical")
        self.assertEqual(run["mode"], "provider")

    def test_role_failure_preserves_deterministic_findings(self):
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"],
                                  transport=Mock(return_value=response({"invalid": True})))
        report, _ = review_manuscript(self.write(PAPER), provider=provider)
        self.assertIn("pattern.feature_selection_before_split", {f.id for f in report.findings})
        self.assertEqual(report.quality["failed_roles"], ["scientific"])
        self.assertTrue(all(f.origin == "deterministic" for f in report.findings))

    def test_http_error_does_not_echo_credentials_or_manuscript(self):
        opener = Mock()
        opener.open.side_effect = HTTPError("https://api.openai.com", 401, "SECRET MANUSCRIPT", {}, None)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-secret"}), patch(
                "manuscript_review.providers.openai.request.build_opener", return_value=opener):
            with self.assertRaises(ReviewError) as caught:
                _post({"model": "test-model"}, 2)
        self.assertIn("HTTP 401", str(caught.exception))
        self.assertNotIn("SECRET", str(caught.exception))
        self.assertNotIn("test-secret", str(caught.exception))

    def test_ungrounded_output_does_not_enter_headline(self):
        def transport(body, timeout):
            row = finding(packet_block(body))
            row["citations"] = []
            return response(envelope([row]))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        report, _ = review_manuscript(self.write(PAPER), provider=provider)
        row = next(f for f in report.findings if f.origin.startswith("provider:"))
        self.assertEqual(row.disposition, "needs_review")
        self.assertNotIn(row.id, report.adversarial["what_could_kill_this_paper"]["finding_ids"])

    def test_headline_never_pads_or_exceeds_seven(self):
        report = self.review_text(PAPER)
        ids = report.adversarial["what_could_kill_this_paper"]["finding_ids"]
        self.assertLessEqual(len(ids), 7)
        self.assertEqual(len(ids), len(set(ids)))
