"""Provenance, source-drift and publication-boundary checks for public showcases."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("showcases", ROOT / "scripts/showcases.py")
showcases = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(showcases)

JATS = b"""<article><front><article-meta><title-group><article-title>Test paper</article-title>
</title-group><abstract><p id="A">An abstract.</p></abstract></article-meta></front>
<body><sec><title>Methods</title><p id="P1">Measured <italic>cells</italic> carefully.</p>
<sec><title>Controls</title><p id="P2">A control.</p></sec></sec>
<sec><title>Associated Data</title><p>Duplicate content.</p></sec></body>
<back><sec><title>Data availability</title><p id="P3">Code is available.</p></sec>
<ref-list><ref><p>Not manuscript evidence.</p></ref></ref-list></back>
<floats-group><fig><label>Figure 1</label><caption><p id="P4">Caption retained.</p></caption>
<graphic href="never-download.png"/></fig></floats-group></article>"""


def review_fixture():
    records = [{"source_id": "P1", "text": "Measured cells carefully."}]
    report = {"documents": [{"blocks": [{"id": "manuscript-block", "text": records[0]["text"]}]}],
              "findings": [{"id": "check.test"}]}
    review = {
        "origin": "model_native", "independent_human_validation": False, "provider_panel_run": False,
        "anchors": {"A1": {"source_id": "P1", "block_id": "manuscript-block",
                           "quote": "cells", "start": 9, "end": 14}},
        "items": [{"id": "ITEM-1", "decision": "verify", "evidence": ["A1"],
                   "counterevidence": [], "engine_finding_ids": ["check.test"]}],
        "baseline_triage": [{"finding_ids": ["check.test"], "review_item_ids": ["ITEM-1"],
                             "reason": "Inspect before escalating."}],
    }
    return review, records, report


class ShowcaseTests(unittest.TestCase):
    def test_extraction_preserves_inline_text_back_matter_and_floated_captions(self):
        normalized, records = showcases.normalize_jats(JATS)
        self.assertIn(b"Measured cells carefully.", normalized)
        self.assertIn(b"### Controls", normalized)
        self.assertIn(b"Code is available.", normalized)
        self.assertIn(b"Caption retained.", normalized)
        self.assertNotIn(b"Duplicate content", normalized)
        self.assertNotIn(b"Not manuscript evidence", normalized)
        self.assertNotIn(b"never-download", normalized)
        self.assertEqual(next(r["text"] for r in records if r["source_id"] == "P1"),
                         "Measured cells carefully.")

    def test_duplicate_source_ids_and_entities_fail_closed(self):
        for raw in (JATS.replace(b'id="P2"', b'id="P1"'),
                    b'<!DOCTYPE article [<!ENTITY x "unsafe">]>' + JATS):
            with self.subTest(raw=raw[:70]), self.assertRaises(ValueError):
                showcases.normalize_jats(raw)

    def test_download_requires_explicit_flag_and_cache_is_checked(self):
        manifest = {"xml_url": "https://example.org/public.xml", "xml_sha256": showcases.digest(JATS)}
        with tempfile.TemporaryDirectory() as tmp, patch.object(showcases.urllib.request, "urlopen") as request:
            cache = Path(tmp)
            with self.assertRaisesRegex(ValueError, "--download"):
                showcases.source_bytes(manifest, cache)
            request.assert_not_called()
            (cache / "source.xml").write_bytes(JATS)
            self.assertEqual(showcases.source_bytes(manifest, cache), JATS)
            request.assert_not_called()
            (cache / "source.xml").write_bytes(JATS + b" ")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                showcases.source_bytes(manifest, cache, download=True)
            # Corrupt cache is not silently replaced, even with --download.
            request.assert_not_called()

    def test_downloaded_drift_and_oversize_never_enter_cache(self):
        manifest = {"xml_url": "https://example.org/public.xml", "xml_sha256": showcases.digest(JATS)}
        for raw, maximum in ((b"unexpected replacement", showcases.MAX_BYTES), (JATS, 4)):
            with self.subTest(maximum=maximum), tempfile.TemporaryDirectory() as tmp:
                cache = Path(tmp) / "cache"
                with patch.object(showcases.urllib.request, "urlopen", return_value=io.BytesIO(raw)), \
                        patch.object(showcases, "MAX_BYTES", maximum):
                    with self.assertRaisesRegex(ValueError, "hash mismatch"):
                        showcases.source_bytes(manifest, cache, download=True)
                self.assertFalse(cache.exists())

    def test_explicit_download_persists_only_verified_bytes(self):
        manifest = {"xml_url": "https://example.org/public.xml", "xml_sha256": showcases.digest(JATS)}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(showcases.urllib.request, "urlopen", return_value=io.BytesIO(JATS)) as request:
            cache = Path(tmp) / "cache"
            self.assertEqual(showcases.source_bytes(manifest, cache, download=True), JATS)
            self.assertEqual((cache / "source.xml").read_bytes(), JATS)
            self.assertEqual(request.call_args.args[0].full_url, manifest["xml_url"])

    def test_text_checks_never_claim_scientific_validation(self):
        result = showcases.verify_review(*review_fixture())
        self.assertEqual(result["exact_anchors"], 1)
        self.assertFalse(result["scientific_validity_verified"])

    def test_tampered_span_source_and_block_are_rejected(self):
        for field, value in (("quote", "invented"), ("start", 8), ("end", -1),
                             ("start", True), ("source_id", "missing"), ("block_id", "missing")):
            review, records, report = review_fixture()
            review["anchors"]["A1"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "Evidence mismatch"):
                showcases.verify_review(review, records, report)
        review, records, report = review_fixture()
        records[0]["text"] = "Different context with the same cells quote."
        with self.assertRaisesRegex(ValueError, "Evidence mismatch"):
            showcases.verify_review(review, records, report)

    def test_missing_duplicate_and_unknown_triage_are_rejected(self):
        for ids in ([], ["check.test", "check.test"], ["check.unknown"]):
            review, records, report = review_fixture()
            review["baseline_triage"][0]["finding_ids"] = ids
            with self.subTest(ids=ids), self.assertRaisesRegex(ValueError, "exactly once"):
                showcases.verify_review(review, records, report)

    def test_invented_engine_citations_and_provenance_claims_are_rejected(self):
        review, records, report = review_fixture()
        review["items"][0]["engine_finding_ids"] = ["invented"]
        with self.assertRaisesRegex(ValueError, "unknown engine"):
            showcases.verify_review(review, records, report)
        for field, value in (("origin", "provider"), ("independent_human_validation", True),
                             ("provider_panel_run", True)):
            review, records, report = review_fixture()
            review[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "provenance"):
                showcases.verify_review(review, records, report)

    def test_public_artifacts_keep_text_separate_and_render_consistently(self):
        for slug in showcases.PAPERS:
            public = ROOT / "showcases" / slug
            manifest = showcases.read_json(public / "source.json")
            review = showcases.read_json(public / "review.json")
            baseline = showcases.read_json(public / "baseline.json")
            receipt = showcases.read_json(public / "provenance.json")
            with self.subTest(paper=slug):
                self.assertEqual((public / "review.md").read_text(encoding="utf-8"),
                                 showcases.render_review(review, manifest))
                readme = (public / "README.md").read_text(encoding="utf-8")
                self.assertEqual(readme, showcases.summary_readme(review, readme))
                self.assertEqual(baseline["manuscript_sha256"], manifest["normalized_sha256"])
                self.assertEqual(receipt["public_baseline_sha256"],
                                 showcases.digest((public / "baseline.json").read_bytes()))
                self.assertEqual(receipt["exact_anchors"], len(review["anchors"]))
                self.assertEqual(receipt["baseline_findings_triaged"], len(baseline["findings"]))
                self.assertEqual(baseline["provider_calls"], 0)
                self.assertNotIn("documents", baseline)
                self.assertNotIn("/Users/", json.dumps(baseline))
                self.assertFalse(review["independent_human_validation"])
                all_ids = [i for group in review["baseline_triage"] for i in group["finding_ids"]]
                self.assertEqual(len(all_ids), len(set(all_ids)))
                self.assertEqual(set(all_ids), {f["id"] for f in baseline["findings"]})
                for finding in baseline["findings"]:
                    self.assertNotIn("evidence", finding)

    def test_summary_cannot_promote_dismissed_items_or_invent_references(self):
        path = ROOT / "showcases" / "single-cell-foundation-models" / "review.json"
        for item_id in ("SC-6", "SC-5", "invented"):
            review = showcases.read_json(path)
            review["at_a_glance"]["priorities"][0]["item_ids"] = [item_id]
            with self.subTest(item_id=item_id), self.assertRaises(ValueError):
                showcases.verify_summary(review)


if __name__ == "__main__":
    unittest.main()
