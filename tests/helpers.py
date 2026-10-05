from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from manuscript_review.pipeline import review_manuscript

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, text, name="paper.md"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def review_text(self, text, **kwargs):
        return review_manuscript(self.write(text), **kwargs)[0]

    def check(self, text, identifier):
        review = self.review_text(text)
        return next(c for c in review.checklist if c.id == identifier)

    def docx(self, body):
        path = self.root / "paper.docx"
        with ZipFile(path, "w") as out:
            out.writestr("word/document.xml",
                         '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                         "<w:body>" + body + "</w:body></w:document>")
        return path


def minimal_pdf(path, text_lines=None):
    """A real, tiny single-page PDF; no PDF-generation dependency required."""
    content = b"BT /F1 12 Tf 50 750 Td "
    for line in text_lines or []:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content += ("(%s) Tj 0 -20 Td " % escaped).encode("ascii")
    content += b"ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    data = b"%PDF-1.4\n"
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(index).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        data += ("%010d 00000 n \n" % offset).encode()
    data += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF"
    path.write_bytes(data)
