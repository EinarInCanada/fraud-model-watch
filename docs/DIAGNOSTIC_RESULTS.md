# Primary error, calibration, subgroup and utility diagnostics

Exploratory analysis of already-scored primary predictions. No new fit, threshold optimization or policy selection. The original manifest and every artifact hash are verified before reading aligned scores. [Complete aggregate tables](results/diagnostics.json); fixed analysis plan in [COMPLETION_PLAN.md](COMPLETION_PLAN.md).

## Paired capture and uncertainty

| Month | Captured by both | Frozen only | Scheduled only | Neither |
|---:|---:|---:|---:|---:|
| 6 | 231 | 20 | 31 | 1168 |
| 7 | 238 | 23 | 30 | 1137 |

Scheduled adds 61 positive captures but loses 43 frozen-model captures: net **18**. A 1,000-replicate, within-month paired row bootstrap (seed 20260916) gives a percentile interval of **[-1, 37]** for the captured-count difference. It includes zero: do not describe the observed gain as robust evidence of superiority. This interval conditions on fixed selections; it does not rerank, refit, account for dependence between applications, or estimate uncertainty over future months. Multinomial sampling of the {-1,0,1} row differences exactly implements this particular row bootstrap efficiently; it is not a different model-based bootstrap.

## Calibration

Ten fixed equal-width probability bins per policy/month, including empty bins as null, are published in the JSON. Boundary 1 belongs to the last bin. These are descriptive reliability tables, not recalibration fitted on the final data. Brier includes both calibration and discrimination; it is not a pure calibration measure.

| Month | Policy | Lowest bin n | Mean score | Observed positive fraction |
|---:|---|---:|---:|---:|
| 6 | frozen | 105682 | 1.127% | 0.979% |
| 6 | scheduled | 107116 | 0.658% | 1.116% |
| 7 | frozen | 95094 | 1.051% | 1.104% |
| 7 | scheduled | 95850 | 0.697% | 1.205% |

The remaining bins and their denominators must also be inspected; most observations lie in the low-score bin and sparse high-score bins cannot establish reliable calibration. No final-label calibrator is trained.

## Rounded-age subgroup review outcomes

Selections are the same **global monthly top-k**, not per-group top-k. Groups follow the authors' coarse age convention; customer age is included in the declared model features. These are synthetic cohort descriptions, not legal fairness findings or causal discrimination estimates. Differences in label prevalence, feature construction and selection mechanisms matter.

| Policy | Age | n | Positive labels | Reviewed | Captured | Recall | False-positive selection rate | Precision |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| frozen | age_lt50 | 171232 | 1889 | 932 | 209 | 11.06% | 0.43% | 22.42% |
| frozen | age_ge50 | 33779 | 989 | 1117 | 303 | 30.64% | 2.48% | 27.13% |
| scheduled | age_lt50 | 171232 | 1889 | 968 | 228 | 12.07% | 0.44% | 23.55% |
| scheduled | age_ge50 | 33779 | 989 | 1081 | 302 | 30.54% | 2.38% | 27.94% |

The net gain is not uniform: scheduled captures 19 more positive labels below age 50 and one fewer at 50+. Older-group label prevalence is 2.93% versus 1.10%; prevalence alone does not explain or justify model behavior. No fairness constraint, intervention or certification was evaluated.

## Hypothetical utility, not financial savings

All 27 policy/value/refit-cost combinations are published. Assumed values per captured positive are 1, 10, 100; refit penalties 0, 5, 50; review cost 1. Utility = V × captured − C × refits − reviewed. Refits cover the whole replay, while capture/review counts cover final months only; this is intentionally a simplified comparison, not full-lifecycle ROI.

Scheduled minus frozen equals **18V − 4C** because review counts match. Scheduled is favored only when **C < 4.5V**, tied at equality. For example V=1,C=5 gives −2 units; V=10,C=5 gives +160 units. Units are not dollars; capture is not prevented loss or even a correct human decision. Uncertainty in capture and real operational costs can reverse the preferred action.

## Reproduce

```sh
.venv/bin/python -m fraud_model_watch.diagnostics --replay artifacts/replay-v1.1 --output artifacts/diagnostics-new.json
.venv/bin/python -m unittest discover -s tests -v
```

Requires local verified Base.csv and primary replay artifacts. Published outputs contain aggregates only.
