# Self-audit: version 0.3.0

Pilot readiness was added on top of the stable v0.2.0 implementation. The full
suite passed: **182 tests, zero failures or skips, in 4.206 seconds**. This retains
all 118 baseline tests and adds 64 for scientific failure modes, diagnostics,
blinded adjudication, ChatGPT exchange, and the pilot workflow.

The original synthetic benchmark is identical to v0.2.0, including the known
paraphrase miss: 11 true positives, 0 scoped false positives, 1 false negative,
68 unscored findings, and 79/79 exact source matches. No live LLM performance
or independently adjudicated scientific-quality result is claimed.

The 0.3.0 wheel built and installed in a separate temporary location. Six
network-blocked portable workflow checks passed: core review, six-role dry run,
compact export, blinded evaluation preparation, CSV scoring, and staged feedback
import. Core review, export, and evaluation also worked without site packages.
The package contains the same four schemas and 13 prompts. Dependency checking
reported no broken requirements.

The realistic fictional fixture exercises design ambiguity, indirect leakage,
subject/specimen/cell units, reference and annotation dependence, rediscovery,
post-selection inference, missing controls, and unavailable modalities. All
model outputs in tests and the walkthrough were constructed locally.
The walkthrough leaves adjudication forms blank.

Narrow support/feasibility heuristics can still miss unsupported criticism or
quarantine valid advice. Blinding can be weakened by wording and review length.
Human ratings are subjective; experts are comparison arms, not answer keys.
Scientific improvement over the baseline remains an empirical question for
the first authorized pilot.

No real manuscript upload, live OpenAI review, telemetry, connector, Git commit,
remote, push, publication, or visibility change occurred.
See [PILOT_READINESS_REPORT.md](PILOT_READINESS_REPORT.md) for exact files and
the recommendation, and [PILOT_GUIDE.md](PILOT_GUIDE.md) to run a pilot.

---

# Archived audit: version 0.2.0

The existing implementation was extended in place. All 54 baseline tests remain,
with 64 additional tests: **118 passed, zero failures and zero skips**, in
2.749 seconds on the final complete suite run. The rule catalogue, rule engine,
extraction, prioritization, configuration, and existing rule/ingestion/CLI tests
retain their baseline file hashes. No baseline source file was removed.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -t .
.venv/bin/python -m pip check
```

The dependency check reported no broken requirements. Verification used Python
3.9.6, pypdf 6.19.0, and jsonschema 4.25.1. Tests cover actual synthetic PDF/DOCX
ingestion, the original rules and overrides, strict response schemas, exact
request exports, explicit API opt-in, mocked response handling, grounded and
ungrounded findings, duplicate/severity conflicts, source locations, six-state
version assessments, and imported prior-review integrity.

The 0.2.0 wheel was built using isolated declared build dependencies, installed
offline into a temporary directory, and imported from that installation while
running outside the checkout. Three network-blocked smoke checks passed:

- Core Markdown review with Python site packages disabled.
- Six-role LLM dry run without an API key.
- One-request paired dry run importing a saved prior review.

The wheel contains all four JSON Schemas and 13 prompt files. An initial attempt
to build without isolation failed because the environment lacked the wheel
build command; the normal isolated build succeeded. No runtime dependency was
added to the deterministic core.

Source, fixtures, examples, configuration, and current instructions were scanned
for machine-specific user paths and API-key patterns; none were found. This is
a narrow static check, not a comprehensive secret scan. Outputs and private
input directories are ignored. No Git repository or remote was created, and
nothing was published or committed.

## Evidence and model boundaries

OpenAI requests are explicitly opt-in and are never made by the benchmark.
All provider testing used mocked responses or dry runs. **No live manuscript
review, model-quality evaluation, or account/model compatibility test occurred.**
Official API documentation was consulted during development; scientific
literature and journal policies were not retrieved.

Only existing source block IDs and exact, unique excerpts are accepted.
Locations are derived locally. Invalid quotes, locations, response schemas,
claim links, and source tampering have regression tests. Heuristic support
checks quarantine several forms of unsupported inference or certainty, while
external claims remain unverified. Exact quotation still does not prove that
the interpretation follows from the evidence.

The report caps headline concerns at seven without padding, distinguishes
ranked claim analysis from the original extraction candidates, and preserves
all 20 detailed audit sections. Duplicates preserve their original reviewer
ratings; conflicts are flagged. Paired comparison retains every active prior
issue and does not treat softer wording as a repaired persistent design flaw.
Neither newly described methods nor an LLM resolution verifies execution.

## Benchmark result and limits

The [six-case benchmark](benchmarks/README.md) detects **11/12** annotated issues:
0 scoped false positives, 1 false negative, and 68 unscored findings outside
the declared issue families. Exact grounding is 79/79. For the 11 detected
annotated issues, expected-phrase alignment, acceptable severity, and structured
action completeness are each 11/11.

These are deterministic regression scores. The annotations are author-designed,
not independently expert-validated. The known paraphrased-leakage miss remains.
Unscored reporting flags can be irrelevant; complete action fields can still
contain weak recommendations. No expert-level accuracy or LLM performance is
claimed. Saved LLM reports can be scored separately after an authorized run.

Remaining gaps include fallible semantic support checking, no figures/OCR or raw
data/code execution, no verified literature novelty, incomplete cohort identity
resolution, no exact dollar budget, and no live API compatibility verification.
Rejected API responses may still incur charges; accepted-call receipts are not
a billing ledger. API `store=false` is not a zero-retention guarantee.

The next evidence-producing step is an explicitly authorized synthetic model
pilot followed by independent scientific adjudication. Real manuscript uploads
require the user's explicit opt-in command. Remote creation, publication, and
visibility changes remain unapproved.

See [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md) for the file inventory,
architecture, commands, roles, and completion details.

---

# Archived audit: version 0.1.0

The remainder records the original baseline. Its limitations and next-build
recommendations describe version 0.1.0, not the current implementation.

The repository began empty. All five requested phases were completed: design,
ingestion/schema/rules/CLI, reviewer routing/reporting, version comparison, and
fixture execution with a false-positive audit.

## Verified behavior

- A fresh Python 3.9 virtual environment successfully installed the editable
  package and optional PDF reader. The system's old pip required upgrading;
  the installation instructions include that step.
- The installed CLI generated both manuscript reviews, a version comparison,
  and all eight local prompt packets.
- 54 tests pass, including actual PDF text extraction, DOCX paragraph/table
  reading, malformed inputs, protected output behavior, supplements, overrides,
  reviewer-provider citation validation, and end-to-end CLI execution.
- Generated reports and saved examples pass the shipped draft-2020-12 JSON
  schemas using the independent jsonschema validator.
- Runtime provenance checks verify every quote against an exact source span.
- Dependency checking reported no broken requirements.

Verification used Python 3.9.6, pypdf 6.19.0, and jsonschema 4.25.1 in the local
virtual environment. The core was also tested without installation through
PYTHONPATH. This is a software fixture audit, not a scientific performance
benchmark or validation on real manuscripts.

## Synthetic fixture result

| Observation | Count |
| --- | ---: |
| Flawed-manuscript findings | 44 |
| Revised-manuscript findings | 20 |
| New affirmative reporting cues | 16 |
| Candidate design remediations | 5 |
| Concerns still detected | 20 |
| Disappearing concerns without resolution evidence | 3 |
| Newly detected concerns | 0 |
| Matched claims with more qualified wording | 3 |

The planted feature-selection leakage, test-set tuning, cohort reuse,
cell-level pseudoreplication, circular signature validation, causal/conservation
overclaims, novelty overstatement, missing intervals, and multiplicity reporting
gap are detected. Explicit condition-platform alignment is also flagged.

The revised fixture remains confounded by platform and response. Acknowledging
that problem improves reporting but does not resolve the scientific concern.
Future calibration, subgroup, and utility analyses do not count as completed.
The reduced finding count is not a validity score.

## False positives found and corrected

| Failure mode | Current guard and regression evidence |
| --- | --- |
| Reference titles count as methods | References excluded from extraction/rules |
| Future validation or calibration counts as completed | Future-work and pending-analysis phrases guarded |
| Negated leakage counts as a disclosed defect | Clause-scoped negation checks |
| Negation in an unrelated clause suppresses an actual reported method | Semicolon/contrast boundaries |
| Internal held-out data counts as external validation | External or explicitly independent cohort/dataset cues required |
| Independent marker genes count as an independent cohort | Independent-cohort cue narrowed |
| Literature-prespecified features imply selection leakage | Prespecified/external-reference guard |
| Unknown feature-selection provenance is treated as established | Downgraded to a plausible issue |
| Omitted or explicitly missing intervals count as reported | Negative reporting guard |
| No detected doublets or missing values imply missing QC | Negative-result exceptions |
| Limitations expressed as "cannot establish" are ignored | Limitation-specific handling |
| Stated confounding disappears once acknowledged | Separate design concern survives reporting acknowledgment |
| A deleted problematic sentence counts as resolution | Separate no-longer-detected classification |
| Negated remediation counts as a fix | Positive-statement requirement |
| Old manual decisions silently carry across versions | All document hashes must match |

## Remaining weaknesses

1. **Language coverage is narrow.** Paraphrases such as "the discovery-derived
   marker panel preceded partitioning" can evade the leakage rule. Complex
   nested negation, reported speech, conditional clauses, tables, and
   cross-sentence relationships can also mislead it.
2. **Mention is not adequacy.** The presence of "FDR", "calibration", or
   "independent cohort" cannot establish a correct implementation. The tool does
   not inspect raw data, cohort overlap, fold contents, model code, or assay QC.
3. **Applicability can be broad.** A survival or single-cell mention can activate
   checks that are irrelevant to the primary question. Use domain/rule controls
   or reasoned, version-bound overrides.
4. **Concern families aggregate instances.** Up to eight evidence spans are
   displayed per rule. A family remaining active does not say which individual
   experiments were repaired.
5. **Cohort/claim extraction is shallow.** Mentions are not deduplicated cohort
   identities, central contribution ranking, or verified claim support.
   Figure links only connect explicit shared labels.
6. **Document structure can be incomplete.** No OCR or visual interpretation
   is provided. PDF columns and reading order can be wrong. DOCX extraction
   omits footnotes, comments, headers, equations, and images; tracked insertions
   are included and deletions excluded.
7. **Reviewer roles are not LLM reviews.** Offline output routes existing
   findings. The optional provider interface validates citation locations,
   not the semantic truth of generated concerns; no live provider was tested.
8. **Version conclusions remain conditional.** Wording changes and newly
   reported methods do not prove analyses were rerun or scientific rigor improved.
9. **No external verification.** Novelty, journal scope, accessible repositories,
   clinical utility, and mechanistic conservation require additional evidence.
10. **Not hardened for hostile inputs.** Resource limits help ordinary local
    use but do not isolate PDF parsers. Output is atomic per file, not per run.

The PDF limitation is consistent with the
[pypdf text-extraction documentation](https://pypdf.readthedocs.io/en/5.7.0/user/extract-text.html):
the reader extracts text and does not perform OCR.

## Recommended next build

Start with expert-labeled passages from real manuscripts, including deliberately
safe controls and methods in supplements. Measure precision/recall separately
for explicit design defects and reporting gaps. Improve cohort identity and
scope-aware extraction, then add an opt-in LLM adapter with budget controls,
semantic citation checks, and human confirmation of consequential judgments.
Add figure/table interpretation and a lightweight UI after those foundations.
