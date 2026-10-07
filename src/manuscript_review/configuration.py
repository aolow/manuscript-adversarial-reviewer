from __future__ import annotations

import json
from pathlib import Path
from .errors import ReviewError
from .models import SEVERITIES, ISSUE_STATUSES
from .prioritization import prioritize
from .rules.catalogue import CHECKS, PATTERNS

DEFAULT_CONFIG = {"disabled_rules": [], "include_domains": [], "exclude_domains": []}
DOMAINS = {"general", "quantitative", "testing", "predictive", "single_cell",
           "perturbation", "biomarker", "survival"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReviewError("Cannot read JSON %s: %s" % (path, exc)) from exc


def load_config(path=None):
    data = read_json(path) if path else {}
    if not isinstance(data, dict) or set(data) - set(DEFAULT_CONFIG):
        raise ReviewError("Configuration must contain only disabled_rules, include_domains, exclude_domains.")
    result = {**DEFAULT_CONFIG, **data}
    for key, value in result.items():
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ReviewError(key + " must be a list of strings.")
    known = {s.id for s in CHECKS + PATTERNS}
    if set(result["disabled_rules"]) - known:
        raise ReviewError("Unknown rule IDs: " + ", ".join(sorted(set(result["disabled_rules"]) - known)))
    for key in ("include_domains", "exclude_domains"):
        if set(result[key]) - DOMAINS:
            raise ReviewError("Unknown domains in " + key)
    if set(result["include_domains"]) & set(result["exclude_domains"]):
        raise ReviewError("A domain cannot be both included and excluded.")
    return result


def prepare_overrides(path, documents):
    if not path:
        return {}
    data = read_json(path)
    if not isinstance(data, dict) or set(data) - {"document_sha256", "sections", "findings"}:
        raise ReviewError("Overrides must contain document_sha256, sections, and/or findings.")
    hashes = {doc.id: doc.sha256 for doc in documents}
    if data.get("document_sha256") != hashes:
        raise ReviewError("Override hashes must match all supplied documents. Regenerate overrides for this version.")
    sections = data.get("sections", {})
    if not isinstance(sections, dict):
        raise ReviewError("Override sections must be a map from block ID to section name.")
    blocks = {block.id: block for doc in documents for block in doc.blocks}
    for key, section in sections.items():
        if key not in blocks or not isinstance(section, str) or not section.strip():
            raise ReviewError("Invalid section override: " + str(key))
        blocks[key].section = section
    return data


def apply_finding_overrides(findings, data):
    overrides = data.get("findings", [])
    if not isinstance(overrides, list):
        raise ReviewError("Override findings must be a list.")
    by_id = {f.id: f for f in findings}
    allowed = {
        "severity": SEVERITIES, "issue_status": ISSUE_STATUSES,
        "confidence": ("low", "medium", "high"),
        "disposition": ("active", "dismissed", "confirmed"),
        "effort": ("low", "medium", "high"), "value": ("low", "medium", "high"),
        "reviewer_likelihood": ("low", "medium", "high"),
    }
    seen = set()
    for override in overrides:
        if not isinstance(override, dict) or set(override) - set(allowed) - {"id", "note"}:
            raise ReviewError("Invalid finding override fields.")
        identifier = override.get("id")
        if identifier not in by_id or identifier in seen:
            raise ReviewError("Unknown or duplicate override finding ID: " + str(identifier))
        seen.add(identifier)
        if not isinstance(override.get("note"), str) or not override["note"].strip():
            raise ReviewError("Every finding override requires a nonempty note.")
        finding = by_id[identifier]
        for key, choices in allowed.items():
            if key in override:
                if override[key] not in choices:
                    raise ReviewError("Invalid override " + key + ": " + str(override[key]))
                setattr(finding, key, override[key])
        if "disposition" in override and finding.disposition != "duplicate":
            finding.duplicate_of = None
        finding.manual_note = override["note"]
        prioritize(finding)
