from manuscript_review.comparison import compare_reviews
from manuscript_review.pipeline import review_manuscript
from .helpers import WorkspaceTest, FIXTURES


class ComparisonTests(WorkspaceTest):
    def test_different_tool_versions_are_explicitly_flagged(self):
        old = self.review_text("Methods\n\nWe used 12 patients.")
        new = self.review_text("Methods\n\nWe used 12 patients.")
        old.tool_version = "0.3.0"
        comparison = compare_reviews(old, new)
        self.assertTrue(any("different tool versions" in value
                            for value in comparison["limitations"]))

    def test_identical_manuscripts_have_no_changes(self):
        old, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        new, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        result = compare_reviews(old, new)
        for key in ("substantive_changes", "new_concerns", "concerns_resolved",
                    "reported_remediation", "no_longer_detected"):
            self.assertEqual(result[key], [])

    def test_revised_fixture_distinguishes_reporting_from_rigor(self):
        old, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        new, _ = review_manuscript(FIXTURES / "revised_manuscript.md")
        result = compare_reviews(old, new)
        self.assertIn("check.confidence_intervals", {r["id"] for r in result["concerns_resolved"]})
        self.assertIn("pattern.cell_pseudoreplication", {r["id"] for r in result["reported_remediation"]})
        self.assertTrue(result["claims_weakened"])
        self.assertTrue(result["concerns_unresolved"])
        self.assertIn("not established", result["rigor_assessment"])
        self.assertTrue(all(r["scientific_resolution"] == "not_verified" for r in result["concerns_resolved"]))

    def test_deleted_claim_does_not_prove_resolution(self):
        old = self.review_text("Abstract\n\nOur results prove a causal mechanism.")
        new = self.review_text("Abstract\n\nWe summarize the observations.")
        result = compare_reviews(old, new)
        self.assertIn("pattern.causal_overclaim", {r["id"] for r in result["no_longer_detected"]})
        self.assertEqual(result["concerns_resolved"], [])

    def test_negated_remediation_is_not_a_fix(self):
        old = self.review_text("Methods\n\nSingle-cell data were analyzed. Cells were treated as independent biological replicates.")
        new = self.review_text("Methods\n\nSingle-cell data were analyzed. Pseudobulk was not performed.")
        result = compare_reviews(old, new)
        self.assertNotIn("pattern.cell_pseudoreplication", {r["id"] for r in result["reported_remediation"]})

    def test_stronger_claim_and_new_concern(self):
        old = self.review_text("Abstract\n\nOur results suggest an association with resistance.")
        new = self.review_text("Abstract\n\nOur results prove a causal mechanism of resistance.")
        result = compare_reviews(old, new)
        self.assertTrue(result["claims_strengthened"])
        self.assertIn("pattern.causal_overclaim", {r["id"] for r in result["new_concerns"]})
