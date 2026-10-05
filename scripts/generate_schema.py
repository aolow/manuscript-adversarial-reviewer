"""Regenerate versioned JSON Schemas from dataclass contracts."""
from dataclasses import fields, is_dataclass
import json
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints

from manuscript_review import models

ROOT = Path(__file__).resolve().parents[1] / "src/manuscript_review"
definitions = {}


def schema_type(kind):
    origin, args = get_origin(kind), get_args(kind)
    if kind is Any:
        return {}
    if kind is type(None):
        return {"type": "null"}
    if kind in (str, int, bool, float):
        return {"type": {str: "string", int: "integer", bool: "boolean", float: "number"}[kind]}
    if origin is list:
        return {"type": "array", "items": schema_type(args[0])}
    if origin is dict:
        return {"type": "object", "additionalProperties": schema_type(args[1])}
    if origin is Union:
        return {"anyOf": [schema_type(arg) for arg in args]}
    if is_dataclass(kind):
        if kind.__name__ not in definitions:
            definitions[kind.__name__] = {}
            hints = get_type_hints(kind)
            definitions[kind.__name__] = {
                "type": "object", "additionalProperties": False,
                "required": [field.name for field in fields(kind)],
                "properties": {field.name: schema_type(hints[field.name]) for field in fields(kind)},
            }
        return {"$ref": "#/$defs/" + kind.__name__}
    raise TypeError(kind)


def generate():
    root = schema_type(models.Review)
    finding = definitions["Finding"]["properties"]
    for key, choices in (("severity", models.SEVERITIES), ("issue_status", models.ISSUE_STATUSES),
                         ("priority", models.PRIORITIES), ("disposition", ("active", "dismissed", "confirmed", "needs_review", "duplicate"))):
        finding[key] = {"type": "string", "enum": list(choices)}
    for name in ("Finding", "CheckResult"):
        definitions[name]["properties"]["confidence"] = {"enum": ["low", "medium", "high"]}
    definitions["Evidence"]["properties"]["relation"] = {
        "enum": ["trigger", "context_only", "candidate_support", "reported_result"]}
    for key in ("start", "end"):
        definitions["Evidence"]["properties"][key]["minimum"] = 0
    definitions["Finding"]["properties"]["evidence"]["minItems"] = 0
    finding["basis"] = {"enum": ["manuscript_direct", "manuscript_inference", "external_claim", "reviewer_opinion"]}
    finding["grounding_status"] = {"enum": ["source_verified", "needs_semantic_review", "ungrounded", "external_unverified"]}
    definitions["Review"]["properties"]["sections"].update(minItems=20, maxItems=20)
    definitions["Review"]["properties"]["schema_version"] = {"const": models.SCHEMA_VERSION}
    definitions["CheckResult"]["properties"]["status"] = {
        "enum": ["reported", "not_established", "explicit_negative_statement", "conflicting", "not_applicable"]}
    lists = ("substantive_changes", "claims_strengthened", "claims_weakened", "concerns_resolved",
             "reported_remediation", "concerns_unresolved", "new_concerns", "no_longer_detected")
    properties = {
        "schema_version": {"const": models.SCHEMA_VERSION},
        "old_run_id": {"type": "string"}, "new_run_id": {"type": "string"},
        "old_document_hashes": {"type": "object", "additionalProperties": {"type": "string"}},
        "new_document_hashes": {"type": "object", "additionalProperties": {"type": "string"}},
        **{key: {"type": "array", "items": {"type": "object"}} for key in lists},
        "rigor_assessment": {"type": "string"}, "positioning_assessment": {"type": "string"},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "issue_assessments": {"type": "array", "items": {"type": "object"}},
        "llm": {"type": "object"},
    }
    comparison = {"type": "object", "additionalProperties": False,
                  "required": list(properties), "properties": properties}
    definitions["Comparison"] = comparison
    definitions["Review"]["properties"]["comparison"] = {
        "anyOf": [{"$ref": "#/$defs/Comparison"}, {"type": "null"}]}
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
              "title": "Manuscript Review " + models.SCHEMA_VERSION, **root, "$defs": definitions}
    return schema, {"$schema": schema["$schema"], "title": "Manuscript Comparison " + models.SCHEMA_VERSION, **comparison}


if __name__ == "__main__":
    for name, schema in zip(("report.schema.json", "comparison.schema.json"), generate()):
        (ROOT / name).write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    from manuscript_review.providers.contracts import REVIEW_SCHEMA, COMPARISON_SCHEMA
    for name, schema in (("llm-response.schema.json", REVIEW_SCHEMA),
                         ("llm-comparison-response.schema.json", COMPARISON_SCHEMA)):
        (ROOT / name).write_text(json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema", **schema
        }, indent=2) + "\n", encoding="utf-8")
