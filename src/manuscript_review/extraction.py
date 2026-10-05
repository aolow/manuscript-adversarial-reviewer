"""Deliberately shallow, inspectable extraction. Candidates are not verified facts."""
from __future__ import annotations

from dataclasses import asdict
import re
from .models import evidence, stable_id

REFERENCE = re.compile(r"\b(?:Fig(?:ure)?\.?|Table)\s*(S?\d+[A-Za-z]?)", re.I)
CLAIM = re.compile(r"\b(?:we (?:show|demonstrate|establish|identify|present|propose|develop|find)|"
                   r"our (?:study|results|method|model)|predict\w*|caus\w*|mechanis\w*|"
                   r"conserv\w*|first|novel|outperform\w*)\b", re.I)
DOMAIN_PATTERNS = {
    "predictive": r"\b(?:predict\w*|classifier|machine learning|AUROC|AUPRC|cross.validation|train.test)\b",
    "single_cell": r"\b(?:single.cell|scRNA.seq|pseudobulk|cell.level|UMAP|Seurat|Scanpy)\b",
    "perturbation": r"\b(?:CRISPR\w*|perturb\w*|sgRNA|guide RNA|knockout|knockdown|MAGeCK|base edit\w*)\b",
    "biomarker": r"\b(?:biomarker|clinical use|prognos\w*|diagnos\w*|survival|time.to.event)\b",
    "testing": r"\b(?:p.values?|t.test|Wilcoxon|differential expression|statistical\w*|significan\w*|ANOVA)\b",
    "quantitative": r"\b(?:patients?|donors?|samples?|cells?|cohorts?|AUROC|effect size|p.values?)\b",
    "survival": r"\b(?:survival|time.to.event|Cox|Kaplan.Meier)\b",
}
EXCLUDED = ("references", "bibliography", "acknowledg")


def substantive_blocks(documents):
    return [b for doc in documents for b in doc.blocks
            if b.kind != "heading" and not b.section.lower().startswith(EXCLUDED)]


def sentences(block):
    for match in re.finditer(r".+?(?:[.!?](?=\s+[A-Z]|\s*$)|$)", block.text, re.S):
        start, end = match.span()
        while start < end and block.text[start].isspace():
            start += 1
        if start < end:
            yield block.text[start:end], evidence(block, start, end)


def extract(documents):
    blocks = substantive_blocks(documents)
    body = "\n".join(b.text for b in blocks)
    domains = ["general"]
    domains.extend(key for key, pattern in DOMAIN_PATTERNS.items() if re.search(pattern, body, re.I))
    claims, methods, cohorts, statistics, references = [], [], [], [], []
    for block in blocks:
        if block.section.startswith("Methods"):
            methods.append({"id": stable_id("method", block.text), "evidence": asdict(evidence(block)),
                            "confidence": "medium", "status": "reported_text"})
        for text, source in sentences(block):
            ev = asdict(source)
            if CLAIM.search(text) and not block.section.startswith(("Methods", "Availability", "Code", "Data")):
                claims.append({"id": stable_id("claim", block.id + str(source.start) + text), "text": text,
                               "section": block.section, "evidence": ev, "confidence": "medium"})
            if re.search(r"\b(?:cohort|dataset|donors?|patients?|participants?|GSE\d+|TCGA|GEO|ICGC)\b", text, re.I):
                sizes = re.findall(r"\b\d[\d,]*\s+(?:patients?|donors?|samples?|cells?|participants?)\b|\bn\s*=\s*\d+", text, re.I)
                cohorts.append({"id": stable_id("cohort", block.id + text), "text": text, "sample_size_mentions": sizes,
                                "evidence": ev, "confidence": "low",
                                "limitation": "Mentions are not deduplicated cohorts or verified replication units."})
            if re.search(r"\b(?:AUROC|AUPRC|p.value|confidence interval|FDR|Benjamini|Cox|Kaplan|"
                         r"Wilcoxon|t.test|regression|cross.validation|bootstrap|permutation)\b", text, re.I):
                statistics.append({"text": text, "evidence": ev, "confidence": "medium"})
            for match in REFERENCE.finditer(text):
                references.append({"label": match.group(0), "evidence": ev, "confidence": "medium"})
    links = []
    result_blocks = [b for b in blocks if b.section.startswith(("Results", "Figure Legends"))]
    for claim in claims:
        refs = [m.group(0) for m in REFERENCE.finditer(claim["text"])]
        candidates = []
        # Link only by an explicit figure/table label, never semantic similarity.
        for block in result_blocks:
            block_refs = {re.sub(r"[^a-z0-9]", "", m.group(0).lower().replace("figure", "fig"))
                          for m in REFERENCE.finditer(block.text)}
            if refs and any(re.sub(r"[^a-z0-9]", "", r.lower().replace("figure", "fig")) in block_refs for r in refs):
                candidates.append(asdict(evidence(block, relation="candidate_support")))
        links.append({"claim_id": claim["id"], "claim": claim["text"], "claim_evidence": claim["evidence"],
                      "explicit_references": refs, "candidate_evidence": candidates,
                      "support_status": "candidate_reference_link" if candidates else "not_established_from_manuscript",
                      "interpretation": "A shared reference is a navigation aid, not a verified supporting result."})
    return {"domains": domains, "claims": claims, "methods": methods, "cohorts": cohorts,
            "statistical_methods": statistics, "figure_table_references": references,
            "claim_evidence_map": links,
            "limitations": ["Extraction is heuristic; false positives and omissions require manual review.",
                           "Figures, causal support, biological validity, and novelty are not independently verified."]}
