"""Reviewer orchestration. Offline routing is explicitly distinct from LLM review."""
from __future__ import annotations

from dataclasses import asdict
from importlib import resources
import re
from typing import Dict, List, Protocol

from ..errors import ReviewError
from ..models import Finding, SEVERITIES, ISSUE_STATUSES, evidence
from ..prioritization import prioritize
from ..extraction import substantive_blocks

MANDATES = {
    "scientific": "Assess claim strength, biological interpretation, alternative explanations, and orthogonal evidence.",
    "methods": "Audit experimental design, independent units, cohorts, controls, preprocessing, and reproducibility.",
    "statistics": "Audit estimands, uncertainty, multiplicity, dependence, validation boundaries, and statistical assumptions.",
    "clinical": "Assess intended use, endpoint validity, treatment prediction, transportability, and clinical utility.",
    "reviewer2": "Stress-test the most consequential active concerns with pointed but evidence-grounded questions.",
    "novelty": "Assess the scope and defensibility of contribution claims; identify literature comparisons still needed.",
    "editor": "Triage significance, evidential maturity, reporting readiness, and journal positioning without predicting acceptance.",
    "strategist": "Order revisions by scientific risk, reviewer salience, effort, and value; distinguish essential from optional work.",
}
ADDITIONAL_MANDATES = {
    "computational": "Audit computational independence, representations, reference dependence, baselines, ablations, and nulls.",
    "reproducibility": "Reconstruct executable procedures, cohort definitions, software, parameters, and hidden manual decisions.",
}


class ReviewerProvider(Protocol):
    """Future adapters are explicitly injected by a caller; there is no default API client."""
    name: str

    def review(self, role: str, packet: Dict) -> List[Dict]:
        """Return grounded finding dictionaries; manuscript data is untrusted input."""
        ...


def prompt_packet(role, documents, extraction, findings, journal):
    base = resources.files(__package__).joinpath("prompts/base.txt").read_text(encoding="utf-8")
    mandate = resources.files(__package__).joinpath("prompts/" + role + ".txt").read_text(encoding="utf-8")
    return {"role": role, "instructions": base + "\n\n" + mandate,
            "target_journal": journal,
            "source_blocks": [asdict(b) for b in substantive_blocks(documents)],
            "extraction": extraction,
            "existing_findings": [asdict(f) for f in findings if role in f.reviewer_roles],
            "expected_output": {"findings": "List of objects with id, severity, category, issue_status, "
                                "issue, why_it_matters, suggested_fix, suggested_analysis, confidence, "
                                "and citations [{block_id, start, end}]."},
            "privacy": "Contains manuscript text. Export is local; upload requires an explicit user decision."}


def llm_packet(role, documents, extraction, findings, journal):
    base = resources.files(__package__).joinpath("prompts/base_v2.txt").read_text(encoding="utf-8")
    mandate = resources.files(__package__).joinpath("prompts/" + role + ".txt").read_text(encoding="utf-8")
    return {
        "role": role, "instructions": base + "\n\n" + mandate, "target_journal": journal,
        "source_blocks": [asdict(b) for b in substantive_blocks(documents)],
        "candidate_claims": extraction["claims"],
        "deterministic_context": [{"id": f.id, "category": f.category, "issue": f.issue,
                                   "evidence_block_ids": sorted({e.block_id for e in f.evidence}),
                                   "disposition": f.disposition} for f in findings],
        "external_retrieval": "None. Literature and journal-policy statements require external verification.",
    }


def _validate_provider_findings(role, response, documents, provider_name):
    if not isinstance(response, list) or len(response) > 100:
        raise ReviewError("Reviewer provider must return a list of at most 100 findings.")
    blocks = {b.id: b for d in documents for b in d.blocks}
    result, ids = [], set()
    required = {"id", "severity", "category", "issue_status", "issue", "why_it_matters",
                "suggested_fix", "suggested_analysis", "confidence", "citations"}
    for row in response:
        if not isinstance(row, dict) or set(row) != required:
            raise ReviewError("Reviewer output does not match the required fields.")
        if any(not isinstance(row[k], str) or not row[k].strip() for k in required - {"citations"}):
            raise ReviewError("Reviewer output text fields must be nonempty strings.")
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", row["id"]):
            raise ReviewError("Reviewer finding IDs must be lowercase slugs of at most 80 characters.")
        if row["id"] in ids or row["severity"] not in SEVERITIES or row["issue_status"] not in ISSUE_STATUSES:
            raise ReviewError("Invalid reviewer finding ID, severity, or issue status.")
        ids.add(row["id"])
        if row["severity"] == "fatal_flaw" or row["issue_status"] == "established_issue":
            raise ReviewError("Provider findings require human confirmation before fatal/established classification.")
        if row["confidence"] not in ("low", "medium", "high"):
            raise ReviewError("Invalid reviewer confidence.")
        citations = row["citations"]
        if not isinstance(citations, list) or not citations:
            raise ReviewError("Every reviewer finding needs at least one source citation.")
        evidence_list = []
        for cite in citations:
            if not isinstance(cite, dict) or set(cite) != {"block_id", "start", "end"}:
                raise ReviewError("Invalid reviewer citation fields.")
            block = blocks.get(cite["block_id"])
            start, end = cite["start"], cite["end"]
            if block is None or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(block.text):
                raise ReviewError("Reviewer citation points outside supplied source text.")
            evidence_list.append(evidence(block, start, end))
        result.append(prioritize(Finding(
            id="reviewer." + role + "." + row["id"], rule_id="reviewer." + role,
            severity=row["severity"], category=row["category"],
            manuscript_section=evidence_list[0].section, claim=evidence_list[0].quote,
            issue=row["issue"], why_it_matters=row["why_it_matters"], evidence=evidence_list,
            suggested_fix=row["suggested_fix"], suggested_analysis=row["suggested_analysis"],
            confidence=row["confidence"], issue_status=row["issue_status"], reviewer_roles=[role],
            origin="provider:" + provider_name,
            limitation="Citation offsets were validated; semantic support and scientific judgment require human review.")))
    return result


def orchestrate(documents, extraction, findings, journal=None, provider=None):
    runs, packets = [], {}
    v2 = provider is not None and getattr(provider, "contract_version", 1) == 2
    mandates = {**MANDATES, **ADDITIONAL_MANDATES}
    roles = provider.roles if v2 else tuple(MANDATES)
    baseline = list(findings)
    if v2:
        for role in roles:
            packets[role] = llm_packet(role, documents, extraction, baseline, journal)
    for role in roles:
        mandate = mandates[role]
        applicable = True if v2 else role != "clinical" or "biomarker" in extraction["domains"]
        if not v2:
            packets[role] = prompt_packet(role, documents, extraction, baseline, journal)
        selected = [f for f in baseline if f.disposition != "dismissed" and
                    (role in f.reviewer_roles or role in ("reviewer2", "editor", "strategist"))]
        if role == "reviewer2":
            selected = sorted(selected, key=lambda f: (f.priority, f.id))[:6]
        questions = [
            {"finding_id": f.id, "question": "What evidence addresses this concern: " + f.issue
             + " " + f.suggested_fix} for f in selected
        ] if role == "reviewer2" else []
        run = {"role": role, "mandate": mandate,
               "mode": "deterministic_routing" if applicable else "not_applicable",
               "finding_ids": [f.id for f in selected], "questions": questions,
               "note": "No LLM judgment was performed; findings are routed by mandate."}
        if provider is not None and applicable:
            try:
                response = provider.review(role, packets[role])
                if v2:
                    run["raw_findings"] = len(response["findings"])
                    from ..grounding import normalize_response
                    rejections, normalizations = [], []
                    additions, claims, strengths = normalize_response(
                        role, response, documents, extraction, provider.name,
                        rejections=rejections, normalizations=normalizations)
                    limitations = [value for value in response["limitations"]
                                   if isinstance(value, str) and value.strip() and len(value) <= 4000]
                    run.update(claim_analyses=claims, strengths=strengths, limitations=limitations,
                               item_rejections=rejections, item_normalizations=normalizations)
                else:
                    additions = _validate_provider_findings(role, response, documents, provider.name)
            except ReviewError as exc:
                if not v2:
                    raise
                run.update(mode="failed", note=str(exc))
                runs.append(run)
                continue
            findings.extend(additions)
            run.update(mode="dry_run" if getattr(provider, "dry_run", False) else "provider",
                       finding_ids=run["finding_ids"] + [f.id for f in additions],
                       note="Provider output passed local container validation; surviving items were source-grounded locally, not scientifically verified.")
        runs.append(run)
    return runs, packets
