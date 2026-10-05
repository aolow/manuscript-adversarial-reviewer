import importlib.util
import unittest
from unittest.mock import patch

from manuscript_review.errors import ReviewError
from manuscript_review.extraction import extract, sentences
from manuscript_review.ingestion import ingest
from .helpers import WorkspaceTest, minimal_pdf


class IngestionTests(WorkspaceTest):
    def test_markdown_sections_locations_and_hash(self):
        path = self.write("# Title\n\n## Methods\n\nWe used 12 patients.\nAcross two cohorts.\n")
        doc = ingest(path)
        block = doc.blocks[-1]
        self.assertEqual(block.section, "Methods")
        self.assertEqual((block.line_start, block.line_end), (5, 6))
        self.assertEqual(len(doc.sha256), 64)
        self.assertEqual(doc.sha256, ingest(path).sha256)
        self.assertEqual(doc.blocks, ingest(path).blocks)
        sentence_evidence = list(sentences(block))
        self.assertEqual(sentence_evidence[1][1].line_start, 6)

    def test_unknown_subheadings_keep_methods_parent(self):
        doc = ingest(self.write("Methods\n\n### Processing\n\nWe used 12 patients."))
        self.assertEqual(doc.blocks[-1].section, "Methods / Processing")

    def test_duplicate_paragraphs_have_unique_block_ids(self):
        doc = ingest(self.write("Methods\n\nRepeated text.\n\nRepeated text."))
        self.assertEqual(len(doc.blocks), len({b.id for b in doc.blocks}))

    def test_docx_headings_table_and_track_changes(self):
        path = self.docx(
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Methods</w:t></w:r></w:p>'
            '<w:p><w:del><w:r><w:t>Deleted claim.</w:t></w:r></w:del>'
            '<w:ins><w:r><w:t>We used 20 patients.</w:t></w:r></w:ins></w:p>'
            '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Donors</w:t></w:r></w:p></w:tc>'
            '<w:tc><w:p><w:r><w:t>20</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
        doc = ingest(path)
        self.assertEqual(doc.blocks[1].text, "We used 20 patients.")
        self.assertEqual(doc.blocks[-1].text, "Donors | 20")
        self.assertEqual(doc.blocks[-1].kind, "table")
        self.assertEqual(doc.blocks[-1].section, "Methods")
        self.assertTrue(any("tracked" in w for w in doc.warnings))

    def test_invalid_docx(self):
        with self.assertRaisesRegex(ReviewError, "DOCX"):
            ingest(self.write("not a zip", "bad.docx"))

    def test_missing_file_and_bad_extension(self):
        with self.assertRaisesRegex(ReviewError, "does not exist"):
            ingest(self.root / "absent.pdf")
        with self.assertRaisesRegex(ReviewError, "Unsupported"):
            ingest(self.write("abc", "paper.csv"))

    def test_empty_and_invalid_encoding(self):
        with self.assertRaisesRegex(ReviewError, "No reviewable"):
            ingest(self.write(" \n"))
        path = self.root / "bad.txt"
        path.write_bytes(b"\xff")
        with self.assertRaisesRegex(ReviewError, "UTF-8"):
            ingest(path)

    def test_file_size_limit(self):
        path = self.write("abcd")
        with patch("manuscript_review.ingestion.MAX_FILE_BYTES", 2):
            with self.assertRaisesRegex(ReviewError, "50 MB"):
                ingest(path)

    def test_docx_xml_size_limit(self):
        path = self.docx("<w:p><w:r><w:t>Text</w:t></w:r></w:p>")
        with patch("manuscript_review.ingestion.MAX_XML_BYTES", 2):
            with self.assertRaisesRegex(ReviewError, "decompressed"):
                ingest(path)

    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "Install .[pdf] to test PDF ingestion.")
    def test_pdf_page_provenance(self):
        path = self.root / "paper.pdf"
        minimal_pdf(path, ["Methods", "We used 12 patients and 48000 cells.", "Results", "AUROC was 0.80."])
        doc = ingest(path)
        self.assertEqual(doc.blocks[-1].section, "Results")
        self.assertEqual(doc.blocks[-1].page, 1)
        self.assertEqual(doc.blocks[-1].extraction_confidence, "medium")

    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "Install .[pdf] to test PDF ingestion.")
    def test_no_text_pdf_fails_actionably(self):
        path = self.root / "blank.pdf"
        minimal_pdf(path)
        with self.assertRaisesRegex(ReviewError, "OCR"):
            ingest(path)

    def test_reference_text_excluded_from_extraction(self):
        doc = ingest(self.write("Methods\n\nWe studied 12 patients.\n\nReferences\n\n"
                                "The first-ever single-cell model proves a causal mechanism."))
        result = extract([doc])
        self.assertEqual(result["claims"], [])
        self.assertNotIn("single_cell", result["domains"])
