from unittest.mock import Mock

from manuscript_review.errors import ReviewError
from manuscript_review.pipeline import review_manuscript
from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, response, envelope, finding, packet_block


class PilotDiagnosticsTests(WorkspaceTest):
    def review(self, transport, roles=("scientific",)):
        provider = OpenAIReviewer(OpenAISettings("test-model", reasoning_effort="high"),
                                  roles=roles, transport=transport)
        report, _ = review_manuscript(self.write(PAPER), provider=provider)
        return report, provider

    def test_usage_kept_when_response_is_incomplete(self):
        raw = response(envelope())
        raw["status"] = "incomplete"
        report, provider = self.review(Mock(return_value=raw))
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["attempted_api_calls"], 1)
        self.assertEqual(data["schema_accepted_calls"], 0)
        self.assertEqual(data["usage"]["input_tokens"], 100)
        self.assertEqual(data["incomplete_roles"], ["scientific"])
        self.assertIsNone(data["estimated_cost_usd"])

    def test_invalid_schema_retains_raw_count_and_usage(self):
        report, _ = self.review(Mock(return_value=response({"findings": [{}]})))
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["raw_findings_known"], 1)
        self.assertEqual(data["rejected_findings_known"], 1)
        self.assertEqual(data["usage"]["output_tokens"], 200)

    def test_citation_rejection_is_visible_after_schema_acceptance(self):
        def fake(body, timeout):
            row = finding(packet_block(body))
            row["citations"][0]["quote"] = "A fabricated scientific statement in the manuscript."
            return response(envelope([row]))
        report, _ = self.review(fake)
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["schema_accepted_calls"], 1)
        self.assertEqual(data["accepted_findings"], 0)
        self.assertEqual(data["rejected_findings_known"], 1)
        self.assertEqual(data["incomplete_roles"], [])

    def test_accepted_quarantined_and_duplicate_counts_are_separate(self):
        def fake(body, timeout):
            good = finding(packet_block(body))
            bad = finding(packet_block(body), "unsupported")
            bad["citations"] = []
            return response(envelope([good, bad]))
        report, _ = self.review(fake, ("methods", "computational"))
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["raw_findings_known"], 4)
        self.assertEqual(data["accepted_findings"], 1)
        self.assertEqual(data["quarantined_findings"], 2)
        self.assertEqual(data["merged_duplicates"], 1)

    def test_invalid_finding_citation_is_rejected_without_failing_role(self):
        def fake(body, timeout):
            row = finding(packet_block(body))
            row["citations"][0]["block_id"] = "fabricated"
            return response(envelope([row]))
        report, _ = self.review(fake)
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["failures"], [])
        self.assertEqual(data["incomplete_roles"], [])
        self.assertEqual(data["schema_accepted_calls"], 1)
        self.assertEqual(data["accepted_findings"], 0)
        self.assertEqual(data["rejected_findings_known"], 1)

    def test_transport_failure_has_unknown_usage_not_zero(self):
        report, _ = self.review(Mock(side_effect=ReviewError("Connection failed.")))
        data = report.quality["pilot_diagnostics"]
        self.assertIsNone(data["usage"]["input_tokens"])
        self.assertFalse(data["raw_count_complete"])
        self.assertEqual(data["failures"][0]["status"], "transport_error")

    def test_cached_and_reasoning_tokens_are_not_double_counted(self):
        raw = response(envelope())
        raw["usage"].update(input_tokens_details={"cached_tokens": 40},
                            output_tokens_details={"reasoning_tokens": 75},
                            total_tokens=300, unexpected_secret="DO NOT KEEP")
        report, _ = self.review(Mock(return_value=raw))
        data = report.quality["pilot_diagnostics"]["usage"]
        self.assertEqual(data["total_tokens"], 300)
        self.assertEqual(data["cached_tokens"], 40)
        self.assertNotIn("DO NOT KEEP", str(report.llm))

    def test_dry_run_has_zero_attempts_and_no_estimated_tokens(self):
        provider = OpenAIReviewer(OpenAISettings("test-model"), dry_run=True)
        report, _ = review_manuscript(self.write(PAPER), provider=provider)
        data = report.quality["pilot_diagnostics"]
        self.assertEqual(data["attempted_api_calls"], 0)
        self.assertEqual(data["prepared_requests"], 6)
        self.assertIsNone(data["usage"]["input_tokens"])

    def test_malformed_provider_content_is_a_controlled_failure(self):
        for output in (None, [{"type": "message", "content": None}], [{"type": "message", "content": [None]}]):
            with self.subTest(output=output):
                report, _ = self.review(Mock(return_value={"status": "completed", "output": output}))
                self.assertEqual(report.quality["failed_roles"], ["scientific"])
