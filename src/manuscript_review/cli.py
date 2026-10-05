from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import tempfile
from .providers.openai import OpenAIReviewer, OpenAISettings

from . import __version__
from .comparison import compare_reviews
from .configuration import load_config
from .errors import ReviewError
from .pipeline import review_manuscript
from .reporting import render_markdown, render_comparison
from .rules.catalogue import CHECKS, PATTERNS


def parser():
    root = argparse.ArgumentParser(
        prog="manuscript-review", description="Local, provenance-first scientific manuscript audit.")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    review = commands.add_parser("review", help="Audit a manuscript and optional supplements.")
    review.add_argument("manuscript", type=Path)
    review.add_argument("--supplement", type=Path, action="append", default=[])
    review.add_argument("--prior", type=Path, help="Also compare against a prior manuscript.")
    review.add_argument("--prior-supplement", type=Path, action="append", default=[])
    review.add_argument("--overrides", type=Path)
    compare = commands.add_parser("compare", help="Audit and compare two manuscript versions.")
    compare.add_argument("old", type=Path)
    compare.add_argument("new", type=Path)
    compare.add_argument("--old-supplement", type=Path, action="append", default=[])
    compare.add_argument("--new-supplement", type=Path, action="append", default=[])
    compare.add_argument("--old-overrides", type=Path)
    compare.add_argument("--new-overrides", type=Path)
    for command in (review, compare):
        command.add_argument("--journal", help="Recorded target; current journal policies are not fetched.")
        command.add_argument("--config", type=Path)
        command.add_argument("--out", type=Path, help="Output directory; default: unique directory under reviews/.")
        command.add_argument("--export-prompts", action="store_true", help="Save local reviewer packets containing manuscript text.")
        command.add_argument("--prior-review", type=Path, help="In paired mode, include a saved prior JSON review, including LLM concerns; hashes must match old inputs.")
        command.add_argument("--llm", action="store_true", help="Explicitly send extracted manuscript text to the selected provider.")
        command.add_argument("--provider", choices=["openai"])
        command.add_argument("--model", help="Required in LLM mode unless MANUSCRIPT_REVIEW_MODEL is set.")
        command.add_argument("--dry-run", action="store_true", help="With --llm: export exact requests, with no API call or key needed.")
        command.add_argument("--roles", help="Comma-separated reviewer names; default: six core adversarial roles.")
        command.add_argument("--temperature", type=float)
        command.add_argument("--reasoning-effort", choices=["none", "minimal", "low", "medium", "high", "xhigh"])
        command.add_argument("--max-output-tokens", type=int, default=6000)
        command.add_argument("--max-request-chars", type=int, default=240000)
        command.add_argument("--timeout", type=float, default=60)
        command.add_argument("--force", action="store_true", help="Replace generated output files if they already exist.")
        command.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                             default=(os.environ.get("MANUSCRIPT_REVIEW_LOG_LEVEL") or "WARNING").upper())
    commands.add_parser("list-rules", help="List rule IDs, applicability, and audit type.")
    bench = commands.add_parser("benchmark", help="Evaluate only local synthetic fixtures; never makes API calls.")
    bench.add_argument("--manifest", type=Path, default=Path("benchmarks/manifest.json"))
    bench.add_argument("--reports", type=Path, help="Optional saved report folder with CASE_ID/report.json.")
    bench.add_argument("--layer", choices=["deterministic", "llm", "combined"], default="deterministic")
    bench.add_argument("--out", type=Path, help="Optional JSON destination; stdout otherwise.")
    export = commands.add_parser("export-chatgpt", help="Create a compact local handoff; never uploads.")
    export.add_argument("report", type=Path)
    export.add_argument("--out", type=Path, required=True)
    export.add_argument("--max-findings", type=int, default=15)
    imported = commands.add_parser("import-chatgpt", help="Validate structured feedback against original sources; stage candidates.")
    imported.add_argument("report", type=Path)
    imported.add_argument("feedback", type=Path)
    imported.add_argument("--context", type=Path, required=True, help="Original exported chatgpt-review.json.")
    imported.add_argument("--manuscript", type=Path, required=True)
    imported.add_argument("--supplement", type=Path, action="append", default=[])
    imported.add_argument("--accept-grounded", action="store_true", help="Explicitly activate only feedback passing all local checks.")
    imported.add_argument("--out", type=Path, required=True)
    evaluation = commands.add_parser("evaluate", help="Prepare and score local blinded human adjudication.")
    stages = evaluation.add_subparsers(dest="stage", required=True)
    prepare = stages.add_parser("prepare")
    prepare.add_argument("--baseline", type=Path, required=True)
    prepare.add_argument("--assisted", type=Path, required=True)
    prepare.add_argument("--expert", type=Path)
    prepare.add_argument("--out", type=Path, required=True)
    score = stages.add_parser("score")
    score.add_argument("bundle", type=Path)
    score.add_argument("--adjudication", type=Path, help="Defaults to BUNDLE/adjudication.json.")
    score.add_argument("--ratings-csv", type=Path, help="Use filled concern-ratings.csv for per-concern ratings.")
    score.add_argument("--out", type=Path, required=True)
    return root


def _json(data):
    return json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def _save(directory, outputs, input_paths, force=False):
    directory = directory.expanduser().resolve()
    inputs = {Path(p).expanduser().resolve() for p in input_paths if p}
    for relative in outputs:
        target = (directory / relative).resolve()
        if target in inputs:
            raise ReviewError("Refusing to overwrite an input file: " + str(target))
        if directory not in target.parents:
            raise ReviewError("Output symlink escapes the output directory: " + str(target))
        if target.exists() and not force:
            raise ReviewError("Output exists: %s. Choose another --out or use --force." % target)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        # Each file replaces atomically, so interrupted writes never leave partial JSON.
        for relative, content in outputs.items():
            target = directory / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            name = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                                 prefix=".review-", delete=False) as handle:
                    name = handle.name
                    handle.write(content)
                os.replace(name, target)
                name = None
            finally:
                if name is not None:
                    Path(name).unlink(missing_ok=True)
    except OSError as exc:
        raise ReviewError("Cannot write outputs: " + str(exc)) from exc
    return directory


def _provider(args):
    if not args.llm:
        if any(value is not None for value in (args.provider, args.model, args.roles,
                                               args.temperature, args.reasoning_effort)) or args.dry_run:
            raise ReviewError("Provider/model/role settings and --dry-run require explicit --llm opt-in.")
        return None
    temperature = args.temperature
    if temperature is None and os.environ.get("MANUSCRIPT_REVIEW_TEMPERATURE"):
        try:
            temperature = float(os.environ["MANUSCRIPT_REVIEW_TEMPERATURE"])
        except ValueError:
            raise ReviewError("MANUSCRIPT_REVIEW_TEMPERATURE must be numeric.") from None
    settings = OpenAISettings(
        model=args.model or os.environ.get("MANUSCRIPT_REVIEW_MODEL"),
        temperature=temperature,
        reasoning_effort=args.reasoning_effort or os.environ.get("MANUSCRIPT_REVIEW_REASONING_EFFORT") or None,
        max_output_tokens=args.max_output_tokens, max_request_chars=args.max_request_chars,
        timeout_seconds=args.timeout)
    return OpenAIReviewer(settings, dry_run=args.dry_run,
                          roles=[r.strip() for r in args.roles.split(",")] if args.roles else None)


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command in ("export-chatgpt", "import-chatgpt", "evaluate"):
        try:
            from .configuration import read_json
            from .exchange import read_review, export_files, import_feedback, verify_original_sources
            if args.command == "export-chatgpt":
                outputs = export_files(read_review(args.report), args.max_findings)
                inputs = [args.report]
            elif args.command == "import-chatgpt":
                original = read_review(args.report)
                verify_original_sources(original, args.manuscript, args.supplement)
                report = import_feedback(original, read_json(args.context), read_json(args.feedback), args.accept_grounded)
                outputs = {"report.json": _json(report.to_dict()), "report.md": render_markdown(report),
                           "diagnostics.json": _json(report.quality["pilot_diagnostics"])}
                inputs = [args.report, args.context, args.feedback, args.manuscript] + args.supplement
            elif args.stage == "prepare":
                from .evaluation import prepare_evaluation
                outputs = prepare_evaluation(read_review(args.baseline), read_review(args.assisted),
                                             read_json(args.expert) if args.expert else None)
                inputs = [args.baseline, args.assisted, args.expert]
            else:
                from .evaluation import score_evaluation, render_scores, apply_csv_ratings
                form_path = args.adjudication or args.bundle / "adjudication.json"
                inputs = [args.bundle / "blinded-reviews.json", args.bundle / "manuscript-context.json",
                          args.bundle / "private/key.json", form_path]
                packet, context, key, form = (read_json(path) for path in inputs)
                if args.ratings_csv:
                    form = apply_csv_ratings(form, args.ratings_csv.read_text(encoding="utf-8-sig"))
                    inputs.append(args.ratings_csv)
                result = score_evaluation(packet, context, key, form)
                outputs = {"evaluation.json": _json(result), "evaluation.md": render_scores(result)}
            directory = _save(args.out, outputs, inputs)
            print("Local output: " + str(directory))
            if args.command == "import-chatgpt":
                print("Feedback " + ("accepted where locally eligible." if args.accept_grounded else
                                     "staged for human review; new findings are not active."))
            if args.command == "evaluate" and args.stage == "score":
                print(result["outcome"])
            return 0
        except (ReviewError, OSError) as exc:
            print("Error: " + str(exc), file=__import__("sys").stderr)
            return 2
    if args.command == "list-rules":
        for kind, specs in (("reporting", CHECKS), ("pattern", PATTERNS)):
            for spec in specs:
                print("%-36s %-14s %-12s %s" % (spec.id, spec.domain, kind, spec.label))
        return 0
    if args.command == "benchmark":
        try:
            from .benchmark import evaluate
            result = _json(evaluate(args.manifest, args.reports, args.layer))
            if args.out:
                if args.out.exists():
                    raise ReviewError("Benchmark output exists; choose a new output path.")
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(result, encoding="utf-8")
                print("Benchmark: " + str(args.out.resolve()))
            else:
                print(result, end="")
            return 0
        except (ReviewError, OSError) as exc:
            print("Error: " + str(exc), file=__import__("sys").stderr)
            return 2
    if args.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        print("Error: invalid MANUSCRIPT_REVIEW_LOG_LEVEL.", file=__import__("sys").stderr)
        return 2
    logging.basicConfig(level=args.log_level, format="%(levelname)s: %(message)s")
    try:
        config = load_config(args.config or os.environ.get("MANUSCRIPT_REVIEW_CONFIG"))
        provider = _provider(args)
        paired = args.command == "compare" or bool(getattr(args, "prior", None))
        if args.prior_review and not paired:
            raise ReviewError("--prior-review requires compare or review --prior.")
        if paired and args.roles:
            raise ReviewError("Paired comparison uses one comparison reviewer; --roles applies to a single-manuscript review.")
        if args.out and args.out.exists() and not args.force:
            if any((args.out / name).exists() for name in (
                    "report.md", "report.json", "comparison.json", "comparison.md", "prior-report.json",
                    "diagnostics.json", "llm-run.json", "requests", "prompts")):
                raise ReviewError("Output exists; choose another --out or use --force. No API calls were made.")
        if args.command == "review":
            if args.prior_supplement and not args.prior:
                raise ReviewError("--prior-supplement requires --prior.")
            report, packets = review_manuscript(args.manuscript, args.supplement, args.journal, config,
                                                args.overrides, provider=None if paired else provider)
            inputs = [args.manuscript] + args.supplement
            prior = None
            if args.prior:
                prior, _ = review_manuscript(args.prior, args.prior_supplement, args.journal, config)
                inputs += [args.prior] + args.prior_supplement
        else:
            prior, _ = review_manuscript(args.old, args.old_supplement, args.journal, config, args.old_overrides)
            report, packets = review_manuscript(args.new, args.new_supplement, args.journal, config, args.new_overrides)
            inputs = [args.old, args.new] + args.old_supplement + args.new_supplement
        if prior:
            if args.prior_review:
                from .configuration import read_json
                from .models import review_from_dict
                saved = review_from_dict(read_json(args.prior_review))
                if {d.id: d.sha256 for d in saved.documents} != {d.id: d.sha256 for d in prior.documents}:
                    raise ReviewError("Saved prior review hashes do not match the supplied old manuscript and supplements.")
                fresh_sources = {b.id: (b.document_id, b.text, b.page, b.line_start, b.line_end, b.paragraph)
                                 for d in prior.documents for b in d.blocks}
                saved_sources = {b.id: (b.document_id, b.text, b.page, b.line_start, b.line_end, b.paragraph)
                                 for d in saved.documents for b in d.blocks}
                if fresh_sources != saved_sources:
                    raise ReviewError("Saved prior source blocks differ from current extraction. Regenerate the prior review before comparing.")
                prior = saved
                inputs.append(args.prior_review)
            report.comparison = compare_reviews(prior, report)
            if provider:
                from .resolution import add_semantic_comparison
                add_semantic_comparison(prior, report, report.comparison, provider)
                report.llm = provider.metadata()
            from .validation import validate_comparison
            validate_comparison(report.comparison, prior.to_dict(), report.to_dict())
        if provider:
            from .diagnostics import attach_diagnostics
            attach_diagnostics(report)
        outputs = {"report.json": _json(report.to_dict()), "report.md": render_markdown(report)}
        if prior:
            outputs.update({"prior-report.json": _json(prior.to_dict()),
                            "comparison.json": _json(report.comparison),
                            "comparison.md": render_comparison(report.comparison)})
        if args.export_prompts:
            for role, packet in packets.items():
                outputs["prompts/" + role + ".json"] = _json(packet)
        if provider:
            for item in provider.requests:
                outputs["requests/" + item["role"] + ".json"] = _json(item)
            outputs["llm-run.json"] = _json(provider.metadata())
            outputs["diagnostics.json"] = _json(report.quality["pilot_diagnostics"])
        if args.config:
            inputs.append(args.config)
        for key in ("overrides", "old_overrides", "new_overrides"):
            if getattr(args, key, None):
                inputs.append(getattr(args, key))
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        directory = _save(args.out or Path("reviews") / stamp, outputs, inputs, args.force)
        active = sum(f.disposition in ("active", "confirmed") for f in report.findings)
        print("Review complete: %d active concerns." % active)
        print("Markdown: " + str(directory / "report.md"))
        print("JSON: " + str(directory / "report.json"))
        if prior:
            print("Comparison: " + str(directory / "comparison.md"))
        if provider and provider.dry_run:
            print("Dry run: %d exact request(s) exported; no API calls made." % len(provider.requests))
        if (report.quality.get("failed_roles") or (report.comparison and
                any(report.comparison.get("llm", {}).get(k) for k in ("failed", "incomplete")))):
            print("LLM review incomplete; deterministic output preserved. Inspect warnings and llm-run.json.")
            return 3
        return 0
    except (ReviewError, OSError) as exc:
        print("Error: " + str(exc), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
