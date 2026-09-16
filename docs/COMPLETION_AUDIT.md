# Completion audit

Scope: the synthetic-data empirical research project approved after the feasibility review, including every requirement frozen in [COMPLETION_PLAN.md](COMPLETION_PLAN.md). Completion means the promised analyses and artifacts are implemented, measured and published—not that a new policy won or deployment benefit was proved.

| Requirement | Delivered evidence | Outcome |
|---|---|---|
| Feasibility, data and related-work review | FEASIBILITY.md, DATA.md | Bounded overlap review, synthetic scope, license and timing limits disclosed |
| Reproducible baseline and primary decision experiment | baseline.py, replay.py, BASELINE_RESULTS.md, RUN_RECORD.md, FINAL_RESULTS.md | Primary protocol preserved; evidence policy did not improve on frozen |
| S1 failure scenarios and S2 statistical extension | stress.py, uncertainty.py, STRESS_RESULTS.md, UNCERTAINTY_RESULTS.md | False alarms, lag, sparse-label misses and multiplicity/power tradeoff measured |
| S3 evidence-volume curves and missed changes | power.py, POWER_RESULTS.md, results/power-s3.json | All 42 cells and intervals; no solution for the four-point decline |
| Label-delay and capacity sensitivities | secondary.py, SECONDARY_RESULTS.md, results/secondary.json | Six fixed settings, four policies, available-label constraints and cached/logical fit counts |
| Simple versus more-complex model | secondary.py, SECONDARY_RESULTS.md | Fixed frozen forest versus logistic, same final observations/capacity; mixed metrics |
| Paired errors, calibration, subgroups, costs | diagnostics.py, DIAGNOSTIC_RESULTS.md, results/diagnostics.json | Overlap, bootstrap, all ten-bin tables, global-selection subgroup denominators, 27 hypothetical utility cells |
| Controlled input faults and no-data demo | faults.py, demo.py, FAULT_RESULTS.md | Eight rejections, three valid-looking accepted cases; no false drift-detection claim |
| English README, report and reproduction guide | README.md, RESEARCH_REPORT.md, REPRODUCE.md | Runnable commands, limitations, research relevance and claim boundaries |
| Tests and publication hygiene | tests/, .github/workflows/tests.yml, .gitignore | Fixture tests on Python 3.11–3.13; only code and reviewed aggregates published |

## Verification record

Verified on 2026-09-16 with Python 3.12.1 and pinned requirements, from clean implementation/documentation commit `9bc4199be40e9a1c2acded942d82fb98835168d2`:

- Full local suite: **54 tests pass**. [CI run 35156084495](https://github.com/EinarInCanada/fraud-model-watch/actions/runs/35156084495) passes on Python 3.11, 3.12 and 3.13. CI uses fixtures, not a BAF download.
- Fresh baseline under `artifacts/verification-baseline`: all four prediction hashes and all development metrics equal the original run.
- Fresh primary predict/score under `artifacts/verification-replay`: **all 18 decision JSON files and all 18 prediction CSV files have identical hashes** to the original. Monthly metrics and pooled counts match exactly; fit timings legitimately differ.
- Fresh replay manifest SHA-256: `227b8037d9ff80062ab40fe8c3a33c968f4d92fa87187030d3e0d282729864af`. It differs from the historical primary anchor because checkout identity and timings differ; the original anchor remains preserved, not replaced.
- Fresh S1, S2, S3, fault, secondary and diagnostic runs under `artifacts/verification-*` reproduce all measured aggregates. Secondary fit seconds and diagnostics' referenced replay-manifest identity are the only deliberately excluded comparisons. Secondary prediction fingerprints also match.
- Demo executed successfully: stable `[]`, abrupt `[8,10,12]`, recovery `[8]`, sparse `[]`. Full JSON trace format exercised by the fixture test.
- Every published aggregate source hash matches its source file. All local Markdown links resolve. `git diff --check` passes.
- Tracked-path inspection finds no `data/`, `artifacts/`, `models/` or `.venv/` content. A targeted credential-pattern scan finds no common AWS, Google, GitHub token or private-key pattern; this is a hygiene check, not a comprehensive security audit.
- GitHub repository visibility verified as **public**. Implementation milestones were individually committed and pushed after verification; the implementation checkout was clean for the independent replay.

The commands are documented in [REPRODUCE.md](REPRODUCE.md); use new output names on every run. Verification artifacts remain local and ignored. This audit records checks actually performed, not a promise of future validation.

## Explicitly not claimed

- No new production monitoring product, autonomous agent, dashboard, banking deployment, causal financial savings or original-algorithm priority.
- No real Canadian-bank records, observed feedback timestamps, assured upstream feature provenance, long-horizon generalization or fairness/legal certification.
- No proof that triggered retraining repairs a deteriorated model; the BAF evidence policies never fired.
- No new untouched holdout for secondary analysis; prior final labels remain consumed.
- No data-license clarification obtained, redistribution permission granted, daily automation created or synthetic contribution history manufactured.

These are documented boundaries, not silently omitted deliverables. Further production or independent-data validation is a new study, not something this evidence establishes.
