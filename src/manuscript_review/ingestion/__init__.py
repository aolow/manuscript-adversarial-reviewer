"""Readers preserve source locators; they never execute manuscript content."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
from typing import List
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from ..errors import ReviewError
from ..models import Block, Document, stable_id
from .sections import heading

MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_XML_BYTES = 30 * 1024 * 1024
MAX_TEXT_CHARS = 5_000_000
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _visible_text(element):
    if element.tag in (NS + "del", NS + "moveFrom"):
        return ""
    if element.tag == NS + "t":
        return element.text or ""
    if element.tag in (NS + "tab", NS + "br"):
        return " "
    return "".join(_visible_text(child) for child in element)


class Collector:
    def __init__(self, document_id):
        self.document_id = document_id
        self.blocks: List[Block] = []
        self.section = "Unsectioned"
        self.canonical = "Unsectioned"
        self.counts = {}
        self.characters = 0

    def add(self, text, kind="paragraph", styled=False, **location):
        text = text.strip()
        if not text:
            return
        self.characters += len(text)
        if self.characters > MAX_TEXT_CHARS:
            raise ReviewError("Extracted text exceeds the 5 million character limit. Split the document.")
        detected = heading(text, styled) if kind != "table" else None
        if detected:
            title, canonical = detected
            if canonical:
                self.canonical = canonical
                self.section = canonical
            else:
                self.section = (self.canonical + " / " + title
                                if self.canonical != "Unsectioned" else title)
            kind = "heading"
        key = stable_id(self.document_id, self.section + "\n" + text)
        self.counts[key] = self.counts.get(key, 0) + 1
        self.blocks.append(Block(id=key + "-" + str(self.counts[key]),
                                 document_id=self.document_id, section=self.section,
                                 text=text, kind=kind, **location))


def _text_lines(text, collector, page=None, confidence="high"):
    pending = []
    start = None

    def flush(end):
        nonlocal pending, start
        if pending:
            collector.add("\n".join(pending), page=page, line_start=start,
                          line_end=end, extraction_confidence=confidence)
        pending, start = [], None

    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if not line.strip() or heading(line):
            flush(number - 1)
            if line.strip():
                collector.add(line, page=page, line_start=number, line_end=number,
                              extraction_confidence=confidence)
        elif line.lstrip().startswith("|"):
            flush(number - 1)
            collector.add(line, kind="table", page=page, line_start=number, line_end=number,
                          extraction_confidence=confidence)
        else:
            if start is None:
                start = number
            pending.append(line)
    flush(len(lines))


def _docx(path, collector, warnings):
    try:
        with ZipFile(path) as archive:
            info = archive.getinfo("word/document.xml")
            if info.file_size > MAX_XML_BYTES:
                raise ReviewError("DOCX document.xml exceeds the 30 MB decompressed limit.")
            xml = archive.read(info)
            if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
                raise ReviewError("DOCX XML entity declarations are not supported.")
            root = ET.fromstring(xml)
    except (BadZipFile, KeyError, ET.ParseError, RuntimeError) as exc:
        raise ReviewError("Cannot read DOCX document.xml: " + str(exc)) from exc
    body = root.find(NS + "body")
    if body is None:
        raise ReviewError("DOCX has no document body.")
    if root.find(".//" + NS + "del") is not None or root.find(".//" + NS + "ins") is not None:
        warnings.append("DOCX contains tracked changes: inserted text is included and deleted text excluded.")
    paragraph = 0
    for element in body:
        if element.tag == NS + "p":
            paragraph += 1
            value = _visible_text(element)
            style = element.find("./" + NS + "pPr/" + NS + "pStyle")
            styled = style is not None and "heading" in style.attrib.get(NS + "val", "").lower()
            collector.add(value, paragraph=paragraph, styled=styled)
        elif element.tag == NS + "tbl":
            for row in element.findall(NS + "tr"):
                paragraph += 1
                cells = [" ".join(_visible_text(p) for p in cell.findall(NS + "p"))
                         for cell in row.findall(NS + "tc")]
                collector.add(" | ".join(cells), kind="table", paragraph=paragraph)
    warnings.append("DOCX extraction covers body paragraphs and table rows; images, equations, "
                    "footnotes, headers, comments, and page layout are not interpreted.")


def ingest(path, document_id="manuscript", role="manuscript"):
    path = Path(path).expanduser().resolve()
    try:
        if not path.is_file():
            raise ReviewError("Input file does not exist: " + str(path))
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ReviewError("Input exceeds 50 MB: " + str(path))
        raw = path.read_bytes()
        suffix = path.suffix.lower()
        collector, warnings = Collector(document_id), []
        if suffix in (".md", ".markdown", ".txt"):
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ReviewError("Text must be UTF-8. Convert the file before reviewing.") from exc
            _text_lines(text, collector)
        elif suffix == ".docx":
            _docx(path, collector, warnings)
        elif suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise ReviewError('PDF support needs: pip install ".[pdf]"') from exc
            try:
                reader = PdfReader(path)
                if reader.is_encrypted and not reader.decrypt(""):
                    raise ReviewError("PDF is password protected. Supply a decrypted local copy.")
                if len(reader.pages) > 1000:
                    raise ReviewError("PDF exceeds the 1,000-page limit.")
                for number, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    if len(text.strip()) < 30:
                        warnings.append("PDF page %d has little or no extractable text; OCR may be needed." % number)
                    _text_lines(text, collector, page=number, confidence="medium")
            except ReviewError:
                raise
            except Exception as exc:
                raise ReviewError("PDF extraction failed: " + str(exc)) from exc
            warnings.append("PDF text order and columns may be inaccurate; figures and visual tables "
                            "are not interpreted. Page line numbers refer to extracted text.")
        else:
            raise ReviewError("Unsupported input format %s; use PDF, DOCX, Markdown, or TXT." % suffix)
    except OSError as exc:
        raise ReviewError("Cannot read input: " + str(exc)) from exc
    if not any(b.kind != "heading" and b.text.strip() for b in collector.blocks):
        raise ReviewError("No reviewable text extracted. For scanned PDFs, run OCR first.")
    if not any(b.kind == "heading" for b in collector.blocks):
        warnings.append("No recognized headings: section assignments are uncertain.")
    return Document(document_id, role, path.name, path.name, sha256(raw).hexdigest(),
                    suffix.lstrip("."), collector.blocks, warnings)
