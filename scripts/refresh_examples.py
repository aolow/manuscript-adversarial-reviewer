"""Rebuild synthetic examples through the public pipeline; no network access."""
import json
from pathlib import Path

from manuscript_review.pipeline import review_manuscript
from manuscript_review.comparison import compare_reviews
from manuscript_review.reporting import render_markdown, render_comparison
from manuscript_review import __version__

ROOT = Path(__file__).resolve().parents[1]


def main():
    old, _ = review_manuscript(ROOT / "fixtures/flawed_manuscript.md")
    new, _ = review_manuscript(ROOT / "fixtures/revised_manuscript.md")
    for label, review in (("flawed", old), ("revised", new)):
        # Fixed metadata makes synthetic examples reproducible, not a real run receipt.
        review.run_id = "example-" + label + "-v" + __version__
        review.created_at = "2026-10-04T00:00:00+00:00"
        for document in review.documents:
            document.path = "fixtures/" + document.name
    new.comparison = compare_reviews(old, new)
    examples = ROOT / "examples"
    examples.mkdir(exist_ok=True)
    for name, data in (("flawed-report.json", old.to_dict()), ("revised-report.json", new.to_dict()),
                       ("comparison.json", new.comparison)):
        (examples / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "EXAMPLE_REPORT.md").write_text(
        "> Synthetic fixture output. No real scientific results. Example metadata is fixed for reproducibility.\n\n"
        + render_markdown(old), encoding="utf-8")
    (examples / "comparison.md").write_text(render_comparison(new.comparison), encoding="utf-8")
    print(json.dumps({
        "flawed_findings": len(old.findings), "revised_findings": len(new.findings),
        "reporting_cues_added": len(new.comparison["concerns_resolved"]),
        "candidate_design_remediations": len(new.comparison["reported_remediation"]),
        "still_detected": len(new.comparison["concerns_unresolved"]),
        "no_longer_detected": len(new.comparison["no_longer_detected"]),
        "new_concerns": len(new.comparison["new_concerns"]),
        "claims_weakened": len(new.comparison["claims_weakened"]),
    }, indent=2))


if __name__ == "__main__":
    main()
