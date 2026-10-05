# Pilot readiness: 0.3.0

The v0.2.0 architecture, deterministic catalogue/engine, and reviewer roster
remain intact. This pass adds local evaluation and exchange workflows, clearer
revision reports, targeted scientific guards, and diagnostics. It creates no
connector, service, telemetry, repository, or remote.

## What changed

- Blinded A/B review preparation, optional expert C arm, per-concern CSV/JSON
  forms, subjective issue inventory, and descriptive scoring. Partial scoring
  keeps sources blinded; completed scoring shows source-specific differences.
- A concise pilot guide covering saved V1, revision, paired comparison, and
  compact handoff. Major comparison groups distinguish persistent/unclear/new
  concerns and scope withdrawal.
- Compact export-chatgpt and import-chatgpt. Exact original sources, export
  identity/scope, schema, citations, and grounding are checked. Default imports
  stage candidates; explicit acceptance only activates locally eligible items.
- A revision brief answering the manuscript's claims, strengths, main threats,
  decisive analyses, wording changes, likely Reviewer 2 attacks, and conditional
  contribution type. Full claim details and the 20-section audit remain below.
- Diagnostics record attempted versus accepted calls, response failures and
  source-validation failures, incomplete roles, request sizes, known usage, raw
  findings, accepted/quarantined findings, duplicates, and headline counts.
  Monetary cost stays unknown without verified pricing/billing data.
- A realistically complex fictional manuscript and constructed-response tests
  for scientific failure modes, including impossible reanalysis versus a
  proposed new experiment.

## Verification

Command: .venv/bin/python -m unittest discover -s tests -t .

**182 tests passed in 4.206 seconds, with no failures or skips: 118 baseline
tests plus 64 new tests.**

| New test module | Tests |
| --- | ---: |
| test_scientific_stress.py | 19 |
| test_pilot_diagnostics.py | 9 |
| test_chatgpt_exchange.py | 14 |
| test_human_evaluation.py | 17 |
| test_pilot_workflow.py | 5 |
| Total added | 64 |

The original ingestion, rules, comparison, CLI, schema, grounding, and provider
tests remain. The new evaluation tests do not represent actual human scores.
Dependency checking reported no broken requirements. A separately installed
0.3.0 wheel passed six workflow smoke checks with network sockets blocked.
Core review, export, and evaluation require no third-party runtime dependency;
PDF and structured feedback validation keep their existing optional dependencies.

## Benchmark versus v0.2.0

The benchmark result is identical, including per-case outcomes.

| Measure | v0.2.0 | v0.3.0 |
| --- | ---: | ---: |
| Annotated issues detected | 11/12 | 11/12 |
| False positives in annotated scope | 0 | 0 |
| Known false negatives | 1 | 1 |
| Unscored findings | 68 | 68 |
| Exact source grounding | 79/79 | 79/79 |
| Annotated evidence alignment | 11/11 | 11/11 |
| Severity within annotated categories | 11/11 | 11/11 |
| Structured action completeness | 11/11 | 11/11 |

The paraphrased leakage miss is retained. These are small deterministic
regression scores, not evidence that the LLM improves scientific reviewing.
That question requires actual manuscript review and independent adjudication.

## First real pilot command

From the project root, with the manuscript saved as manuscripts/pilot-v1.pdf
and OPENAI_API_KEY plus MANUSCRIPT_REVIEW_MODEL already set privately:

    .venv/bin/manuscript-review review manuscripts/pilot-v1.pdf --llm --provider openai --out reviews/pilot-v1

This explicitly sends manuscript text and makes up to six reviewer calls.
Add --dry-run and use a different output directory to inspect requests first.
No real OpenAI manuscript command was run during this work.
See [PILOT_GUIDE.md](PILOT_GUIDE.md) for the saved-V1-to-V2 workflow.

## What to bring into ChatGPT

    .venv/bin/manuscript-review export-chatgpt reviews/pilot-v1/report.json --out handoffs/pilot-v1

Upload **handoffs/pilot-v1/chatgpt-review.json**. Paste the short instructions
from **handoffs/pilot-v1/CHATGPT_PROMPT.md**. The JSON includes the feedback schema;
there is no additional schema attachment. Keep raw requests, diagnostics, full
reports, original manuscripts, and evaluation keys locally unless you make a
separate decision to share them.

A local synthetic walkthrough is available under reviews/pilot-readiness-demo.
Its assisted output is explicitly constructed, not live model output; its human
adjudication forms are intentionally unfilled. Its ChatGPT package is 54,071 bytes.
The regenerated [example report](EXAMPLE_REPORT.md) shows the shorter opening.

## Remaining limits and recommendation

Ready for a **supervised exploratory manuscript pilot**, with a source extraction
check and human scientific adjudication. Not yet validated as scientifically
better than the deterministic baseline, and not ready for unattended reliance.

Live account/model compatibility, latency, cost, output completeness, and review
quality are untested. Scientific entailment and data-feasibility checks are
narrow heuristics, not guarantees. Novelty needs independently verified
literature; no literature retrieval is introduced. Figures, raw data/code, and
execution remain outside the validated scope.

The compact package omits context deliberately; ChatGPT must not treat omitted
methods as absent. Blinding cannot hide every stylistic cue. Important-issue
inventories and scores are subjective and can be incomplete. Paired comparison
tracks old LLM concerns but detects new concerns with the deterministic V2 audit;
it does not silently generate a new full LLM review of V2.

No live call or human evaluation occurred. No Git commit, push, publication,
remote creation, or visibility change occurred. Your next explicit opt-in
command is the authorization boundary for a real manuscript upload.

## Exact file inventory

The following inventory is relative to the project root and compares against
the captured v0.2.0 baseline. Generated local walkthrough outputs are listed
separately; build products and the virtual environment are excluded.

### Modified files (24)

- .gitignore
- ARCHITECTURE.md
- AUDIT.md
- CHANGELOG.md
- DEVELOPMENT_REPORT.md
- EXAMPLE_REPORT.md
- README.md
- SCHEMA.md
- examples/comparison.json
- examples/comparison.md
- examples/flawed-report.json
- examples/revised-report.json
- pyproject.toml
- scripts/refresh_examples.py
- src/manuscript_review/__init__.py
- src/manuscript_review/cli.py
- src/manuscript_review/comparison.py
- src/manuscript_review/grounding.py
- src/manuscript_review/pipeline.py
- src/manuscript_review/providers/openai.py
- src/manuscript_review/reporting.py
- src/manuscript_review/resolution.py
- src/manuscript_review/reviewers/__init__.py
- src/manuscript_review/reviewers/prompts/base_v2.txt

### Added files (14)

- CHATGPT_WORKFLOW.md
- EVALUATION_GUIDE.md
- HUMAN_ADJUDICATION.md
- PILOT_GUIDE.md
- PILOT_READINESS_REPORT.md
- fixtures/pilot_complex_manuscript.md
- src/manuscript_review/diagnostics.py
- src/manuscript_review/evaluation.py
- src/manuscript_review/exchange.py
- tests/test_chatgpt_exchange.py
- tests/test_human_evaluation.py
- tests/test_pilot_diagnostics.py
- tests/test_pilot_workflow.py
- tests/test_scientific_stress.py

### Local synthetic walkthrough outputs

- reviews/pilot-readiness-demo/README.md
- reviews/pilot-readiness-demo/assisted/diagnostics.json
- reviews/pilot-readiness-demo/assisted/report.json
- reviews/pilot-readiness-demo/assisted/report.md
- reviews/pilot-readiness-demo/baseline/report.json
- reviews/pilot-readiness-demo/baseline/report.md
- reviews/pilot-readiness-demo/evaluation/RUBRIC.md
- reviews/pilot-readiness-demo/evaluation/adjudication.json
- reviews/pilot-readiness-demo/evaluation/blinded-reviews.json
- reviews/pilot-readiness-demo/evaluation/blinded-reviews.md
- reviews/pilot-readiness-demo/evaluation/concern-ratings.csv
- reviews/pilot-readiness-demo/evaluation/manuscript-context.json
- reviews/pilot-readiness-demo/evaluation/private/key.json
- reviews/pilot-readiness-demo/handoff/CHATGPT_PROMPT.md
- reviews/pilot-readiness-demo/handoff/chatgpt-review.json
