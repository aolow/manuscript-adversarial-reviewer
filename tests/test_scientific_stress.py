"""Constructed responses probe guardrails, not live model scientific performance."""
from manuscript_review.grounding import normalize_response
from manuscript_review.pipeline import review_manuscript
from .helpers import WorkspaceTest, FIXTURES
from .llm_helpers import finding, envelope, source_block, action


class ScientificStressTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.report, _ = review_manuscript(FIXTURES / "pilot_complex_manuscript.md")

    def row(self, phrase, topic="leakage", interpretation=None, issue_key="other"):
        block = source_block(self.report.documents, phrase)
        row = finding(block)
        row.update(topic=topic, issue_key=issue_key,
                   support_rationale="The cited passage states: " + block["text"])
        row["action"]["held_out_unit"] = "Independent donors within discovery data, if linkage can be recovered"
        if interpretation:
            row["interpretation"] = interpretation
        return row

    def check(self, row):
        rows, _, _ = normalize_response("reviewer2", envelope([row]), self.report.documents,
                                        self.report.extraction, "test")
        return rows[0]

    def test_confident_unsupported_biological_interpretation_is_quarantined(self):
        row = self.row("The analysis is observational", "causality",
                       "The cell state definitely causes lineage conversion.")
        self.assertIn("unsupported_certainty", self.check(row).quality_flags)
        self.assertEqual(self.check(row).disposition, "needs_review")

    def test_plausible_invented_design_in_interpretation_is_quarantined(self):
        row = self.row("The analysis is observational", "causality",
                       "This randomized controlled trial demonstrates treatment specificity.")
        self.assertIn("invented_design_in_interpretation", self.check(row).quality_flags)

    def test_association_cannot_be_promoted_to_causation(self):
        row = self.row("The analysis is observational", "causality",
                       "The observations establish a causal mechanism of resistance.")
        self.assertIn("association_promoted_to_causation", self.check(row).quality_flags)

    def test_valid_causal_caution_is_not_reversed(self):
        row = self.row("The analysis is observational", "causality",
                       "An observational association cannot establish a causal mechanism.")
        self.assertEqual(self.check(row).disposition, "active")

    def test_indirect_leakage_description_can_anchor_a_review(self):
        row = self.row("All labeled specimens contributed", interpretation=
                       "Pooled ranking may expose evaluation information before partitioning.")
        self.assertEqual(self.check(row).disposition, "active")

    def test_feature_definition_leakage_is_not_limited_to_classifier_fitting(self):
        row = self.row("All labeled specimens contributed", interpretation=
                       "Coordinates built from pooled ranking may transmit outcome information even with a separately fitted classifier.",
                       issue_key="feature_selection_before_split")
        self.assertEqual(self.check(row).grounding_status, "source_verified")

    def test_train_test_donor_overlap_remains_a_supported_concern(self):
        row = self.row("All labeled specimens contributed", interpretation=
                       "Repeated specimens across the partition may undermine donor-independent evaluation.")
        self.assertEqual(self.check(row).disposition, "active")

    def test_pseudoreplication_is_anchored_to_actual_unit_statement(self):
        row = self.row("treated every cell", "pseudoreplication",
                       "Treating cells as independent replicates may understate donor-level uncertainty.",
                       "cell_pseudoreplication")
        row["category"] = "single_cell"
        self.assertEqual(self.check(row).disposition, "active")

    def test_specimen_count_is_not_a_subject_count(self):
        row = self.row("Discovery cohort A included", "pseudoreplication",
                       "The study contains 96 independent subjects.")
        self.assertIn("unsupported_biological_unit_count", self.check(row).quality_flags)

    def test_post_selection_interval_concern_is_preserved(self):
        row = self.row("Model settings were chosen", "statistics",
                       "The interval may omit uncertainty introduced by choosing the best observed configuration.")
        row["category"] = "statistics"
        self.assertEqual(self.check(row).disposition, "active")

    def test_reference_annotation_dependence_is_source_anchored(self):
        row = self.row("The reference atlas was annotated", "circularity",
                       "Agreement with assigned labels may reflect the annotation panel rather than independent biological validation.",
                       "circular_signature")
        row["category"] = "circularity"
        self.assertEqual(self.check(row).disposition, "active")

    def test_claim_exceeding_experiment_is_not_accepted_as_support(self):
        row = self.row("The analysis is observational", "causality",
                       "The design demonstrates a conserved causal pathway in every tissue.")
        self.assertIn("association_promoted_to_causation", self.check(row).quality_flags)

    def test_explicitly_missing_negative_control_can_motivate_new_experiment(self):
        row = self.row("No untreated negative-control", "other",
                       "An untreated condition would help distinguish treatment-specific effects.")
        row["action"].update(kind="experiment", input="Collect a new untreated negative-control condition")
        self.assertEqual(self.check(row).disposition, "active")

    def test_unreported_control_cannot_be_asserted_absent(self):
        row = self.row("The selected configuration achieved", "other",
                       "Negative controls were absent.")
        self.assertIn("unreported_control_treated_as_absent", self.check(row).quality_flags)

    def test_technical_rediscovery_is_not_called_independent_validation(self):
        row = self.row("The validation collection was named", "validation",
                       "Repeated aliquots may demonstrate technical consistency but not transportability to new patients.",
                       "cohort_reuse")
        self.assertEqual(self.check(row).disposition, "active")

    def test_novelty_hypothesis_stays_externally_unverified(self):
        row = self.row("We claim a new reference-mapping", "novelty",
                       "A similar mapping workflow may already exist.")
        row.update(basis="external_claim", category="positioning", citations=[])
        self.assertEqual(self.check(row).grounding_status, "external_unverified")

    def test_literature_assertion_cannot_masquerade_as_source_verification(self):
        row = self.row("We claim a new reference-mapping", "novelty",
                       "Prior studies established this reference-mapping workflow.")
        self.assertIn("external_verification_required", self.check(row).quality_flags)

    def test_impossible_reanalysis_is_quarantined(self):
        row = self.row("No untreated negative-control", "other",
                       "Protein data could distinguish RNA state from functional activity.")
        row["action"].update(input="Existing protein measurements for all baseline samples",
                             comparison="Compare protein activity and RNA-state associations")
        result = self.check(row)
        self.assertIn("action_requires_unavailable_data", result.quality_flags)
        self.assertEqual(result.disposition, "needs_review")

    def test_new_experiment_is_distinct_from_impossible_reanalysis(self):
        row = self.row("No untreated negative-control", "other",
                       "Protein data could distinguish RNA state from functional activity.")
        row["action"].update(kind="experiment", input="Collect new protein measurements",
                             comparison="Compare protein activity and RNA-state associations")
        self.assertNotIn("action_requires_unavailable_data", self.check(row).quality_flags)
