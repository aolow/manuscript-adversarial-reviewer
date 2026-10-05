from manuscript_review.configuration import load_config
from manuscript_review.pipeline import review_manuscript
from .helpers import WorkspaceTest, FIXTURES


class RuleTests(WorkspaceTest):
    def test_all_deliberately_planted_patterns_are_detected(self):
        report, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        ids = {f.rule_id for f in report.findings}
        expected = {"feature_selection_before_split", "test_set_tuning", "cohort_reuse",
                    "cell_pseudoreplication", "circular_signature", "causal_overclaim",
                    "conservation_overclaim", "novelty_overclaim", "confidence_intervals",
                    "external_validation", "multiple_testing"}
        self.assertTrue(expected <= ids, expected - ids)
        self.assertTrue(all(f.severity != "fatal_flaw" for f in report.findings))

    def test_explicit_negation_does_not_trigger_design_flaw(self):
        report = self.review_text("Methods\n\nWe did not select genes before splitting the predictive dataset.\n"
                                 "Cells were not treated as independent biological replicates in single-cell analysis.")
        self.assertFalse(any(f.id.startswith("pattern.") for f in report.findings))

    def test_prespecified_features_are_not_automatically_leakage(self):
        report = self.review_text("Methods\n\nWe selected prespecified genes from prior literature before splitting the predictive dataset.")
        self.assertNotIn("pattern.feature_selection_before_split", {f.id for f in report.findings})

    def test_unknown_selection_provenance_is_only_plausible(self):
        report = self.review_text("Methods\n\nWe selected genes before splitting the predictive dataset.")
        finding = next(f for f in report.findings if f.id == "pattern.feature_selection_before_split")
        self.assertEqual(finding.issue_status, "plausible_issue")

    def test_prior_work_does_not_trigger_novelty_or_causality(self):
        report = self.review_text("Introduction\n\nPrior work described the first-ever model.\n"
                                 "Previous studies demonstrate causal mechanisms.")
        self.assertFalse(any(f.id.startswith("pattern.") for f in report.findings))

    def test_reporting_negation_future_and_reference_matrix(self):
        cases = [
            ("Methods\n\nOur predictor used external validation.", "reported"),
            ("Methods\n\nOur predictor had no external validation.", "explicit_negative_statement"),
            ("Methods\n\nWe will conduct external validation of our predictor.", "not_established"),
            ("Methods\n\nExternal validation of the predictor requires further study.", "not_established"),
            ("Methods\n\nOur predictor was evaluated.\n\nReferences\n\nExternal validation.", "not_established"),
            ("Methods\n\nOur predictor was evaluated on a held-out cohort.", "not_established"),
        ]
        for text, status in cases:
            with self.subTest(text=text):
                self.assertEqual(self.check(text, "external_validation").status, status)

    def test_independent_markers_are_not_an_external_cohort(self):
        text = "Methods\n\nIndependent marker genes were used to validate the predictive signature."
        self.assertEqual(self.check(text, "external_validation").status, "not_established")

    def test_explicitly_missing_intervals_are_not_reported_intervals(self):
        for phrase in ("Confidence intervals were omitted.", "The result has missing confidence intervals."):
            with self.subTest(phrase=phrase):
                self.assertEqual(self.check("Results\n\nWe analyzed 12 patients. " + phrase,
                                            "confidence_intervals").status, "explicit_negative_statement")

    def test_condition_platform_alignment_requires_different_platforms(self):
        template = "Methods\n\nWe studied 12 patients. All responders were measured on platform A and all nonresponders on platform {}."
        bad = self.review_text(template.format("B"))
        control = self.review_text(template.format("A"))
        self.assertIn("pattern.design_confounding", {f.id for f in bad.findings})
        self.assertNotIn("pattern.design_confounding", {f.id for f in control.findings})

    def test_acknowledged_confounding_remains_a_scientific_concern(self):
        report = self.review_text("Limitations\n\nPlatform and response remain confounded in the patient cohort.")
        self.assertIn("pattern.design_confounding", {f.id for f in report.findings})

    def test_conflicting_reporting_is_visible(self):
        check = self.check("Methods\n\nOur predictor used external validation.\n\n"
                           "Discussion\n\nNo external validation was performed.", "external_validation")
        self.assertEqual(check.status, "conflicting")
        self.assertEqual(len(check.evidence), 2)

    def test_independent_clauses_do_not_share_negation(self):
        check = self.check("Methods\n\nNo external validation was performed; confidence intervals "
                           "were computed for 12 patients.", "confidence_intervals")
        self.assertEqual(check.status, "reported")

    def test_negative_outcomes_are_not_missing_methods(self):
        self.assertEqual(self.check("Methods\n\nIn our single-cell analysis, no doublets were detected.", "doublets").status, "reported")
        self.assertEqual(self.check("Methods\n\nIn our biomarker cohort, no missing values were observed.", "missingness").status, "reported")

    def test_limitations_can_acknowledge_absent_evidence(self):
        self.assertEqual(self.check("Discussion\n\nThis study cannot establish causality.", "limitations").status, "reported")

    def test_single_cell_rules_not_applied_to_non_single_cell_paper(self):
        report = self.review_text("Methods\n\nWe interviewed 12 patients about treatment preferences.")
        self.assertTrue(all(c.status == "not_applicable" for c in report.checklist if c.domain == "single_cell"))

    def test_domain_override_can_disable_survival(self):
        config = load_config(self.write('{"exclude_domains": ["survival"]}', "config.json"))
        report = self.review_text("Methods\n\nWe modeled survival in 12 patients.", config=config)
        self.assertEqual(next(c for c in report.checklist if c.id == "censoring").status, "not_applicable")

    def test_supplement_reporting_carries_supplement_provenance(self):
        main = self.write("Methods\n\nWe developed a predictor in 12 patients.")
        supplement = self.write("Supplementary Methods\n\nExternal validation was performed in an independent cohort.", "supplement.md")
        report, _ = review_manuscript(main, supplements=[supplement])
        check = next(c for c in report.checklist if c.id == "external_validation")
        self.assertEqual(check.status, "reported")
        self.assertEqual(check.evidence[0].document_id, "supplement-1")

    def test_absence_uses_cautious_status_and_context(self):
        report = self.review_text("Methods\n\nWe developed a predictor in 12 patients.")
        finding = next(f for f in report.findings if f.id == "check.external_validation")
        self.assertEqual(finding.issue_status, "plausible_issue")
        self.assertIn("not established", finding.issue)
        self.assertEqual(finding.evidence[0].relation, "context_only")
        self.assertEqual(finding.confidence, "low")

    def test_revised_future_clinical_methods_do_not_count_as_completed(self):
        report, _ = review_manuscript(FIXTURES / "revised_manuscript.md")
        checks = {c.id: c for c in report.checklist}
        for key in ("calibration", "clinical_utility", "subgroups"):
            self.assertEqual(checks[key].status, "not_established")

    def test_finding_ids_stable_across_run_and_filename(self):
        text = "Methods\n\nWe selected genes using all samples before splitting the predictor data."
        first = self.review_text(text)
        second, _ = review_manuscript(self.write(text, "renamed.txt"))
        self.assertEqual([f.id for f in first.findings], [f.id for f in second.findings])
        self.assertNotEqual(first.run_id, second.run_id)
