"""Dependency-free schema and provenance validation for generated reports."""
from __future__ import annotations

from .errors import ReviewError
from .models import SCHEMA_VERSION, SEVERITIES, ISSUE_STATUSES, PRIORITIES


def validate_report(data):
    required = {"schema_version", "tool_version", "run_id", "created_at", "target_journal",
                "documents", "extraction", "findings", "checklist", "reviewer_runs",
                "sections", "warnings", "configuration", "comparison", "claim_analyses",
                "adversarial", "quality", "llm"}
    if not isinstance(data, dict) or set(data) != required or data["schema_version"] != SCHEMA_VERSION:
        raise ReviewError("Invalid report top-level schema.")
    blocks = {b["id"]: b for d in data["documents"] for b in d["blocks"]}
    if len(blocks) != sum(len(d["blocks"]) for d in data["documents"]):
        raise ReviewError("Source block IDs must be unique.")
    findings = data["findings"]
    ids = {f["id"] for f in findings}
    if len(ids) != len(findings):
        raise ReviewError("Finding IDs must be unique.")
    for finding in findings:
        if finding["severity"] not in SEVERITIES or finding["issue_status"] not in ISSUE_STATUSES:
            raise ReviewError("Invalid finding classification.")
        if finding["priority"] not in PRIORITIES or finding["confidence"] not in ("low", "medium", "high"):
            raise ReviewError("Invalid finding priority or confidence.")
        if not finding["evidence"] and not (finding["origin"].startswith("provider:")
                and finding["grounding_status"] in ("ungrounded", "external_unverified")
                and finding["confidence"] == "low" and finding["disposition"] in ("needs_review", "dismissed")):
            raise ReviewError("Findings require source context.")
        if finding["duplicate_of"] is not None and finding["duplicate_of"] not in ids:
            raise ReviewError("Duplicate finding refers to an unknown canonical finding.")
    if len(data["sections"]) != 20:
        raise ReviewError("A report must contain all 20 sections.")

    def inspect(value):
        if isinstance(value, dict):
            if {"quote", "block_id", "start", "end", "document_id"} <= set(value):
                block = blocks.get(value["block_id"])
                start, end = value["start"], value["end"]
                if (block is None or type(start) is not int or type(end) is not int or
                        not 0 <= start < end <= len(block["text"]) or
                        block["document_id"] != value["document_id"] or
                        block["section"] != value["section"] or block["page"] != value["page"] or
                        block["paragraph"] != value["paragraph"] or
                        value["line_start"] != (block["line_start"] + block["text"][:start].count("\n")
                                                if block["line_start"] is not None else None) or
                        block["text"][start:end] != value["quote"]):
                    raise ReviewError("Evidence does not match its source block.")
            if "finding_ids" in value and not set(value["finding_ids"]) <= ids:
                raise ReviewError("Report refers to an unknown finding.")
            for key, child in value.items():
                if key != "comparison":  # comparison contains sources from two independent reviews
                    inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    inspect(data)
    return True


def validate_comparison(comparison, old, new):
    from .providers.contracts import RESOLUTION_STATUSES
    registries = {side: {b["id"]: b for d in data["documents"] for b in d["blocks"]}
                  for side, data in (("old", old), ("new", new))}
    old_ids = {f["id"] for f in old["findings"] if f["disposition"] in ("active", "confirmed")}
    rows = comparison.get("issue_assessments", [])
    if {r["prior_issue_id"] for r in rows} != old_ids or len(rows) != len(old_ids):
        raise ReviewError("Comparison must assess each prior active issue exactly once.")
    for row in rows:
        if row["status"] not in RESOLUTION_STATUSES or row["execution_verified"] is not False:
            raise ReviewError("Invalid comparison classification or unsupported execution claim.")
        for side in ("old", "new"):
            for ev in row[side + "_evidence"]:
                block = registries[side].get(ev["block_id"])
                if (block is None or block["text"][ev["start"]:ev["end"]] != ev["quote"]
                        or block["section"] != ev["section"] or block["page"] != ev["page"]
                        or block["document_id"] != ev["document_id"]):
                    raise ReviewError("Comparison evidence does not match the specified manuscript version.")
    return True
