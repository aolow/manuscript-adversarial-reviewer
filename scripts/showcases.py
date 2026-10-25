"""Reproduce public-paper showcases; download inputs only with --download.

No provider is configured. Full manuscripts and reports stay in ignored reviews/.
The checked-in baseline is a projection of an actual offline CLI report, not a
scientific verdict. Model-native annotations are checked for exact text only.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ("single-cell-foundation-models", "virtual-biotech")
MAX_BYTES = 5 * 1024 * 1024


def digest(data):
    return sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_jats(raw):
    """Extract text in source order, keeping paragraph IDs for evidence checks.

    Include abstract, body, back matter and floated figure captions. Exclude
    references and the duplicated Associated Data wrapper. No figures, external
    supplements, layout, or equation interpretation is performed.
    """
    if b"<!ENTITY" in raw:
        raise ValueError("XML entity declarations are unsupported")
    root = ET.fromstring(raw)
    records = []

    def text(node):
        return " ".join("".join(node.itertext()).split())

    def add(node, kind, depth):
        value = text(node)
        if value:
            records.append({"source_id": node.get("id") or "node-%03d" % (len(records) + 1),
                            "kind": kind, "depth": min(depth, 6), "text": value})

    def visit(node, depth=2):
        if node.tag in ("ref-list", "graphic", "media", "table-wrap-foot"):
            # Media may contain the supplement's descriptive caption, not its content.
            if node.tag == "media":
                for caption in node.findall("caption"):
                    visit(caption, depth)
            return
        if node.tag == "sec" and node.findtext("title") in ("References", "Associated Data"):
            return
        if node.tag == "title":
            add(node, "heading", depth)
        elif node.tag in ("p", "table", "disp-formula"):
            add(node, "paragraph", depth)
        elif node.tag == "fig":
            label = node.find("label")
            if label is not None:
                add(label, "heading", depth)
            for caption in node.findall("caption"):
                visit(caption, depth + 1)
        else:
            for child in node:
                visit(child, depth + (node.tag == "sec" and child.tag == "sec"))

    title = root.find("./front/article-meta/title-group/article-title")
    if title is None:
        raise ValueError("JATS article title is missing")
    add(title, "heading", 1)
    for part in root.findall("./front/article-meta/abstract"):
        if part.find("title") is None:
            records.append({"source_id": "abstract-heading", "kind": "heading",
                            "depth": 2, "text": "Abstract"})
        visit(part)
    for name in ("body", "back", "floats-group"):
        part = root.find(name)
        if part is not None:
            visit(part)
    if len(records) < 2:
        raise ValueError("No article content")
    ids = [r["source_id"] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate source IDs")
    markdown = "\n\n".join(("#" * r["depth"] + " " if r["kind"] == "heading" else "")
                             + r["text"] for r in records) + "\n"
    return markdown.encode("utf-8"), records


def source_bytes(manifest, cache, download=False):
    """Verify bytes before parsing. Never silently accept a changed web source."""
    path = cache / "source.xml"
    if path.exists():
        if path.stat().st_size > MAX_BYTES:
            raise ValueError("Cached source exceeds size limit")
        raw = path.read_bytes()
    elif download:
        request = urllib.request.Request(manifest["xml_url"], headers={"User-Agent": "MAR-public-showcase/1"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read(MAX_BYTES + 1)
    else:
        raise ValueError("Source not cached; use --download to fetch the pinned public article")
    if len(raw) > MAX_BYTES or digest(raw) != manifest["xml_sha256"]:
        raise ValueError("Source hash mismatch; keep the pinned version and investigate upstream drift")
    if not path.exists():
        cache.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return raw


def project_baseline(report):
    """Publish all engine leads, without redistributing the full manuscript."""
    return {
        "mode": "offline_deterministic", "provider_calls": 0,
        "tool_version": report["tool_version"], "schema_version": report["schema_version"],
        "manuscript_sha256": report["documents"][0]["sha256"],
        "source_block_count": len(report["documents"][0]["blocks"]),
        "findings": [{k: f[k] for k in ("id", "rule_id", "severity", "issue_status", "issue",
                                       "origin", "disposition", "grounding_status")}
                     for f in report["findings"]],
        "checklist": [{"id": c["id"], "status": c["status"]} for c in report["checklist"]],
        "reviewer_modes": [{"role": r["role"], "mode": r["mode"]} for r in report["reviewer_runs"]],
        "warnings": report["warnings"],
    }


def verify_review(review, records, report):
    """Validate provenance and quote spans, not scientific reasoning or truth."""
    if (review["origin"] != "model_native" or review["independent_human_validation"] is not False
            or review["provider_panel_run"] is not False):
        raise ValueError("Showcase must disclose model-native, non-independent provenance")
    source = {r["source_id"]: r for r in records}
    blocks = {b["id"]: b for b in report["documents"][0]["blocks"]}
    engine_ids = {f["id"] for f in report["findings"]}
    anchors = review["anchors"]
    used = set()
    item_ids = set()
    for item in review["items"]:
        if item["id"] in item_ids:
            raise ValueError("Duplicate review item ID")
        item_ids.add(item["id"])
        if item["decision"] not in ("retain", "narrow", "verify", "dismiss", "strength"):
            raise ValueError("Invalid review decision")
        if not item["evidence"]:
            raise ValueError("Review item has no evidence")
        for key in item["evidence"] + item["counterevidence"]:
            if key not in anchors:
                raise ValueError("Review item references missing anchor")
            used.add(key)
        if not set(item["engine_finding_ids"]).issubset(engine_ids):
            raise ValueError("Review item references unknown engine finding")
    triaged = []
    for group in review["baseline_triage"]:
        triaged.extend(group["finding_ids"])
        if not group["reason"] or not set(group["review_item_ids"]).issubset(item_ids):
            raise ValueError("Invalid baseline triage cross-reference")
    if len(triaged) != len(set(triaged)) or set(triaged) != engine_ids:
        raise ValueError("Every baseline finding must be triaged exactly once")
    if used != set(anchors):
        raise ValueError("Unreferenced anchors")
    for key, anchor in anchors.items():
        record = source.get(anchor["source_id"])
        block = blocks.get(anchor["block_id"])
        start, end, quote = anchor["start"], anchor["end"], anchor["quote"]
        if (not record or not block or not quote or type(start) is not int or type(end) is not int
                or not 0 <= start < end <= len(block["text"])
                or record["text"] != block["text"] or block["text"][start:end] != quote):
            raise ValueError("Evidence mismatch: " + key)
    return {"review_items": len(item_ids), "exact_anchors": len(anchors),
            "baseline_findings_triaged": len(triaged), "scientific_validity_verified": False}


def render_review(review, manifest):
    """Keep the readable showcase synchronized with the structured audit."""
    lines = ["# " + review["title"], "",
             "> Model-native scientific review with a separately executed offline CLI baseline. "
             "No provider panel was run. Not independently human-validated.", "",
             "Source: [" + manifest["title"] + "](" + manifest["article_url"] + "). "
             + ", ".join(manifest["authors"]) + ". " + manifest["version"] + ".", "",
             review["summary"], "", "## Coverage", "", review["coverage"], "",
             "All decisions below are model-native interpretations, including the decisions to "
             "dismiss a concern. Exact source-span checks do not verify those interpretations. "
             "Engine dispositions remain unchanged in [baseline.json](baseline.json).", ""]
    groups = [("Revision priorities", ("retain", "narrow")),
              ("Verify before escalating", ("verify",)),
              ("Strengths worth preserving", ("strength",)),
              ("Concerns that did not survive checking", ("dismiss",))]
    for title, decisions in groups:
        lines.extend(["## " + title, ""])
        for item in review["items"]:
            if item["decision"] not in decisions:
                continue
            lines.extend(["### " + item["id"] + " — " + item["title"], "",
                          "**Decision: " + item["decision"] + ".** " + item["assessment"], "",
                          "**Evidence:** " + ", ".join("[" + a + "](#" + a.lower() + ")" for a in item["evidence"]) + ".", "",
                          "**Counterevidence / scope:** " + item["challenge"] + " "
                          + " ".join("[" + a + "](#" + a.lower() + ")" for a in item["counterevidence"]), "",
                          "**Next step:** " + item["next_step"], "",
                          "**What would change this decision:** " + item["decision_change"], "",
                          "**Origin:** model-native. **Related engine leads:** "
                          + (", ".join("`" + i + "`" for i in item["engine_finding_ids"]) or "none; not an engine-generated finding") + ".", ""])
    lines.extend(["## Complete disposition of the offline leads", "",
                  "This is an annotated demonstration, not a measured false-positive rate. "
                  "The following groups cover every engine lead exactly once; these are "
                  "recommendations, not overrides of the original report.", ""])
    for group in review["baseline_triage"]:
        lines.extend(["- **" + group["decision"] + ":** " + group["reason"] + " Related review: "
                      + ", ".join(group["review_item_ids"]) + ". Leads: "
                      + ", ".join("`" + i + "`" for i in group["finding_ids"]) + ".", ""])
    lines.extend(["## Evidence ledger", "",
                  "Short excerpts are attributed to the article above. Source IDs refer to the "
                  "pinned JATS snapshot; `node-*` IDs are assigned by the converter. "
                  "[review.json](review.json) retains MAR block IDs and exact character offsets. "
                  "Reproduction downloads the full context locally for inspection.", ""])
    for key, anchor in review["anchors"].items():
        lines.extend(["### " + key, "", "Source `" + anchor["source_id"] + "`: “" + anchor["quote"] + "”", ""])
    return "\n".join(lines).rstrip() + "\n"


def reproduce(slug, download=False):
    public = ROOT / "showcases" / slug
    manifest = read_json(public / "source.json")
    cache = ROOT / "reviews" / "showcases" / "sources" / slug
    raw = source_bytes(manifest, cache, download)
    markdown, records = normalize_jats(raw)
    if digest(markdown) != manifest["normalized_sha256"]:
        raise ValueError("Normalized source drift; converter or pinned input changed")
    # A new directory on every run preserves earlier receipts and raw reports.
    runs = ROOT / "reviews" / "showcases" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=slug + "-", dir=runs))
    manuscript = run / "manuscript.md"
    manuscript.write_bytes(markdown)
    write_json(run / "source-index.json", records)
    command = [sys.executable, "-m", "manuscript_review", "review", str(manuscript),
               "--out", str(run / "review")]
    subprocess.run(command, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    report = read_json(run / "review" / "report.json")
    baseline = project_baseline(report)
    write_json(run / "baseline.json", baseline)
    if baseline != read_json(public / "baseline.json"):
        raise ValueError("Offline baseline changed; inspect " + str(run / "baseline.json"))
    review = read_json(public / "review.json")
    result = verify_review(review, records, report)
    if (public / "review.md").read_text(encoding="utf-8") != render_review(review, manifest):
        raise ValueError("Readable review is out of sync with review.json")
    result.update({"paper": slug, "source_sha256": digest(raw), "baseline_matches": True,
                   "engine_run_id": report["run_id"], "engine_created_at": report["created_at"],
                   "provider_calls": 0, "command": command})
    write_json(run / "verification.json", result)
    print(json.dumps({**result, "output": str(run)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", choices=("all",) + PAPERS)
    parser.add_argument("--download", action="store_true", help="Fetch pinned public XML if not already cached")
    args = parser.parse_args()
    try:
        for paper in PAPERS if args.paper == "all" else (args.paper,):
            reproduce(paper, args.download)
    except (ValueError, OSError, ET.ParseError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        parser.exit(1, "Showcase verification failed: " + detail + "\n")


if __name__ == "__main__":
    main()
