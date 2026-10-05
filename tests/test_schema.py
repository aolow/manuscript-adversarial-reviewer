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
