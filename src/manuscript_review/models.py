"""Versioned, JSON-serializable contracts shared by all pipeline stages."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import re
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.1.0"
SEVERITIES = ("fatal_flaw", "major", "moderate", "minor", "optional_strengthening")
ISSUE_STATUSES = ("established_issue", "plausible_issue", "speculative_concern")
PRIORITIES = ("P0_verify_before_submission", "P1_high_value_revision",
              "P2_targeted_clarification", "P3_optional_strengthening")


def stable_id(prefix: str, text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return prefix + "-" + sha256(normalized.encode("utf-8")).hexdigest()[:12]


@dataclass
class Block:
    id: str
    document_id: str
    section: str
    text: str
    kind: str = "paragraph"
    page: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    paragraph: Optional[int] = None
    extraction_confidence: str = "high"


@dataclass
class Document:
    id: str
    role: str
    name: str
    path: str
    sha256: str
    format: str
    blocks: List[Block]
    warnings: List[str] = field(default_factory=list)


@dataclass
class Evidence:
    document_id: str
    block_id: str
    section: str
    quote: str
    start: int
    end: int
    relation: str = "trigger"
    page: Optional[int] = None
    line_start: Optional[int] = None
    paragraph: Optional[int] = None


def evidence(block: Block, start: int = 0, end: Optional[int] = None,
             relation: str = "trigger") -> Evidence:
    end = len(block.text) if end is None else end
    line = (block.line_start + block.text[:start].count("\n")
            if block.line_start is not None else None)
    return Evidence(block.document_id, block.id, block.section, block.text[start:end],
                    start, end, relation, block.page, line, block.paragraph)


@dataclass
class Finding:
    id: str
    rule_id: str
    severity: str
    category: str
    manuscript_section: str
    claim: str
    issue: str
    why_it_matters: str
    evidence: List[Evidence]
    suggested_fix: str
    suggested_analysis: str
    confidence: str
    issue_status: str
    reviewer_roles: List[str]
    origin: str = "deterministic"
    priority: str = ""
    priority_rationale: str = ""
    reviewer_likelihood: str = "high"
    effort: str = "medium"
    value: str = "high"
    disposition: str = "active"
    manual_note: Optional[str] = None
    limitation: str = "Text heuristics do not verify the underlying analysis or data."
    basis: str = "manuscript_direct"
    grounding_status: str = "source_verified"
    evidence_statement: str = ""
    support_rationale: str = ""
    topic: str = ""
    claim_ids: List[str] = field(default_factory=list)
    action: Dict[str, Any] = field(default_factory=dict)
    quality_flags: List[str] = field(default_factory=list)
    duplicate_of: Optional[str] = None
    reviewer_assessments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CheckResult:
    id: str
    label: str
    status: str
    evidence: List[Evidence]
    searched_document_ids: List[str]
    searched_block_count: int
    confidence: str
    interpretation: str
    domain: str = "general"


@dataclass
class Review:
    schema_version: str
    tool_version: str
    run_id: str
    created_at: str
    target_journal: Optional[str]
    documents: List[Document]
    extraction: Dict[str, Any]
    findings: List[Finding]
    checklist: List[CheckResult]
    reviewer_runs: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    warnings: List[str]
    configuration: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None
    claim_analyses: List[Dict[str, Any]] = field(default_factory=list)
    adversarial: Dict[str, Any] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)
    llm: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def review_from_dict(data):
    """Load a versioned local review after validating its sources and references."""
    from .validation import validate_report
    try:
        validate_report(data)
        values = dict(data)
        values["documents"] = [Document(**{**d, "blocks": [Block(**b) for b in d["blocks"]]})
                               for d in data["documents"]]
        values["findings"] = [Finding(**{**f, "evidence": [Evidence(**e) for e in f["evidence"]]})
                              for f in data["findings"]]
        values["checklist"] = [CheckResult(**{**c, "evidence": [Evidence(**e) for e in c["evidence"]]})
                               for c in data["checklist"]]
        return Review(**values)
    except (TypeError, KeyError):
        from .errors import ReviewError
        raise ReviewError("Saved review does not match the current versioned report contract.") from None
