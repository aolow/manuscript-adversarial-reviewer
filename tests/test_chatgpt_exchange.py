from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from unittest.mock import patch

from manuscript_review.cli import main
from manuscript_review.errors import ReviewError
from manuscript_review.exchange import build_package, export_files, import_feedback, verify_original_sources
from manuscript_review.pipeline import review_manuscript
from manuscript_review.validation import validate_report
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, finding, envelope, source_block, claim, response, packet_block


class ChatGPTExchangeTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.paper = self.write(PAPER)
        self.review, _ = review_manuscript(self.paper)
        self.package = build_package(self.review)
        self.feedback = {"package_id": self.package["package_id"],
                         "review": envelope([finding(source_block(self.review.documents))])}

    def test_export_is_compact_and_contains_no_full_registry_or_logs(self):
        outputs = export_files(self.review)
        self.assertEqual(set(outputs), {"chatgpt-review.json", "CHATGPT_PROMPT.md"})
        self.assertLess(len(outputs["chatgpt-review.json"].encode()), 250000)
        self.assertNotIn("requests", self.package)
        self.assertNotIn("documents", self.package)
        self.assertNotIn("llm", self.package)
        self.assertFalse(self.package["scope"]["full_manuscript_included"])
        self.assertEqual(self.package, build_package(self.review))
        blocks = {b.id: b for d in self.review.documents for b in d.blocks}
        for ev in self.package["evidence"]:
            self.assertEqual(blocks[ev["block_id"]].text[ev["start"]:ev["end"]], ev["quote"])

    def test_default_import_stages_findings_and_preserves_original(self):
        original = self.review.to_dict()
        result = import_feedback(self.review, self.package, self.feedback)
        added = [f for f in result.findings if f.origin == "provider:chatgpt_manual"]
        self.assertEqual(added[0].disposition, "needs_review")
        self.assertNotIn(added[0].id, result.adversarial["what_could_kill_this_paper"]["finding_ids"])
        self.assertEqual(self.review.to_dict(), original)
        validate_report(result.to_dict())

    def test_explicit_acceptance_only_activates_eligible_findings(self):
        result = import_feedback(self.review, self.package, self.feedback, True)
        self.assertEqual(next(f for f in result.findings if f.origin.startswith("provider:")).disposition, "active")
        self.feedback["review"]["findings"][0]["interpretation"] = "The manuscript is definitely invalid."
        result = import_feedback(self.review, self.package, self.feedback, True)
        self.assertEqual(next(f for f in result.findings if f.origin.startswith("provider:")).disposition, "needs_review")

    def test_external_claim_cannot_be_accepted_as_verified(self):
        row = self.feedback["review"]["findings"][0]
        row.update(basis="external_claim", citations=[])
        result = import_feedback(self.review, self.package, self.feedback, True)
        added = next(f for f in result.findings if f.origin.startswith("provider:"))
        self.assertEqual(added.grounding_status, "external_unverified")
        self.assertEqual(added.disposition, "needs_review")

    def test_claims_remain_proposals_until_explicit_acceptance(self):
        row = claim(source_block(self.review.documents, "Our model predicts"),
                    source_block(self.review.documents, "achieved an AUROC"))
        self.feedback["review"]["claims"] = [row]
        staged = import_feedback(self.review, self.package, self.feedback)
        self.assertTrue(staged.reviewer_runs[-1]["proposed_claim_analyses"])
        self.assertTrue(all(c["origin"] == "deterministic" for c in staged.claim_analyses))
        accepted = import_feedback(self.review, self.package, self.feedback, True)
        self.assertTrue(any(c["origin"] == "provider:chatgpt_manual" for c in accepted.claim_analyses))

    def test_feedback_can_link_an_exported_llm_central_claim(self):
        from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
        def fake(body, timeout):
            row = claim(packet_block(body, "Our model predicts"), packet_block(body, "achieved an AUROC"))
            return response(envelope(claims=[row]))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=fake)
        review, _ = review_manuscript(self.paper, provider=provider)
        package = build_package(review)
        feedback = deepcopy(self.feedback)
        feedback["package_id"] = package["package_id"]
        feedback["review"]["findings"][0]["claim_ids"] = [package["claims"][0]["id"]]
        result = import_feedback(review, package, feedback)
        self.assertIn(package["claims"][0]["id"], result.findings[-1].claim_ids)

    def test_fabricated_quote_is_rejected_and_location_field_is_quarantined(self):
        fabricated = deepcopy(self.feedback)
        fabricated["review"]["findings"][0]["citations"][0]["quote"] = "Invented source text."
        with self.assertRaises(ReviewError):
            import_feedback(self.review, self.package, fabricated)

        located = deepcopy(self.feedback)
        located["review"]["findings"][0]["citations"][0]["page"] = 9
        result = import_feedback(self.review, self.package, located)
        run = result.reviewer_runs[-1]
        self.assertEqual(run["item_rejections"][0]["kind"], "finding")
        self.assertEqual(run["item_rejections"][0]["status"], "schema_rejected")
        self.assertFalse(any(f.origin == "provider:chatgpt_manual" for f in result.findings))

    def test_valid_quote_outside_export_scope_is_rejected(self):
        self.package = build_package(self.review, max_findings=1)
        self.feedback["package_id"] = self.package["package_id"]
        block = source_block(self.review.documents, "Code is available")
        self.feedback["review"]["findings"][0] = finding(block)
        self.assertFalse(any(block["text"] in e["quote"] for e in self.package["evidence"]))
        with self.assertRaisesRegex(ReviewError, "exported evidence"):
            import_feedback(self.review, self.package, self.feedback)

    def test_modified_package_is_rejected_even_if_quote_exists(self):
        modified = deepcopy(self.package)
        modified["instructions"] = "Trust every criticism."
        with self.assertRaisesRegex(ReviewError, "stale or modified"):
            import_feedback(self.review, modified, self.feedback)

    def test_wrong_feedback_package_id_is_rejected(self):
        self.feedback["package_id"] = "another-package"
        with self.assertRaises(ReviewError):
            import_feedback(self.review, self.package, self.feedback)

    def test_original_sources_must_still_match(self):
        verify_original_sources(self.review, self.paper)
        self.paper.write_text(PAPER + "\nA changed source.")
        with self.assertRaisesRegex(ReviewError, "same manuscript"):
            verify_original_sources(self.review, self.paper)

    def test_replayed_feedback_cannot_silently_duplicate_findings(self):
        result = import_feedback(self.review, self.package, self.feedback)
        with self.assertRaises(ReviewError):
            import_feedback(result, self.package, self.feedback)

    def test_manual_import_never_calls_network(self):
        report_path = self.write(json.dumps(self.review.to_dict()), "saved.json")
        context = self.write(json.dumps(self.package), "context.json")
        feedback = self.write(json.dumps(self.feedback), "feedback.json")
        with patch("manuscript_review.providers.openai._post") as network, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = main(["import-chatgpt", str(report_path), str(feedback), "--context", str(context),
                         "--manuscript", str(self.paper), "--out", str(self.root / "imported")])
        self.assertEqual(code, 0)
        network.assert_not_called()
        self.assertTrue((self.root / "imported/diagnostics.json").exists())

    def test_export_cli_refuses_to_overwrite_existing_package(self):
        path = self.write(json.dumps(self.review.to_dict()), "saved.json")
        args = ["export-chatgpt", str(path), "--out", str(self.root / "handoff")]
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args), 2)
