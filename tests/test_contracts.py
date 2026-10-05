from copy import deepcopy
from dataclasses import asdict
import json

from manuscript_review.configuration import load_config
from manuscript_review.errors import ReviewError
from manuscript_review.pipeline import review_manuscript
from manuscript_review.reporting import render_markdown
from manuscript_review.validation import validate_report
from .helpers import WorkspaceTest, FIXTURES


class ContractTests(WorkspaceTest):
    def test_report_has_twenty_sections_and_valid_exact_citations(self):
        report, packets = review_manuscript(FIXTURES / "flawed_manuscript.md")
        data = json.loads(json.dumps(report.to_dict()))
        self.assertTrue(validate_report(data))
        self.assertEqual(len(report.sections), 20)
        self.assertEqual(len(packets), 8)
        self.assertTrue(all("untrusted" in p["instructions"] for p in packets.values()))
        markdown = render_markdown(report)
        self.assertIn("## 20. Confidence/uncertainty notes", markdown)
        self.assertIn("Source: manuscript; Methods; line", markdown)

    def test_tampered_quote_rejected(self):
        report, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        data = report.to_dict()
        data["findings"][0]["evidence"][0]["quote"] = "invented result"
        with self.assertRaisesRegex(ReviewError, "Evidence"):
            validate_report(data)

    def test_duplicate_ids_rejected(self):
        report, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        data = report.to_dict()
        data["findings"].append(deepcopy(data["findings"][0]))
        with self.assertRaisesRegex(ReviewError, "unique"):
            validate_report(data)

    def test_claim_reference_link_is_never_verified_support(self):
        report, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        links = report.extraction["claim_evidence_map"]
        self.assertTrue(any(r["support_status"] == "candidate_reference_link" for r in links))
        self.assertTrue(any(r["support_status"] == "not_established_from_manuscript" for r in links))
        self.assertTrue(all(r["support_status"] != "verified" for r in links))

    def test_manual_override_retained_and_hash_bound(self):
        path = self.write("Methods\n\nWe developed a predictor in 12 patients.")
        original, _ = review_manuscript(path)
        override = {"document_sha256": {"manuscript": original.documents[0].sha256},
                    "findings": [{"id": "check.external_validation", "disposition": "dismissed",
                                  "note": "Exploratory study; no generalization claim."}]}
        override_path = self.write(json.dumps(override), "overrides.json")
        changed, _ = review_manuscript(path, overrides_path=override_path)
        finding = next(f for f in changed.findings if f.id == "check.external_validation")
        self.assertEqual(finding.disposition, "dismissed")
        self.assertIn("Exploratory", finding.manual_note)
        path.write_text("Changed manuscript.", encoding="utf-8")
        with self.assertRaisesRegex(ReviewError, "hashes"):
            review_manuscript(path, overrides_path=override_path)

    def test_manual_section_override(self):
        path = self.write("Unrecognized source text.")
        original, _ = review_manuscript(path)
        override = {"document_sha256": {"manuscript": original.documents[0].sha256},
                    "sections": {original.documents[0].blocks[0].id: "Methods"}}
        changed, _ = review_manuscript(path, overrides_path=self.write(json.dumps(override), "overrides.json"))
        self.assertEqual(changed.documents[0].blocks[0].section, "Methods")
        self.assertEqual(len(changed.extraction["methods"]), 1)

    def test_invalid_config_cannot_silently_disable_checks(self):
        for data in ({"disable_rules": []}, {"disabled_rules": ["does_not_exist"]},
                     {"include_domains": ["mystery"]}, {"disabled_rules": "external_validation"}):
            with self.subTest(data=data), self.assertRaises(ReviewError):
                load_config(self.write(json.dumps(data), "config.json"))

    def test_provider_findings_require_real_offsets(self):
        class BadProvider:
            name = "fake"
            def review(self, role, packet):
                return [{"id": "test", "severity": "major", "category": "design",
                         "issue_status": "plausible_issue", "issue": "Question", "why_it_matters": "Reason",
                         "suggested_fix": "Fix", "suggested_analysis": "Analysis", "confidence": "low",
                         "citations": [{"block_id": "invented", "start": 0, "end": 12}]}]
        with self.assertRaisesRegex(ReviewError, "outside supplied"):
            self.review_text("Methods\n\nWe used 12 patients.", provider=BadProvider())

    def test_valid_injected_provider_is_labeled(self):
        class StubProvider:
            name = "test-stub"
            def review(self, role, packet):
                if role != "scientific":
                    return []
                block = next(b for b in packet["source_blocks"] if b["kind"] != "heading")
                return [{"id": "scope", "severity": "optional_strengthening", "category": "design",
                         "issue_status": "speculative_concern", "issue": "Check scope.", "why_it_matters": "Scope matters.",
                         "suggested_fix": "Clarify scope.", "suggested_analysis": "Review applicability.", "confidence": "low",
                         "citations": [{"block_id": block["id"], "start": 0, "end": len(block["text"])}]}]
        report = self.review_text("Methods\n\nWe used 12 patients.", provider=StubProvider())
        finding = next(f for f in report.findings if f.id == "reviewer.scientific.scope")
        self.assertEqual(finding.origin, "provider:test-stub")
        self.assertEqual(finding.priority, "P3_optional_strengthening")
        self.assertNotIn("No LLM review was performed", " ".join(report.warnings))
