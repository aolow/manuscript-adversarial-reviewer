"""Small, explicitly synthetic regression benchmark; no provider calls."""
from pathlib import Path
import json
import re

from .errors import ReviewError
from .grounding import action_flags
from .models import review_from_dict
from .pipeline import review_manuscript
from .validation import validate_report


def evaluate(manifest_path, reports_dir=None, layer="deterministic"):
    manifest_path = Path(manifest_path).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReviewError("Cannot read benchmark manifest.") from exc
    if not isinstance(manifest, dict) or manifest.get("synthetic_only") is not True:
        raise ReviewError("Benchmark manifests must explicitly declare synthetic_only=true.")
    if (not isinstance(manifest.get("evaluated_rule_ids"), list) or
            any(not isinstance(key, str) for key in manifest["evaluated_rule_ids"]) or
            not isinstance(manifest.get("cases"), list) or not isinstance(manifest.get("version"), str)):
        raise ReviewError("Invalid benchmark manifest structure.")
    if layer not in ("deterministic", "llm", "combined"):
        raise ReviewError("Unknown benchmark layer.")
    if layer != "deterministic" and not reports_dir:
        raise ReviewError("LLM/combined scoring requires --reports from an explicitly authorized prior run; benchmark never calls a provider.")
    universe = set(manifest["evaluated_rule_ids"])
    cases, totals = [], dict(tp=0, fp=0, fn=0, evaluated_findings=0, unscored_findings=0,
                            provenance_valid=0, provenance_total=0, evidence_aligned=0,
                            evidence_total=0, severity_correct=0, severity_total=0,
                            actionable=0, action_total=0)
    for case in manifest["cases"]:
        if (not isinstance(case, dict) or not isinstance(case.get("id"), str)
                or not re.fullmatch(r"[a-z][a-z0-9_-]*", case["id"])
                or not isinstance(case.get("file"), str) or not isinstance(case.get("expected"), list)):
            raise ReviewError("Invalid benchmark case.")
        for annotation in case["expected"]:
            if (not isinstance(annotation, dict) or annotation.get("rule_id") not in universe or
                    not isinstance(annotation.get("evidence_phrases"), list) or
                    not isinstance(annotation.get("acceptable_severities"), list)):
                raise ReviewError("Benchmark annotation is invalid or outside evaluated_rule_ids.")
        path = (manifest_path.parent / case["file"]).resolve()
        if manifest_path.parent not in path.parents:
            raise ReviewError("Benchmark fixture paths must remain within the manifest directory.")
        report, _ = review_manuscript(path)
        expected_hashes = {d.id: d.sha256 for d in report.documents}
        data = report.to_dict()
        if reports_dir:
            try:
                data = review_from_dict(json.loads(
                    (Path(reports_dir) / case["id"] / "report.json").read_text())).to_dict()
            except (OSError, ValueError) as exc:
                raise ReviewError("Missing or invalid saved report for benchmark case " + case["id"]) from exc
            if {d["id"]: d["sha256"] for d in data["documents"]} != expected_hashes:
                raise ReviewError("Saved benchmark report source hash mismatch: " + case["id"])
            fresh_blocks = {b.id: (b.document_id, b.text, b.page, b.line_start, b.line_end, b.paragraph)
                            for d in report.documents for b in d.blocks}
            saved_blocks = {b["id"]: (b["document_id"], b["text"], b["page"], b["line_start"],
                                      b["line_end"], b["paragraph"])
                            for d in data["documents"] for b in d["blocks"]}
            if fresh_blocks != saved_blocks:
                raise ReviewError("Saved benchmark source blocks differ from current extraction: " + case["id"])
        validate_report(data)
        findings = [f for f in data["findings"] if f["disposition"] in ("active", "confirmed")
                    and (layer == "combined" or
                         (layer == "llm") == f["origin"].startswith("provider:"))]
        expected = {row["rule_id"]: row for row in case["expected"]}
        observed = {f["rule_id"] for f in findings} & universe
        tp, fp, fn = observed & set(expected), observed - set(expected), set(expected) - observed
        totals["tp"] += len(tp)
        totals["fp"] += len(fp)
        totals["fn"] += len(fn)
        totals["evaluated_findings"] += len(observed)
        totals["unscored_findings"] += sum(f["rule_id"] not in universe for f in findings)
        totals["provenance_total"] += len(findings)
        totals["provenance_valid"] += sum(bool(f["evidence"]) and all(e["quote"] for e in f["evidence"]) for f in findings)
        for rule_id in tp:
            finding = next(f for f in findings if f["rule_id"] == rule_id)
            annotation = expected[rule_id]
            text = " ".join(e["quote"] for e in finding["evidence"]).lower()
            totals["evidence_total"] += 1
            totals["evidence_aligned"] += any(phrase.lower() in text for phrase in annotation["evidence_phrases"])
            totals["severity_total"] += 1
            totals["severity_correct"] += finding["severity"] in annotation["acceptable_severities"]
            totals["action_total"] += 1
            totals["actionable"] += not action_flags(finding["action"], finding["severity"])
        cases.append({"id": case["id"], "true_positives": sorted(tp), "false_positives": sorted(fp),
                      "false_negatives": sorted(fn), "unscored_findings": sum(f["rule_id"] not in universe for f in findings)})
    ratio = lambda a, b: a / b if b else None
    return {
        "benchmark_version": manifest["version"],
        "mode": "saved_reports" if reports_dir else "deterministic",
        "layer": layer,
        "case_count": len(cases), "counts": totals,
        "scores": {
            "precision_in_annotated_scope": ratio(totals["tp"], totals["tp"] + totals["fp"]),
            "recall_in_annotated_scope": ratio(totals["tp"], totals["tp"] + totals["fn"]),
            "exact_source_grounding": ratio(totals["provenance_valid"], totals["provenance_total"]),
            "expected_evidence_alignment": ratio(totals["evidence_aligned"], totals["evidence_total"]),
            "severity_calibration": ratio(totals["severity_correct"], totals["severity_total"]),
            "structured_action_completeness": ratio(totals["actionable"], totals["action_total"]),
        },
        "cases": cases, "evaluated_rule_ids": sorted(universe),
        "limitations": [
            "Tiny author-designed synthetic regression set; annotations are expert-style, not independently expert-validated.",
            "Precision/recall and false positives are measured only inside the declared rule scope; unscored findings are counted separately.",
            "Exact source matching is not semantic entailment; expected-phrase alignment is a limited synthetic grounding check.",
            "Actionability measures populated analysis/text fields, not feasibility or scientific value.",
            "No expert-level performance, real-manuscript generalization, or live LLM quality is established.",
            "Saved LLM findings map through their declared issue_key; independently review those labels before interpreting model scores.",
        ],
    }
