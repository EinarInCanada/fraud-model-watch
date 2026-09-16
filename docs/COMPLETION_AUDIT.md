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

Final reproduction and publication checks are recorded below after execution. No incomplete or pending check should be interpreted as passing.

## Explicitly not claimed

- No new production monitoring product, autonomous agent, dashboard, banking deployment, causal financial savings or original-algorithm priority.
- No real Canadian-bank records, observed feedback timestamps, assured upstream feature provenance, long-horizon generalization or fairness/legal certification.
- No proof that triggered retraining repairs a deteriorated model; the BAF evidence policies never fired.
- No new untouched holdout for secondary analysis; prior final labels remain consumed.
- No data-license clarification obtained, redistribution permission granted, daily automation created or synthetic contribution history manufactured.

These are documented boundaries, not silently omitted deliverables. Further production or independent-data validation is a new study, not something this evidence establishes.
