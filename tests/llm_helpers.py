"""Synthetic-only provider responses; these helpers never call a network."""
from copy import deepcopy
import json

PAPER = """# Synthetic model

## Abstract

Our model predicts response in cancer patients.

## Methods

We selected genes using all samples before splitting patients into training and test sets.

Code is available in a versioned repository.

## Results

Our model achieved an AUROC of 0.91 in the test cohort.
"""


def action():
    return {"kind": "analysis", "input": "Original patient measurements and response labels",
            "comparison": "Original evaluation versus nested selection within training folds",
            "held_out_unit": "Independent patients from a separate cohort",
            "metric": "AUROC, AUPRC, calibration, and patient-bootstrap confidence intervals",
            "expected_interpretation": "A large decline after nested selection weakens the claimed generalization.",
            "text_section": None, "text_claim": None, "recommended_framing": None}


def finding(block, identifier="leakage"):
    return {
        "id": identifier, "topic": "leakage", "issue_key": "feature_selection_before_split",
        "severity": "major", "category": "leakage",
        "issue_status": "plausible_issue", "basis": "manuscript_direct",
        "evidence_statement": block["text"],
        "interpretation": "Selecting genes before the split may inflate held-out prediction performance.",
        "support_rationale": "Gene selection used all samples before the training and test split.",
        "why_it_matters": "Evaluation samples can influence the fitted representation.",
        "suggested_fix": "Refit selection inside each training fold and lock the pipeline before external evaluation.",
        "suggested_analysis": "Compare nested and original performance on independent patients.",
        "confidence": "high", "citations": [{"block_id": block["id"], "quote": block["text"]}],
        "claim_ids": [], "action": action(),
    }


def envelope(findings=None, claims=None, strengths=None):
    return {"findings": findings or [], "claims": claims or [], "strengths": strengths or [], "limitations": []}


def response(payload):
    return {"status": "completed", "id": "synthetic-response", "model": "test-model",
            "usage": {"input_tokens": 100, "output_tokens": 200},
            "output": [{"type": "reasoning", "summary": []},
                       {"type": "message", "content": [{"type": "output_text", "text": json.dumps(payload)}]}]}


def packet_block(body, contains="We selected"):
    packet = json.loads(body["input"][0]["content"])
    return next(b for b in packet["source_blocks"] if contains in b["text"])


def source_block(documents, contains="We selected"):
    from dataclasses import asdict
    return next(asdict(b) for d in documents for b in d.blocks if contains in b.text)


def claim(claim_block, support_block):
    return {"id": "response", "claim_text": claim_block["text"], "importance": "central",
            "importance_rationale": "The response prediction claim is the manuscript's main contribution.",
            "rank": 1, "manuscript_evidence": [{"block_id": claim_block["id"], "quote": claim_block["text"]}],
            "supporting_evidence": [{"block_id": support_block["id"], "quote": support_block["text"]}],
            "strongest_support": "The manuscript reports AUROC 0.91 in the test cohort.",
            "strongest_weakness": "Selection may use held-out samples.",
            "alternative_explanation": "Selection leakage may explain apparent accuracy.",
            "falsification_analysis": action(), "decisive_analysis": action(),
            "impact_if_false": "The predictive contribution would require reanalysis and narrower claims.",
            "confidence_in_claim": "medium"}
