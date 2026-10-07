"""Local pilot diagnostics. No telemetry, pricing lookup, or additional API calls."""
from collections import Counter


def safe_usage(usage):
    if not isinstance(usage, dict):
        return {}
    result = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        if type(usage.get(key)) is int and usage[key] >= 0:
            result[key] = usage[key]
    for key, child in (("input_tokens_details", "cached_tokens"),
                       ("output_tokens_details", "reasoning_tokens")):
        value = usage.get(key)
        if isinstance(value, dict) and type(value.get(child)) is int and value[child] >= 0:
            result[key] = {child: value[child]}
    return result


def usage_totals(receipts, attempted):
    result = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        values = [r["usage"][key] for r in receipts if key in r.get("usage", {})]
        result[key] = sum(values) if values else None
        result[key + "_coverage"] = {"calls_with_value": len(values), "attempted_calls": attempted}
    for parent, key in (("input_tokens_details", "cached_tokens"),
                        ("output_tokens_details", "reasoning_tokens")):
        values = [r["usage"][parent][key] for r in receipts if key in r.get("usage", {}).get(parent, {})]
        result[key] = sum(values) if values else None
    result["note"] = "Known usage only; missing receipts are not zero. Cached input and reasoning output are subsets, not extra totals."
    return result


def attach_diagnostics(review):
    """Counts distinguish returned, locally accepted, quarantined and duplicate records."""
    rows = [f for f in review.findings if f.origin.startswith("provider:")]
    counts = Counter(f.disposition for f in rows)
    runs = review.reviewer_runs
    calls = review.llm.get("calls", [])
    raw = [r.get("raw_findings") for r in calls]
    manual = [r for r in runs if r["mode"] == "manual_import"]
    known = [n for n in raw if type(n) is int]
    known += [r["raw_findings"] for r in manual]
    failed = [r["role"] for r in runs if r["mode"] == "failed"]
    comparison = (review.comparison or {}).get("llm", {})
    if comparison.get("failed") or comparison.get("incomplete"):
        failed.append("comparison")
    headline = set(review.adversarial.get("what_could_kill_this_paper", {}).get("finding_ids", []))
    failures = [c for c in calls if c.get("status") != "schema_accepted"]
    schema_roles = {c["role"] for c in calls if c.get("status") == "schema_accepted"}
    item_rejections = [item for run in runs for item in run.get("item_rejections", [])]
    item_normalizations = [item for run in runs for item in run.get("item_normalizations", [])]
    rejection_counts = Counter(item.get("kind", "unknown") for item in item_rejections)
    call_roles = {c["role"] for c in calls}
    failures += [{"role": r["role"], "status": "source_validation_rejected", "reason": r["note"]}
                 for r in runs if r["mode"] == "failed" and r["role"] in schema_roles]
    failures += [{"role": r["role"], "status": "request_preparation_rejected", "reason": r["note"]}
                 for r in runs if r["mode"] == "failed" and r["role"] not in call_roles]
    if comparison.get("failed") and "comparison" in schema_roles:
        failures.append({"role": "comparison", "status": "source_validation_rejected",
                         "reason": comparison.get("error", "Comparison validation failed.")})
    elif comparison.get("incomplete"):
        failures.append({
            "role": "comparison", "status": "item_rejections",
            "reason": "Some prior issues were not accepted from the semantic comparison; deterministic assessments were retained.",
        })
    diagnostics = {
        "model": review.llm.get("settings", {}).get("model"),
        "reasoning_effort": review.llm.get("settings", {}).get("reasoning_effort"),
        "dry_run": review.llm.get("dry_run", False),
        "prepared_requests": review.llm.get("request_count", 0),
        "attempted_api_calls": review.llm.get("attempted_calls", 0),
        "schema_accepted_calls": review.llm.get("completed_calls", 0),
        "failures": failures,
        "incomplete_roles": sorted(set(failed)),
        "not_run_roles": [r["role"] for r in runs if r["mode"] in ("dry_run", "not_applicable")],
        "usage": review.llm.get("usage", {}),
        "estimated_cost_usd": None,
        "cost_status": "Unavailable: token counts alone do not supply a verified price or billed currency. Failed calls may incur charges.",
        "raw_findings_known": sum(known),
        "raw_count_complete": all(n is not None for n in raw),
        "accepted_findings": counts["active"] + counts["confirmed"],
        "quarantined_findings": counts["needs_review"],
        "merged_duplicates": counts["duplicate"],
        "dismissed_findings": counts["dismissed"],
        "rejected_findings_known": max(
            max(0, sum(known) - len(rows)), rejection_counts["finding"]),
        "rejected_claims_known": rejection_counts["claim"],
        "rejected_strengths_known": rejection_counts["strength"],
        "item_rejections": item_rejections,
        "item_normalizations": item_normalizations,
        "deterministic_findings": sum(f.origin == "deterministic" for f in review.findings),
        "headline_findings": len(headline),
        "provider_headline_findings": sum(f.id in headline for f in rows),
        "manual_import_batches": len(manual),
        "api_call_scope": ("API calls belong to the original provider review; manual import makes zero API calls."
                           if manual else "Calls attempted in this review operation."),
        "comparison_coverage": comparison.get("coverage"),
        "comparison_item_rejections": comparison.get("item_rejections", []),
        "note": "Accepted means eligible for display after local checks; scientific correctness is not verified.",
    }
    review.quality["pilot_diagnostics"] = diagnostics
    return diagnostics
