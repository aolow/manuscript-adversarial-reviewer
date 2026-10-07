"""Strict LLM response contracts, also validated locally before interpretation."""
from ..errors import ReviewError
from ..rules.catalogue import CHECKS, PATTERNS


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else list(required),
            "additionalProperties": False}


def array(items, maximum=30):
    return {"type": "array", "items": items, "maxItems": maximum}


TEXT = {"type": "string", "minLength": 1, "maxLength": 4000}
NULLABLE = {"anyOf": [TEXT, {"type": "null"}]}
SLUG = {"type": "string", "pattern": "^[a-z][a-z0-9_-]{0,79}$"}
CONFIDENCE = {"type": "string", "enum": ["low", "medium", "high"]}
BASIS = {"type": "string", "enum": [
    "manuscript_direct", "manuscript_inference", "external_claim", "reviewer_opinion"]}
TOPICS = ["leakage", "pseudoreplication", "circularity", "causality", "conservation",
          "novelty", "validation", "confounding", "statistics", "calibration",
          "reproducibility", "clinical", "writing", "other"]
CITATION = obj({"block_id": TEXT, "quote": {"type": "string", "minLength": 12, "maxLength": 1200}})
ACTION = obj({
    "kind": {"type": "string", "enum": ["analysis", "experiment", "text", "reporting", "none"]},
    "input": NULLABLE, "comparison": NULLABLE, "held_out_unit": NULLABLE,
    "metric": NULLABLE, "expected_interpretation": NULLABLE,
    "text_section": NULLABLE, "text_claim": NULLABLE, "recommended_framing": NULLABLE,
}, required=["kind"])
FINDING = obj({
    "id": SLUG, "topic": {"type": "string", "enum": TOPICS},
    "issue_key": {"type": "string", "enum": sorted({rule.id for rule in CHECKS + PATTERNS}) + ["other"]},
    "severity": {"type": "string", "enum": ["major", "moderate", "minor", "optional_strengthening"]},
    "category": {"type": "string", "enum": ["design", "statistics", "leakage", "confounding", "circularity",
                          "validation", "interpretation", "positioning", "clinical",
                          "single_cell", "perturbation", "reproducibility", "reporting", "writing", "other"]},
    "issue_status": {"type": "string", "enum": ["plausible_issue", "speculative_concern"]},
    "basis": BASIS, "evidence_statement": TEXT, "interpretation": TEXT,
    "support_rationale": TEXT, "why_it_matters": TEXT,
    "suggested_fix": TEXT, "suggested_analysis": TEXT,
    "confidence": CONFIDENCE, "citations": array(CITATION, 8),
    "claim_ids": array(TEXT, 10), "action": ACTION,
})
CLAIM = obj({
    "id": SLUG, "claim_text": TEXT,
    "importance": {"type": "string", "enum": ["central", "supporting", "exploratory"]},
    "importance_rationale": TEXT, "rank": {"type": "integer", "minimum": 1, "maximum": 20},
    "manuscript_evidence": array(CITATION, 8), "supporting_evidence": array(CITATION, 8),
    "strongest_support": TEXT, "strongest_weakness": TEXT, "alternative_explanation": TEXT,
    "falsification_analysis": ACTION, "decisive_analysis": ACTION,
    "impact_if_false": TEXT, "confidence_in_claim": CONFIDENCE,
})
STRENGTH = obj({"text": TEXT, "citations": array(CITATION, 8)})
REVIEW_SCHEMA = obj({
    "findings": array(FINDING, 10), "claims": array(CLAIM, 6),
    "strengths": array(STRENGTH, 8), "limitations": array(TEXT, 12),
})
# Provider payloads are accepted at the container level first. Individual
# findings/claims/strengths are validated independently during grounding so one
# malformed element cannot discard unrelated output from the same reviewer call.
REVIEW_ENVELOPE_SCHEMA = obj({
    "findings": {"type": "array", "maxItems": 10},
    "claims": {"type": "array", "maxItems": 6},
    "strengths": {"type": "array", "maxItems": 8},
    "limitations": {"type": "array", "maxItems": 12},
})
RESOLUTION_STATUSES = ["resolved", "partially_resolved", "unresolved", "worsened",
                       "no_longer_applicable", "cannot_determine"]
ASSESSMENT = obj({
    "prior_issue_id": TEXT, "status": {"type": "string", "enum": RESOLUTION_STATUSES},
    "rationale": TEXT, "old_citations": array(CITATION, 8),
    "new_citations": array(CITATION, 8), "wording_softened_only": {"type": "boolean"},
    "remaining_action": TEXT, "confidence": CONFIDENCE,
})
COMPARISON_SCHEMA = obj({"assessments": array(ASSESSMENT, 200), "limitations": array(TEXT, 12)})
COMPARISON_ENVELOPE_SCHEMA = obj({
    "assessments": {"type": "array", "maxItems": 200},
    "limitations": {"type": "array", "maxItems": 12},
})


def validate_payload(payload, schema):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ReviewError('LLM validation needs the optional dependency: pip install ".[llm]"') from exc
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda e: str(e.path))
    if errors:
        # Do not echo model output or manuscript text in errors/logs.
        error = errors[0]
        path = ".".join(str(p) for p in error.path) or "root"
        exc = ReviewError("LLM output violates JSON Schema at %s (%s)." % (path, error.validator))
        exc.schema_path = path
        exc.schema_validator = str(error.validator)
        raise exc
    return payload
