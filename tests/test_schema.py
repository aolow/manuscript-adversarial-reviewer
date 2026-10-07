import importlib.util
import json
import unittest

from manuscript_review.comparison import compare_reviews
from manuscript_review.pipeline import review_manuscript
from .helpers import FIXTURES, ROOT


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "Install .[test] for JSON Schema validation.")
class SchemaTests(unittest.TestCase):
    def test_api_contracts_are_strict_typed_objects_and_match_exports(self):
        from manuscript_review.providers.contracts import REVIEW_SCHEMA, COMPARISON_SCHEMA
        def inspect(value):
            if isinstance(value, dict):
                if "enum" in value:
                    self.assertEqual(value.get("type"), "string")
                if value.get("type") == "object":
                    self.assertIs(value.get("additionalProperties"), False)
                    self.assertLessEqual(set(value["required"]), set(value["properties"]))
                    if set(value["properties"]) == {
                            "kind", "input", "comparison", "held_out_unit", "metric",
                            "expected_interpretation", "text_section", "text_claim",
                            "recommended_framing"}:
                        self.assertEqual(value["required"], ["kind"])
                    else:
                        self.assertEqual(set(value["required"]), set(value["properties"]))
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        for name, contract in (("llm-response.schema.json", REVIEW_SCHEMA),
                               ("llm-comparison-response.schema.json", COMPARISON_SCHEMA)):
            inspect(contract)
            shipped = json.loads((ROOT / "src/manuscript_review" / name).read_text())
            shipped.pop("$schema")
            self.assertEqual(shipped, contract)

    def test_provider_envelope_is_strict_at_top_level_but_defers_child_validation(self):
        from manuscript_review.providers.contracts import (
            REVIEW_SCHEMA, REVIEW_ENVELOPE_SCHEMA, validate_payload)
        from .llm_helpers import envelope
        payload = envelope([{"id": "INVALID ID"}])
        self.assertIs(validate_payload(payload, REVIEW_ENVELOPE_SCHEMA), payload)
        with self.assertRaises(Exception):
            validate_payload(payload, REVIEW_SCHEMA)
        malformed_container = {"findings": [], "claims": [], "strengths": []}
        with self.assertRaises(Exception):
            validate_payload(malformed_container, REVIEW_ENVELOPE_SCHEMA)

    def test_review_contract_is_bounded_for_live_generation(self):
        from manuscript_review.providers.contracts import REVIEW_SCHEMA
        self.assertEqual(REVIEW_SCHEMA["properties"]["findings"]["maxItems"], 10)
        self.assertEqual(REVIEW_SCHEMA["properties"]["claims"]["maxItems"], 6)
        finding = REVIEW_SCHEMA["properties"]["findings"]["items"]
        self.assertIn("other", finding["properties"]["category"]["enum"])
        self.assertEqual(finding["properties"]["action"]["required"], ["kind"])

    def test_reports_and_comparison_validate_against_shipped_schema(self):
        import jsonschema
        schema_root = ROOT / "src/manuscript_review"
        report_schema = json.loads((schema_root / "report.schema.json").read_text())
        comparison_schema = json.loads((schema_root / "comparison.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(report_schema)
        jsonschema.Draft202012Validator.check_schema(comparison_schema)
        old, _ = review_manuscript(FIXTURES / "flawed_manuscript.md")
        new, _ = review_manuscript(FIXTURES / "revised_manuscript.md")
        new.comparison = compare_reviews(old, new)
        for review in (old, new):
            jsonschema.validate(review.to_dict(), report_schema)
        jsonschema.validate(new.comparison, comparison_schema)
        for name in ("flawed-report.json", "revised-report.json"):
            jsonschema.validate(json.loads((ROOT / "examples" / name).read_text()), report_schema)
        jsonschema.validate(json.loads((ROOT / "examples/comparison.json").read_text()), comparison_schema)

    def test_mocked_llm_report_and_response_contracts_validate(self):
        import jsonschema
        from manuscript_review.providers.openai import OpenAIReviewer, OpenAISettings
        from .llm_helpers import envelope, finding, packet_block, response
        def transport(body, timeout):
            row = finding(packet_block(body, "We selected"))
            return response(envelope([row]))
        provider = OpenAIReviewer(OpenAISettings("test-model"), roles=["scientific"], transport=transport)
        report, _ = review_manuscript(FIXTURES / "flawed_manuscript.md", provider=provider)
        path = ROOT / "src/manuscript_review"
        jsonschema.validate(report.to_dict(), json.loads((path / "report.schema.json").read_text()))
        for name in ("llm-response.schema.json", "llm-comparison-response.schema.json"):
            jsonschema.Draft202012Validator.check_schema(json.loads((path / name).read_text()))
