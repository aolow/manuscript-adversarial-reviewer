from __future__ import annotations

from datetime import datetime, timezone
import logging
from uuid import uuid4

from . import __version__
from .configuration import DEFAULT_CONFIG, prepare_overrides, apply_finding_overrides
from .extraction import extract
from .ingestion import ingest
from .models import Review, SCHEMA_VERSION
from .prioritization import prioritize
from .reporting import build_sections
from .reviewers import orchestrate
from .rules import run_rules
from .adversarial import build_adversarial
from .grounding import reconcile

logger = logging.getLogger(__name__)


def review_manuscript(path, supplements=(), journal=None, config=None, overrides_path=None, provider=None):
    config = config or DEFAULT_CONFIG.copy()
    documents = [ingest(path)]
    documents.extend(ingest(p, "supplement-%d" % number, "supplement")
                     for number, p in enumerate(supplements, 1))
    logger.info("Extracted %d blocks from %d document(s).",
                sum(len(d.blocks) for d in documents), len(documents))
    overrides = prepare_overrides(overrides_path, documents)
    extraction = extract(documents)
    domains = (set(extraction["domains"]) | set(config["include_domains"])) - set(config["exclude_domains"])
    extraction["domains"] = sorted(domains)
    findings, checklist = run_rules(documents, extraction, config["disabled_rules"])
    baseline_overrides = {**overrides, "findings": [f for f in overrides.get("findings", [])
                                                  if not f.get("id", "").startswith("reviewer.")]}
    apply_finding_overrides(findings, baseline_overrides)
    reviewer_runs, packets = orchestrate(documents, extraction, findings, journal, provider)
    reconciliation = reconcile(findings)
    # Human/version-bound overrides are authoritative and therefore apply after
    # provider duplicate reconciliation, which must not overwrite them.
    apply_finding_overrides(findings, overrides)
    by_id = {finding.id: finding for finding in findings}
    reconciliation = [
        event for event in reconciliation
        if by_id.get(event["duplicate_id"]) is not None
        and by_id[event["duplicate_id"]].disposition == "duplicate"
        and by_id[event["duplicate_id"]].duplicate_of == event["canonical_id"]
    ]
    findings.sort(key=lambda f: (f.priority, f.id))
    warnings = [d.id + ": " + warning for d in documents for warning in d.warnings]
    warnings.append("No underlying data, analysis code, figure images, or external literature were verified.")
    if provider is None:
        warnings.append("Reviewer roles route deterministic findings; no LLM review was performed.")
    elif getattr(provider, "dry_run", False):
        warnings.append("Dry run: exact requests were prepared locally; no LLM API call was made.")
    warnings.extend(run["role"] + ": " + run["note"] for run in reviewer_runs if run["mode"] == "failed")
    if config["disabled_rules"] or config["exclude_domains"]:
        warnings.append("Configuration reduced audit coverage; inspect configuration in JSON.")
    review = Review(SCHEMA_VERSION, __version__, "run-" + uuid4().hex,
                    datetime.now(timezone.utc).isoformat(), journal, documents, extraction,
                    findings, checklist, reviewer_runs, [], warnings,
                    {**config, "manual_overrides": overrides})
    review.quality = {"duplicate_groups": reconciliation,
                      "failed_roles": [run["role"] for run in reviewer_runs if run["mode"] == "failed"],
                      "semantic_entailment_verified": False}
    if provider is not None and hasattr(provider, "metadata"):
        review.llm = provider.metadata()
    review.adversarial = build_adversarial(review)
    review.sections = build_sections(review)
    if provider is not None:
        from .diagnostics import attach_diagnostics
        attach_diagnostics(review)
    from .validation import validate_report
    validate_report(review.to_dict())
    logger.info("Generated %d findings and %d checklist entries.", len(findings), len(checklist))
    return review, packets
