"""Boundary regressions: disposable sources and mocked transports only."""
import contextlib
import io
import os
import sys
from unittest.mock import Mock, patch

from manuscript_review.cli import _save, main
from manuscript_review.errors import ReviewError
from manuscript_review.grounding import resolve_citations
from manuscript_review.providers.bedrock import BedrockReviewer, BedrockSettings
from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
from manuscript_review.reviewers import llm_packet
from manuscript_review.reporting import render_markdown
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, envelope, response


class OutputHardeningTests(WorkspaceTest):
    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(list(map(str, args)))

    def test_force_preserves_manuscript_in_stale_prompt_folder(self):
        prompts = self.root / "prompts"
        prompts.mkdir()
        paper = prompts / "draft.md"
        paper.write_text(PAPER)
        status = self.invoke("review", paper, "--out", self.root, "--force")
        self.assertEqual(status, 2)
        self.assertEqual(paper.read_text(), PAPER)
        self.assertFalse((self.root / "report.json").exists())

    def test_force_preserves_environment_configuration_in_stale_output(self):
        config = self.write("{}", "diagnostics.json")
        paper = self.write(PAPER)
        with patch.dict(os.environ, {"MANUSCRIPT_REVIEW_CONFIG": str(config)}):
            status = self.invoke("review", paper, "--out", self.root, "--force")
        self.assertEqual(status, 2)
        self.assertEqual(config.read_text(), "{}")

    def test_force_preserves_input_symlink_inside_cleanup_folder(self):
        paper = self.write(PAPER)
        output = self.root / "review"
        prompts = output / "prompts"
        prompts.mkdir(parents=True)
        alias = prompts / "draft.md"
        alias.symlink_to(paper)
        status = self.invoke("review", alias, "--out", output, "--force")
        self.assertEqual(status, 2)
        self.assertTrue(alias.is_symlink())
        self.assertEqual(paper.read_text(), PAPER)

    def test_invalid_output_plan_does_not_delete_old_artifacts(self):
        old = self.write("previous diagnostics", "diagnostics.json")
        paper = self.write(PAPER, "report.md")
        with self.assertRaises(ReviewError):
            _save(self.root, {"report.md": "replacement"}, [paper], force=True)
        self.assertEqual(old.read_text(), "previous diagnostics")
        self.assertEqual(paper.read_text(), PAPER)

    def test_output_collision_is_checked_before_any_provider_call(self):
        paper = self.write(PAPER, "report.md")
        transport = Mock(return_value=response(envelope()))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        with patch("manuscript_review.cli._provider", return_value=provider):
            status = self.invoke("review", paper, "--llm", "--out", self.root, "--force")
        self.assertEqual(status, 2)
        transport.assert_not_called()
        self.assertEqual(paper.read_text(), PAPER)

    def test_invalid_output_parent_is_checked_before_any_provider_call(self):
        parent = self.write("keep", "not-a-folder")
        paper = self.write(PAPER)
        transport = Mock(return_value=response(envelope()))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        with patch("manuscript_review.cli._provider", return_value=provider):
            status = self.invoke("review", paper, "--llm", "--out", parent / "review")
        self.assertEqual(status, 2)
        transport.assert_not_called()
        self.assertEqual(parent.read_text(), "keep")

    def test_escaping_output_symlink_is_checked_before_any_provider_call(self):
        directory = self.root / "review"
        directory.mkdir()
        untouched = self.write("keep", "outside.md")
        (directory / "report.md").symlink_to(untouched)
        paper = self.write(PAPER)
        transport = Mock(return_value=response(envelope()))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        with patch("manuscript_review.cli._provider", return_value=provider):
            status = self.invoke("review", paper, "--llm", "--out", directory, "--force")
        self.assertEqual(status, 2)
        transport.assert_not_called()
        self.assertEqual(untouched.read_text(), "keep")


class ProviderHardeningTests(WorkspaceTest):
    def packet(self):
        review = self.review_text(PAPER)
        return llm_packet("scientific", review.documents, review.extraction, review.findings, None)

    def test_missing_validator_blocks_both_live_providers_before_transport(self):
        constructors = (
            (OpenAIReviewer, OpenAISettings("test-model")),
            (BedrockReviewer, BedrockSettings("test-model", region="us-west-2")),
        )
        packet = self.packet()
        for reviewer, settings in constructors:
            with self.subTest(provider=reviewer.name), patch.dict(sys.modules, {"jsonschema": None}):
                transport = Mock(return_value=response(envelope()))
                with self.assertRaises(ReviewError):
                    provider = reviewer(settings, transport=transport)
                    provider.review("scientific", packet)
                transport.assert_not_called()

    def test_openai_outbound_schema_requires_all_fields_without_changing_local_contract(self):
        from copy import deepcopy
        from jsonschema import Draft202012Validator
        from manuscript_review.providers.contracts import REVIEW_SCHEMA, COMPARISON_SCHEMA
        original = deepcopy(REVIEW_SCHEMA)
        provider = OpenAIReviewer(OpenAISettings("test-model"), dry_run=True)

        def check(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    self.assertEqual(set(value["required"]), set(value["properties"]))
                    self.assertIs(value["additionalProperties"], False)
                for child in value.values():
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)

        for schema in (REVIEW_SCHEMA, COMPARISON_SCHEMA):
            body = provider.prepare("scientific", self.packet(), schema)
            check(body["text"]["format"]["schema"])
        outbound = provider.prepare("scientific", self.packet())["text"]["format"]["schema"]
        action = outbound["properties"]["findings"]["items"]["properties"]["action"]
        nullable_action = {key: None for key in action["properties"]}
        nullable_action["kind"] = "none"
        Draft202012Validator(action).validate(nullable_action)
        self.assertEqual(REVIEW_SCHEMA, original)
        self.assertEqual(REVIEW_SCHEMA["properties"]["findings"]["items"]["properties"]["action"]["required"], ["kind"])

    def test_malformed_bedrock_envelope_is_a_controlled_failure(self):
        for output in (None, [], "invalid"):
            with self.subTest(output=output):
                provider = BedrockReviewer(
                    BedrockSettings("test-model", region="us-west-2"),
                    transport=Mock(return_value={"stopReason": "tool_use", "output": output}))
                with self.assertRaises(ReviewError):
                    provider.review("scientific", self.packet())
                self.assertEqual(provider.calls[0]["status"], "invalid_response")

    def test_bedrock_rejects_wrong_or_multiple_tool_names(self):
        correct = {"toolUse": {"name": "manuscript_scientific", "input": envelope()}}
        wrong = {"toolUse": {"name": "unrequested_tool", "input": envelope()}}
        malformed = {"toolUse": {"name": "manuscript_scientific", "input": "bad"}}
        for content in ([wrong], [correct, malformed]):
            with self.subTest(content=content):
                provider = BedrockReviewer(
                    BedrockSettings("test-model", region="us-west-2"),
                    transport=Mock(return_value={"stopReason": "tool_use", "output": {
                        "message": {"role": "assistant", "content": content}}}))
                with self.assertRaises(ReviewError):
                    provider.review("scientific", self.packet())

    def test_malformed_expert_citation_has_actionable_error(self):
        review = self.review_text(PAPER)
        for citations in ([{"block_id": [], "quote": "invalid"}], None, "invalid"):
            with self.subTest(citations=citations), self.assertRaises(ReviewError):
                resolve_citations(citations, review.documents)


class ReviewCoverageTests(WorkspaceTest):
    def test_failed_panel_is_labeled_before_revision_brief(self):
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"],
                                  transport=Mock(side_effect=ReviewError("Connection failed.")))
        report = self.review_text(PAPER, provider=provider)
        markdown = render_markdown(report)
        opening = markdown.split("## Revision brief")[0]
        self.assertIn("provider-assisted", opening)
        self.assertIn("Incomplete LLM review", opening)
        self.assertIn("scientific", opening)
        self.assertNotIn("offline deterministic audit", opening)

    def test_excluded_items_are_visible_without_failing_whole_role(self):
        from .llm_helpers import finding, packet_block
        def transport(body, timeout):
            valid = finding(packet_block(body))
            return response(envelope([valid, {"id": "malformed"}]))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        report = self.review_text(PAPER, provider=provider)
        self.assertEqual(report.quality["failed_roles"], [])
        self.assertTrue(any(f.origin == "provider:openai" for f in report.findings))
        opening = render_markdown(report).split("## Revision brief")[0]
        self.assertIn("1 output item(s) rejected", opening)
        self.assertIn("not independent evidence", opening)

    def test_preview_cannot_look_like_completed_panel(self):
        provider = OpenAIReviewer(OpenAISettings("test-model"), dry_run=True)
        opening = render_markdown(self.review_text(PAPER, provider=provider)).split("## Revision brief")[0]
        self.assertIn("request preview; no model judgment performed", opening)
        self.assertNotIn("**Mode:** provider-assisted", opening)
