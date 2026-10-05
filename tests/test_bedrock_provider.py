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

    def response(self, payload, stop_reason="tool_use", mode="tool"):
        content = (
            [{"toolUse": {
                "toolUseId": "tool-1",
                "name": "manuscript_scientific",
                "input": payload,
            }}]
            if mode == "tool"
            else [{"text": json.dumps(payload)}]
        )
        return {
            "stopReason": stop_reason,
            "usage": {"inputTokens": 100, "outputTokens": 200, "totalTokens": 300},
            "output": {"message": {"role": "assistant", "content": content}},
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
        self.assertNotIn("outputConfig", body)
        self.assertEqual(
            body["toolConfig"]["toolChoice"]["tool"]["name"], "manuscript_scientific")
        schema = body["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"]
        self.assertIsInstance(schema, dict)

    def test_outbound_schema_uses_bedrock_supported_subset(self):
        provider = BedrockReviewer(BedrockSettings("test-model", region="us-west-2"), dry_run=True)
        body = provider.prepare("scientific", self.packet())
        schema = body["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"]

        def keys(value):
            if isinstance(value, dict):
                result = set(value)
                for child in value.values():
                    result.update(keys(child))
                return result
            if isinstance(value, list):
                result = set()
                for child in value:
                    result.update(keys(child))
                return result
            return set()

        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("anyOf", keys(schema))
        self.assertIn("minLength", keys(schema))
        self.assertIn("maxLength", keys(schema))
        self.assertIn("pattern", keys(schema))
        self.assertIn("maxItems", keys(schema))
        self.assertEqual(schema["properties"]["findings"]["maxItems"], 30)
        finding_schema = schema["properties"]["findings"]["items"]
        self.assertEqual(finding_schema["properties"]["title"]["maxLength"], 500)
        self.assertEqual(finding_schema["properties"]["title"]["minLength"], 1)
        self.assertIn("pattern", finding_schema["properties"]["id"])
        action = finding_schema["properties"]["action"]
        self.assertNotIn("input", action.get("required", []))
        self.assertEqual(action["properties"]["input"]["type"], "string")
        self.assertEqual(action["properties"]["input"]["maxLength"], 4000)

    def test_prompt_mode_keeps_conservative_schema_stripping(self):
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2", json_mode="prompt"),
            dry_run=True)
        body = provider.prepare("scientific", self.packet())
        system_text = body["system"][0]["text"]
        self.assertNotIn('"maxLength"', system_text)
        self.assertNotIn('"maxItems"', system_text)
        self.assertNotIn('"pattern"', system_text)

    def test_full_local_schema_still_rejects_invalid_bedrock_output(self):
        packet = self.packet()
        row = finding(self.block(packet))
        row["id"] = "INVALID ID"
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2"),
            transport=Mock(return_value=self.response(envelope([row]))))
        with self.assertRaises(ReviewError):
            provider.review("scientific", packet)

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

    def test_bedrock_temperature_effort_and_mode_validation(self):
        for settings in (
            BedrockSettings("test-model", region="us-west-2", temperature=1.1),
            BedrockSettings("test-model", region="us-west-2", temperature=0.2, reasoning_effort="high"),
            BedrockSettings("test-model", region="us-west-2", reasoning_effort="minimal"),
            BedrockSettings("test-model", region="us-west-2", reasoning_effort="high"),
            BedrockSettings("test-model", region="us-west-2", json_mode="other"),
        ):
            with self.subTest(settings=settings), self.assertRaises(ReviewError):
                BedrockReviewer(settings, dry_run=True)

    def test_prompt_mode_is_zero_structured_output_dependency_fallback(self):
        packet = self.packet()
        payload = envelope([finding(self.block(packet))])
        transport = Mock(return_value=self.response(payload, stop_reason="end_turn", mode="prompt"))
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2", json_mode="prompt"),
            transport=transport)
        result = provider.review("scientific", packet)
        body = transport.call_args.args[0]
        self.assertEqual(len(result["findings"]), 1)
        self.assertNotIn("toolConfig", body)
        self.assertNotIn("outputConfig", body)
        self.assertIn('"findings"', body["system"][0]["text"])

    def test_effort_is_prompt_mode_only(self):
        provider = BedrockReviewer(
            BedrockSettings(
                "test-model", region="us-west-2",
                reasoning_effort="high", json_mode="prompt"),
            dry_run=True)
        body = provider.prepare("scientific", self.packet())
        self.assertEqual(body["outputConfig"]["effort"], "high")
        self.assertNotIn("toolConfig", body)
        self.assertNotIn("temperature", body["inferenceConfig"])

    def test_tool_mode_requires_tool_output(self):
        provider = BedrockReviewer(
            BedrockSettings("test-model", region="us-west-2"),
            transport=Mock(return_value=self.response(
                envelope(), stop_reason="end_turn", mode="prompt")))
        with self.assertRaisesRegex(ReviewError, "no tool output"):
            provider.review("scientific", self.packet())
