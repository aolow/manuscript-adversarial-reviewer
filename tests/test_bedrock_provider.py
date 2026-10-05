import json
from unittest.mock import Mock

from manuscript_review.errors import ReviewError
from manuscript_review.providers.bedrock import BedrockReviewer, BedrockSettings
from manuscript_review.reviewers import llm_packet
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, envelope, finding


class BedrockProviderTests(WorkspaceTest):
    def packet(self):
        report = self.review_text(PAPER)
        return llm_packet("scientific", report.documents, report.extraction, report.findings, None)

    def response(self, payload, stop_reason="end_turn"):
        return {
            "stopReason": stop_reason,
            "usage": {"inputTokens": 100, "outputTokens": 200, "totalTokens": 300},
            "output": {"message": {"role": "assistant", "content": [{"text": json.dumps(payload)}]}},
        }

    def block(self, packet, contains="We selected"):
        return next(b for b in packet["source_blocks"] if contains in b["text"])

    def test_dry_run_never_calls_transport_or_needs_boto3(self):
        transport = Mock(side_effect=AssertionError("network attempted"))
        provider = BedrockReviewer(BedrockSettings("test-model", region="us-west-2"),
                                   dry_run=True, transport=transport)
        result = provider.review("scientific", self.packet())
        self.assertEqual(result, envelope())
        transport.assert_not_called()
        self.assertEqual(provider.metadata()["completed_calls"], 0)

    def test_exact_dry_run_body_matches_live_body(self):
        packet = self.packet()
        dry = BedrockReviewer(BedrockSettings("test-model", region="us-west-2"), dry_run=True)
        transport = Mock(return_value=self.response(envelope()))
        live = BedrockReviewer(BedrockSettings("test-model", region="us-west-2"), transport=transport)
        dry.review("scientific", packet)
        live.review("scientific", packet)
        self.assertEqual(dry.requests[0]["body"], transport.call_args.args[0])
        self.assertEqual(dry.requests[0]["sha256"], live.requests[0]["sha256"])
        body = dry.requests[0]["body"]
        self.assertEqual(body["modelId"], "test-model")
        self.assertEqual(body["outputConfig"]["textFormat"]["type"], "json_schema")
        self.assertNotIn("toolConfig", body)

    def test_structured_finding_is_schema_validated(self):
        packet = self.packet()
        payload = envelope([finding(self.block(packet))])
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2"),
            transport=Mock(return_value=self.response(payload)))
        result = provider.review("scientific", packet)
        self.assertEqual(len(result["findings"]), 1)
        meta = provider.metadata()
        self.assertEqual(meta["completed_calls"], 1)
        self.assertEqual(meta["usage"]["input_tokens"], 100)
        self.assertEqual(meta["usage"]["output_tokens"], 200)

    def test_incomplete_or_filtered_output_is_rejected(self):
        for stop_reason in ("max_tokens", "content_filtered", "guardrail_intervened"):
            provider = BedrockReviewer(
                BedrockSettings("test-model", region="us-west-2"),
                transport=Mock(return_value=self.response(envelope(), stop_reason)))
            with self.subTest(stop_reason=stop_reason), self.assertRaises(ReviewError):
                provider.review("scientific", self.packet())

    def test_bedrock_temperature_and_effort_validation(self):
        for settings in (
            BedrockSettings("test-model", region="us-west-2", temperature=1.1),
            BedrockSettings("test-model", region="us-west-2", temperature=0.2, reasoning_effort="high"),
            BedrockSettings("test-model", region="us-west-2", reasoning_effort="minimal"),
        ):
            with self.subTest(settings=settings), self.assertRaises(ReviewError):
                BedrockReviewer(settings, dry_run=True)

    def test_effort_is_explicit_only(self):
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2", reasoning_effort="high"), dry_run=True)
        body = provider.prepare("scientific", self.packet())
        self.assertEqual(body["outputConfig"]["effort"], "high")
        self.assertNotIn("temperature", body["inferenceConfig"])
