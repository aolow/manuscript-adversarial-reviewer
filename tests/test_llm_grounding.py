from copy import deepcopy
from dataclasses import asdict

from manuscript_review.errors import ReviewError
from manuscript_review.grounding import normalize_response, reconcile
from manuscript_review.pipeline import review_manuscript
from manuscript_review.validation import validate_report
from .helpers import WorkspaceTest
from .llm_helpers import PAPER, finding, envelope, source_block, claim


class GroundingTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.report = self.review_text(PAPER)
        self.block = source_block(self.report.documents)

    def normalize(self, payload, role="scientific"):
        return normalize_response(role, payload, self.report.documents, self.report.extraction, "test")

    def test_exact_quote_is_resolved_to_local_location(self):
        items, _, _ = self.normalize(envelope([finding(self.block)]))
        ev = items[0].evidence[0]
        self.assertEqual(ev.section, "Methods")
        self.assertEqual(ev.quote, self.block["text"])
        self.assertEqual(ev.line_start, self.block["line_start"])
        self.assertEqual(items[0].grounding_status, "source_verified")
        self.assertIn("semantic_entailment_not_verified", items[0].quality_flags)
        self.assertEqual(items[0].confidence, "medium")

    def test_finding_with_only_fabricated_quote_is_dropped_not_role_aborted(self):
        bad = finding(self.block, "bad-citation")
        bad["citations"][0]["quote"] = "We performed a randomized trial in 900 patients."
        good = finding(self.block, "good-citation")
        items, _, _ = self.normalize(envelope([bad, good]))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].evidence[0].quote, self.block["text"])

    def test_finding_with_nonexistent_block_is_dropped_not_role_aborted(self):
        bad = finding(self.block, "bad-block")
        bad["citations"][0]["block_id"] = "invented-block"
        good = finding(self.block, "good-block")
        items, _, _ = self.normalize(envelope([bad, good]))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].evidence[0].block_id, self.block["id"])

    def test_invalid_citation_is_filtered_when_another_citation_is_valid(self):
        row = finding(self.block)
        row["citations"].append({
            "block_id": self.block["id"],
            "quote": "A fabricated quote that is not in the cited block.",
        })
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items[0].evidence), 1)
        self.assertIn("invalid_citations_dropped", items[0].quality_flags)

    def test_model_cannot_supply_page_or_section(self):
        for field, value in (("page", 999), ("section", "Imaginary Methods"), ("start", 19)):
            row = finding(self.block)
            row["citations"][0][field] = value
            rejections = []
            items, _, _ = normalize_response(
                "scientific", envelope([row]), self.report.documents, self.report.extraction,
                "test", rejections=rejections)
            with self.subTest(field=field):
                self.assertEqual(items, [])
                self.assertEqual(rejections[0]["kind"], "finding")
                self.assertEqual(rejections[0]["status"], "schema_rejected")

    def test_wrong_topic_chunk_is_quarantined(self):
        code = source_block(self.report.documents, "Code is available")
        row = finding(code)
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(items[0].disposition, "needs_review")
        self.assertEqual(items[0].confidence, "low")
        self.assertIn("source_topic_mismatch", items[0].quality_flags)

    def test_fabricated_numeric_premise_flagged(self):
        row = finding(self.block)
        row["evidence_statement"] = "We selected genes in 1000 patients."
        items, _, _ = self.normalize(envelope([row]))
        self.assertIn("unsupported_numeric_premise", items[0].quality_flags)
        self.assertEqual(items[0].disposition, "needs_review")

    def test_ungrounded_criticism_is_retained_without_fake_citation(self):
        row = finding(self.block)
        row["citations"] = []
        row["evidence_statement"] = "An independent cohort is not established from the manuscript."
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(items[0].grounding_status, "ungrounded")
        self.assertEqual(items[0].evidence, [])
        self.assertEqual(items[0].confidence, "low")

    def test_external_hypothesis_is_not_manuscript_fact(self):
        row = finding(self.block)
        row.update(basis="external_claim", topic="novelty", issue_key="novelty_overclaim",
                   category="positioning", citations=[])
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(items[0].grounding_status, "external_unverified")
        self.assertIn("external_verification_required", items[0].quality_flags)

    def test_cross_chunk_synthesis_requires_multiple_chunks(self):
        row = finding(self.block)
        row["basis"] = "manuscript_inference"
        items, _, _ = self.normalize(envelope([row]))
        self.assertIn("synthesis_needs_multiple_source_chunks", items[0].quality_flags)

    def test_multi_chunk_inference_is_distinct_from_direct_evidence(self):
        row = finding(self.block)
        result = source_block(self.report.documents, "achieved an AUROC")
        row["basis"] = "manuscript_inference"
        row["citations"].append({"block_id": result["id"], "quote": result["text"]})
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(items[0].basis, "manuscript_inference")
        self.assertEqual(items[0].grounding_status, "source_verified")

    def test_unsupported_certainty_quarantined(self):
        row = finding(self.block)
        row["interpretation"] = "The manuscript is definitely invalid."
        items, _, _ = self.normalize(envelope([row]))
        self.assertIn("unsupported_certainty", items[0].quality_flags)
        self.assertEqual(items[0].confidence, "low")

    def test_negated_or_protected_design_cannot_support_opposite_critique(self):
        self.report = self.review_text("Methods\n\nFeature selection was performed only within each training fold.")
        block = source_block(self.report.documents, "Feature selection")
        items, _, _ = self.normalize(envelope([finding(block)]))
        self.assertIn("source_describes_protection_not_flaw", items[0].quality_flags)
        self.assertEqual(items[0].disposition, "needs_review")

    def test_fatal_or_established_provider_judgments_rejected(self):
        for field, value in (("severity", "fatal_flaw"), ("issue_status", "established_issue")):
            row = finding(self.block)
            row[field] = value
            rejections = []
            items, _, _ = normalize_response(
                "scientific", envelope([row]), self.report.documents, self.report.extraction,
                "test", rejections=rejections)
            with self.subTest(field=field):
                self.assertEqual(items, [])
                self.assertEqual(rejections[0]["status"], "schema_rejected")

    def test_incomplete_analysis_action_flagged(self):
        row = finding(self.block)
        row["action"]["held_out_unit"] = None
        items, _, _ = self.normalize(envelope([row]))
        self.assertIn("incomplete_action", items[0].quality_flags)
        self.assertEqual(items[0].disposition, "needs_review")

    def test_schema_rejects_only_malformed_item_and_keeps_sibling(self):
        for mutate in (lambda r: r.update(invented="x"), lambda r: r.pop("why_it_matters"),
                       lambda r: r.update(confidence=0.99)):
            bad = finding(self.block, "bad")
            mutate(bad)
            good = finding(self.block, "good")
            rejections = []
            items, _, _ = normalize_response(
                "scientific", envelope([bad, good]), self.report.documents, self.report.extraction,
                "test", rejections=rejections)
            with self.subTest(mutate=mutate):
                self.assertEqual(len(items), 1)
                self.assertEqual(len(rejections), 1)
                self.assertEqual(rejections[0]["kind"], "finding")
                self.assertEqual(rejections[0]["status"], "schema_rejected")

    def test_cosmetic_model_id_is_normalized_not_rejected(self):
        row = finding(self.block)
        row["id"] = "Finding 4 INVALID"
        normalizations = []
        items, _, _ = normalize_response(
            "scientific", envelope([row]), self.report.documents, self.report.extraction,
            "test", normalizations=normalizations)
        self.assertEqual(len(items), 1)
        self.assertEqual(normalizations, [{"kind": "finding", "index": 0, "field": "id"}])

    def test_provider_finding_id_does_not_depend_on_model_slug(self):
        first = finding(self.block, "first-model-id")
        second = finding(self.block, "different-model-id")
        a, _, _ = self.normalize(envelope([first]))
        b, _, _ = self.normalize(envelope([second]))
        self.assertEqual(a[0].id, b[0].id)

    def test_harmless_whitespace_and_unicode_quote_drift_is_resolved(self):
        self.report = self.review_text("Methods\n\nWe used 12 patients — across two cohorts.")
        block = source_block(self.report.documents, "We used")
        row = finding(block)
        row["citations"][0]["quote"] = "We used 12 patients - across  two cohorts."
        row["evidence_statement"] = block["text"]
        items, _, _ = self.normalize(envelope([row]))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].evidence[0].quote, block["text"])
        self.assertIn("normalized_citation_match", items[0].quality_flags)

    def test_duplicate_and_conflicting_ratings_preserved(self):
        first, _, _ = self.normalize(envelope([finding(self.block)]), role="methods")
        row = finding(self.block)
        row["severity"] = "moderate"
        second, _, _ = self.normalize(envelope([row]), role="computational")
        merged = first + second
        events = reconcile(merged)
        self.assertEqual(len(events), 1)
        self.assertEqual(merged[1].disposition, "duplicate")
        self.assertEqual(merged[1].duplicate_of, merged[0].id)
        self.assertEqual(merged[0].severity, "moderate")
        self.assertEqual(len(merged[0].reviewer_assessments), 2)
        self.assertIn("severity_disagreement", merged[0].quality_flags)

    def test_different_evidence_not_silently_merged(self):
        first, _, _ = self.normalize(envelope([finding(self.block)]), role="methods")
        other = deepcopy(first[0])
        other.id = "reviewer.computational.other"
        other.evidence = []
        self.assertEqual(reconcile(first + [other]), [])

    def test_central_claim_and_support_are_source_anchored(self):
        abstract = source_block(self.report.documents, "Our model predicts")
        result = source_block(self.report.documents, "achieved an AUROC")
        _, claims, _ = self.normalize(envelope(claims=[claim(abstract, result)]))
        self.assertEqual(claims[0]["importance"], "central")
        self.assertEqual(claims[0]["manuscript_evidence"][0]["section"], "Abstract")
        self.assertEqual(claims[0]["supporting_evidence"][0]["section"], "Results")

    def test_paraphrased_central_claim_is_retained_for_semantic_review(self):
        row = claim(source_block(self.report.documents, "Our model predicts"),
                    source_block(self.report.documents, "achieved an AUROC"))
        row["claim_text"] = "A transcriptional signature may generalize as a predictive biomarker."
        _, claims, _ = self.normalize(envelope(claims=[row]))
        self.assertEqual(len(claims), 1)
        self.assertIn("claim_paraphrase_needs_semantic_review", claims[0]["quality_flags"])
        self.assertEqual(claims[0]["confidence_in_claim"], "low")

    def test_bad_claim_citation_does_not_discard_independent_findings(self):
        row = claim(source_block(self.report.documents, "Our model predicts"),
                    source_block(self.report.documents, "achieved an AUROC"))
        row["manuscript_evidence"][0]["quote"] = "A fabricated central claim excerpt that is not in the manuscript."
        item = finding(self.block)
        item["claim_ids"] = [row["id"]]
        findings, claims, _ = self.normalize(envelope([item], claims=[row]))
        self.assertEqual(claims, [])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].claim_ids, [])
        self.assertEqual(findings[0].origin, "provider:test")

    def test_unknown_claim_link_is_dropped_without_aborting_finding(self):
        row = finding(self.block)
        row["claim_ids"] = ["unprovided-claim"]
        findings, _, _ = self.normalize(envelope([row]))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].claim_ids, [])
        self.assertIn("dangling_claim_ref_dropped", findings[0].quality_flags)

    def test_runtime_validation_catches_tampered_locations(self):
        for field, value in (("page", 99), ("section", "Fake"), ("paragraph", 999), ("line_start", 1234)):
            data = self.report.to_dict()
            data["findings"][0]["evidence"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ReviewError, "Evidence"):
                validate_report(data)

    def test_text_edit_cannot_invent_target_section(self):
        row = finding(self.block)
        row["action"].update(kind="text", text_section="Invented section", text_claim=self.block["text"],
                             recommended_framing="Narrow the prediction claim to the studied population.")
        items, _, _ = self.normalize(envelope([row]))
        self.assertIn("text_edit_section_not_found", items[0].quality_flags)
        self.assertEqual(items[0].disposition, "needs_review")

    def test_fabricated_strength_is_not_promoted(self):
        strength = {"text": "A randomized trial in 900 patients established robustness.",
                    "citations": [{"block_id": self.block["id"], "quote": self.block["text"]}]}
        _, _, strengths = self.normalize(envelope(strengths=[strength]))
        self.assertEqual(strengths[0]["grounding_status"], "needs_semantic_review")


    def test_bad_strength_citation_does_not_discard_role_outputs(self):
        bad = {"text": "The study design is a clear strength.",
               "citations": [{"block_id": self.block["id"],
                              "quote": "A fabricated strength excerpt not in the manuscript."}]}
        good = {"text": "The methods are described in the manuscript.",
                "citations": [{"block_id": self.block["id"], "quote": self.block["text"]}]}
        findings, _, strengths = self.normalize(
            envelope([finding(self.block)], strengths=[bad, good]))
        self.assertEqual(len(findings), 1)
        self.assertEqual(len(strengths), 1)
        self.assertEqual(strengths[0]["text"], good["text"])
