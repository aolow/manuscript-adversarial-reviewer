from copy import deepcopy
from dataclasses import asdict
from unittest.mock import Mock

from manuscript_review.comparison import compare_reviews
from manuscript_review.errors import ReviewError
from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
from manuscript_review.resolution import add_semantic_comparison
from manuscript_review.validation import validate_comparison
from .helpers import WorkspaceTest
from .llm_helpers import response


class SemanticComparisonTests(WorkspaceTest):
    def versions(self):
        old = self.review_text("Abstract\n\nOur results prove a causal mechanism.\n\n"
                               "Methods\n\nWe developed a predictor using 12 patients.\n"
                               "We selected genes using all samples before splitting into training and test sets.")
        new = self.review_text("Abstract\n\nOur results suggest an association.\n\n"
                               "Methods\n\nWe developed a predictor using 12 patients.\n"
                               "We selected genes using all samples before splitting into training and test sets.\n\n"
                               "Results\n\nConfidence intervals were calculated for the primary estimate.")
        return old, new

    def assessment(self, old, new, identifier, status):
        finding = next(f for f in old.findings if f.id == identifier)
        old_ev = finding.evidence[0]
        current = next((f for f in new.findings if f.id == identifier), None)
        if current:
            new_ev = current.evidence[0]
        else:
            from manuscript_review.models import evidence
            new_ev = evidence(next(b for d in new.documents for b in d.blocks if b.kind != "heading"))
        return {"prior_issue_id": identifier, "status": status,
                "rationale": "The supplied descriptions support this reviewer interpretation.",
                "old_citations": [{"block_id": old_ev.block_id, "quote": old_ev.quote}],
                "new_citations": [{"block_id": new_ev.block_id, "quote": new_ev.quote}],
                "wording_softened_only": False,
                "remaining_action": "Verify the analysis boundaries in the executable code.", "confidence": "medium"}

    def test_each_prior_issue_has_both_version_slots(self):
        old, new = self.versions()
        comparison = compare_reviews(old, new)
        self.assertEqual(len(comparison["issue_assessments"]), len(old.findings))
        self.assertTrue(validate_comparison(comparison, old.to_dict(), new.to_dict()))
        self.assertTrue(all("old_evidence" in row and "new_evidence" in row for row in comparison["issue_assessments"]))

    def test_reporting_resolution_and_method_problem_are_distinct(self):
        old, new = self.versions()
        rows = {r["prior_issue_id"]: r for r in compare_reviews(old, new)["issue_assessments"]}
        self.assertEqual(rows["check.confidence_intervals"]["status"], "resolved")
        self.assertEqual(rows["check.confidence_intervals"]["resolution_scope"], "reporting_only")
        self.assertEqual(rows["pattern.feature_selection_before_split"]["status"], "unresolved")

    def test_softened_wording_does_not_resolve_persistent_leakage(self):
        old, new = self.versions()
        comparison = compare_reviews(old, new)
        row = self.assessment(old, new, "pattern.feature_selection_before_split", "resolved")
        row["wording_softened_only"] = True
        provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=response(
            {"assessments": [row], "limitations": []})))
        add_semantic_comparison(old, new, comparison, provider)
        found = next(r for r in comparison["issue_assessments"] if r["prior_issue_id"] == row["prior_issue_id"])
        self.assertEqual(found["status"], "unresolved")
        self.assertIn("conflicts_with_persistent_deterministic_evidence", found["quality_flags"])

    def test_missing_version_evidence_cannot_establish_resolution(self):
        old, new = self.versions()
        row = self.assessment(old, new, "pattern.causal_overclaim", "resolved")
        row["new_citations"] = []
        comparison = compare_reviews(old, new)
        provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=response(
            {"assessments": [row], "limitations": []})))
        add_semantic_comparison(old, new, comparison, provider)
        found = next(r for r in comparison["issue_assessments"] if r["prior_issue_id"] == row["prior_issue_id"])
        self.assertEqual(found["status"], "cannot_determine")

    def test_fabricated_comparison_citation_rejects_only_that_assessment(self):
        old, new = self.versions()
        bad = self.assessment(old, new, "pattern.causal_overclaim", "resolved")
        bad["new_citations"][0]["quote"] = "A fabricated intervention proved the mechanism."
        good = self.assessment(old, new, "pattern.feature_selection_before_split", "unresolved")
        comparison = compare_reviews(old, new)
        provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=response(
            {"assessments": [bad, good], "limitations": []})))
        add_semantic_comparison(old, new, comparison, provider)
        self.assertFalse(comparison["llm"].get("failed", False))
        self.assertTrue(comparison["llm"]["incomplete"])
        self.assertEqual(comparison["llm"]["coverage"]["assessed_by_llm"], 1)
        accepted = next(r for r in comparison["issue_assessments"]
                        if r["prior_issue_id"] == good["prior_issue_id"])
        rejected = next(r for r in comparison["issue_assessments"]
                        if r["prior_issue_id"] == bad["prior_issue_id"])
        self.assertEqual(accepted["origin"], "provider:openai")
        self.assertEqual(rejected["origin"], "deterministic")
        self.assertEqual(comparison["llm"]["item_rejections"][0]["status"], "source_rejected")

    def test_malformed_assessment_isolated_and_low_confidence_not_promoted(self):
        old, new = self.versions()
        malformed = self.assessment(old, new, "pattern.causal_overclaim", "resolved")
        malformed.pop("remaining_action")
        good = self.assessment(old, new, "pattern.feature_selection_before_split", "unresolved")
        good["confidence"] = "low"
        comparison = compare_reviews(old, new)
        provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=response(
            {"assessments": [malformed, good], "limitations": []})))
        add_semantic_comparison(old, new, comparison, provider)
        accepted = next(r for r in comparison["issue_assessments"]
                        if r["prior_issue_id"] == good["prior_issue_id"])
        self.assertEqual(accepted["confidence"], "low")
        self.assertEqual(comparison["llm"]["item_rejections"][0]["status"], "schema_rejected")

    def test_deterministic_wording_softening_is_not_applied_globally(self):
        old, new = self.versions()
        comparison = compare_reviews(old, new)
        leakage = next(r for r in comparison["issue_assessments"]
                       if r["prior_issue_id"] == "pattern.feature_selection_before_split")
        self.assertTrue(comparison["claims_weakened"])
        self.assertFalse(leakage["wording_softened_only"])

    def test_comparison_preserves_actual_provider_identity(self):
        old, new = self.versions()
        row = self.assessment(old, new, "pattern.feature_selection_before_split", "unresolved")
        class BedrockStub:
            name = "bedrock"
            dry_run = False
            def compare(self, packet):
                return {"assessments": [row], "limitations": []}
            def metadata(self):
                return {"provider": self.name, "calls": [], "usage": {}}
        comparison = compare_reviews(old, new)
        add_semantic_comparison(old, new, comparison, BedrockStub())
        accepted = next(r for r in comparison["issue_assessments"]
                        if r["prior_issue_id"] == row["prior_issue_id"])
        self.assertEqual(accepted["origin"], "provider:bedrock")

    def test_explicit_withdrawal_can_be_no_longer_applicable(self):
        old, _ = self.versions()
        new = self.review_text("Discussion\n\nWe no longer claim that our results establish a causal mechanism.")
        row = self.assessment(old, new, "pattern.causal_overclaim", "no_longer_applicable")
        comparison = compare_reviews(old, new)
        provider = OpenAIReviewer(OpenAISettings("test-model"), transport=Mock(return_value=response(
            {"assessments": [row], "limitations": []})))
        add_semantic_comparison(old, new, comparison, provider)
        found = next(r for r in comparison["issue_assessments"] if r["prior_issue_id"] == row["prior_issue_id"])
        self.assertEqual(found["status"], "no_longer_applicable")
        self.assertFalse(found["execution_verified"])

    def test_cross_version_provenance_tampering_is_rejected(self):
        old, new = self.versions()
        for field, value in (("section", "Invented"), ("line_start", 999), ("paragraph", 999)):
            comparison = compare_reviews(old, new)
            comparison["issue_assessments"][0]["old_evidence"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ReviewError, "specified manuscript version"):
                validate_comparison(comparison, old.to_dict(), new.to_dict())

    def test_comparison_hash_or_run_provenance_tampering_is_rejected(self):
        old, new = self.versions()
        for field, value in (("old_run_id", "forged-run"),
                             ("new_document_hashes", {"manuscript": "forged"})):
            comparison = compare_reviews(old, new)
            comparison[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ReviewError, "provenance"):
                validate_comparison(comparison, old.to_dict(), new.to_dict())

    def test_severity_increase_is_worsened(self):
        old, new = self.versions()
        next(f for f in new.findings if f.id == "pattern.feature_selection_before_split").severity = "fatal_flaw"
        row = next(r for r in compare_reviews(old, new)["issue_assessments"]
                   if r["prior_issue_id"] == "pattern.feature_selection_before_split")
        self.assertEqual(row["status"], "worsened")
