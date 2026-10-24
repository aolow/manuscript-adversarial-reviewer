# MAR review and hardening — 2026-10-24

Reviewed the current engine at `112c4a2` (v0.4.0) and the separate
[`aolow/mar-skill`](https://github.com/aolow/mar-skill) at `a7f2638`.
The original local engine checkout was 13 commits behind GitHub; this work starts
from current remote main on a local `codex/review-hardening` branch. The sibling
skill checkout is also on that branch. This report records the implementation and
local validation; Git history records subsequent commits and publication.

## Findings fixed

| Priority | Finding and consequence | Fix and regression evidence |
| --- | --- | --- |
| P1 | Forced cleanup ran before input protection. A draft inside `prompts/` could be deleted; an environment-selected configuration at `diagnostics.json` could disappear. An invalid later output could also delete earlier artifacts before failing. | Validate the complete write/cleanup plan before mutation, including source symlinks, supplements, prior reviews, overrides and environment configuration. Disposable-file tests assert originals and old artifacts survive refusal. |
| P1 | OpenAI sent a strict schema whose action objects required only `kind`. That contradicts the provider's all-fields-required contract and can reject every review request. | Build a separate OpenAI schema copy requiring all object properties; nonapplicable action values remain nullable. Recursive outbound-schema and non-mutation tests preserve the local/Bedrock omission-friendly contract. |
| P2 | Output collisions, escaping symlinks and non-directory parents were sometimes detected only after model calls. A missing `jsonschema` dependency was also discovered after transport. | Preflight known destination problems and validation availability before calls. Mocked-transport tests assert zero calls for these failures. Later disk failures remain possible. |
| P2 | A malformed Bedrock `output` could escape the controlled failure path. Tool-mode parsing accepted an arbitrary tool name and ignored malformed additional tool outputs. An unhashable expert citation ID could raise an uncontrolled exception. | Validate envelope types, require exactly one output from the requested tool, and validate citation container/ID types. Boundary regressions cover each case. |
| P2 | The skill automatically used `--force`, ranked role recurrence as independent corroboration, assumed six-role completion even for paired comparison, and promoted journal expectations from model memory. | Fresh run directories; actual coverage/exclusion reporting; evidence-based prioritization; explicit paired-comparison scope; verified policy sources or an unverified label. The checklist preserves IDs, dispositions, dissent and author decisions. |
| P2 | A fully failed panel could appear as an offline audit; item exclusions were easy to miss before reading the brief. | Preview/failure/exclusion notices now appear before the revision brief. Regression tests cover failed, partially accepted, and dry-run outputs. |

The OpenAI change follows the fetched
[Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs#all-fields-must-be-required).
No live API request was used to confirm provider behavior; the contract and
transport tests are local.

## What recent research contributes

The [Virtual Biotech paper](https://doi.org/10.1126/science.aeg6779) was published
in Science in September 2026. The publisher full text was inaccessible during this
review; architectural detail was checked against the authors'
[project description](https://virtualbiotech.ai/) and the full
[February 2026 preprint](https://pmc.ncbi.nlm.nih.gov/articles/PMC12970349/), retrieved
through Europe PMC. The preprint separates specialist analyses, scientific review,
and synthesis. Its reviewer checks relevance, evidence strength and thoroughness;
the authors also warn that errors can propagate and human oversight remains needed.

The [Virtual Lab study](https://doi.org/10.1038/s41586-025-09442-9), published in July
2025, combines specialized roles, critique and human guidance in a nanobody-design
workflow with experimental testing. This is evidence about that scientific task,
not validation of manuscript-review quality.

**Adaptation implemented in the skill:** one bounded evidence challenge before
final triage. For each consequential theme, retain the claim and source evidence,
inspect counterevidence or the strongest rebuttal, state what would change the
recommendation, and propose a feasible discriminating check. Apply the same
scrutiny to strengths. A single well-supported concern can outrank several repeated
weak opinions. No new reviewer personas, automated debate rounds, literature
retrieval, or extra provider calls were added to the engine.

The skill's `references/synthesis.md` contains the reusable procedure and its
research limits. Its effectiveness remains a hypothesis. The next useful experiment
is blinded expert comparison of old and revised triage using the same manuscripts
and fixed provider outputs. Measure important correct concerns, unsupported and
missed issues, action feasibility and author usefulness. Include disagreement and
counterevidence cases. The existing evaluation CLI compares deterministic and
assisted reports; it does not yet directly score two alternative skill checklists.

## Validation

- Baseline: **223 tests passed** on current upstream engine code.
- After hardening: **238 tests passed**, including 15 new boundary/coverage tests.
- Deterministic benchmark: exact JSON equality with the checked-in baseline across
  six synthetic cases: **11 TP, 0 FP, 1 FN**, 68 unscored findings, 79/79 exact source
  grounding. The known paraphrased-leakage miss remains.
- Skill structural validator: passed. Markdown reference targets and Git whitespace
  checks passed. This is not a behavioral or scientific-quality evaluation.
- All provider responses used for validation were mocks or dry runs. No real
  manuscript was uploaded and no paid model call was made.

Writes remain atomic per file, not transactional for a whole run. Exact source
matching and heuristic grounding do not establish scientific entailment. No live
provider acceptance, blinded expert adjudication, or global skill installation
was performed during validation.

## Files changed

Engine checkout:

- `src/manuscript_review/cli.py`
- `src/manuscript_review/grounding.py`
- `src/manuscript_review/providers/bedrock.py`
- `src/manuscript_review/providers/contracts.py`
- `src/manuscript_review/providers/openai.py`
- `src/manuscript_review/reporting.py`
- `tests/test_hardening.py`
- `CHANGELOG.md`
- `DATA_SAFETY.md`
- `HARDENING_REVIEW.md`

Sibling `mar-skill` checkout:

- `SKILL.md`
- `README.md`
- `references/checklist-template.md`
- `references/roles.md`
- `references/synthesis.md`
