# S2: fewer false alarms, but severe small-sample loss of responsiveness

[Protocol](UNCERTAINTY_PROTOCOL.md) committed before execution; implementation commit `4c7c300`. Primary BAF and S1 results remain unchanged. This is an exploratory study of generated binomial aggregates with 500 fresh paired seeds per regime/denominator, not a trained-model comparison.

## All results

n denotes positive labels per month. The interval is a 95% exact binomial interval for the proportion of simulated runs with at least one request. It is not a guarantee for bank data or a simultaneous interval across cells. The pre/post boundary is decision month 7, when the first changed-month labels can arrive. In stable runs it is only a reporting boundary.

| n | Regime | Gate | Runs with request | Any request [95% interval] | Before 7 | From 7 | Mean requests | Conditional median first from 7 |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 30 | stable | persistence | 205/500 | 41.00% [36.65%, 45.45%] | 15.40% | 38.40% | 0.826 | 9 |
| 30 | stable | fisher_uncorrected | 10/500 | 2.00% [0.96%, 3.65%] | 0.80% | 1.60% | 0.024 | 10.5 |
| 30 | stable | fisher_bonferroni | 1/500 | 0.20% [0.01%, 1.11%] | 0.20% | 0.00% | 0.002 | — |
| 30 | persistent | persistence | 371/500 | 74.20% [70.13%, 77.98%] | 15.60% | 74.00% | 1.856 | 8 |
| 30 | persistent | fisher_uncorrected | 57/500 | 11.40% [8.75%, 14.52%] | 0.00% | 11.40% | 0.132 | 10 |
| 30 | persistent | fisher_bonferroni | 5/500 | 1.00% [0.33%, 2.32%] | 0.00% | 1.00% | 0.010 | 11 |
| 30 | transient | persistence | 220/500 | 44.00% [39.60%, 48.48%] | 16.20% | 41.20% | 0.890 | 8 |
| 30 | transient | fisher_uncorrected | 9/500 | 1.80% [0.83%, 3.39%] | 0.40% | 1.60% | 0.026 | 7 |
| 30 | transient | fisher_bonferroni | 1/500 | 0.20% [0.01%, 1.11%] | 0.00% | 0.20% | 0.002 | 7 |
| 1000 | stable | persistence | 1/500 | 0.20% [0.01%, 1.11%] | 0.20% | 0.00% | 0.002 | — |
| 1000 | stable | fisher_uncorrected | 1/500 | 0.20% [0.01%, 1.11%] | 0.20% | 0.00% | 0.002 | — |
| 1000 | stable | fisher_bonferroni | 1/500 | 0.20% [0.01%, 1.11%] | 0.20% | 0.00% | 0.002 | — |
| 1000 | persistent | persistence | 497/500 | 99.40% [98.26%, 99.88%] | 0.40% | 99.40% | 2.904 | 8 |
| 1000 | persistent | fisher_uncorrected | 497/500 | 99.40% [98.26%, 99.88%] | 0.40% | 99.40% | 2.904 | 8 |
| 1000 | persistent | fisher_bonferroni | 497/500 | 99.40% [98.26%, 99.88%] | 0.40% | 99.40% | 2.904 | 8 |
| 1000 | transient | persistence | 5/500 | 1.00% [0.33%, 2.32%] | 0.00% | 1.00% | 0.010 | 8 |
| 1000 | transient | fisher_uncorrected | 5/500 | 1.00% [0.33%, 2.32%] | 0.00% | 1.00% | 0.010 | 8 |
| 1000 | transient | fisher_bonferroni | 5/500 | 1.00% [0.33%, 2.32%] | 0.00% | 1.00% | 0.010 | 8 |

Pre/post columns overlap when a run requests in both periods. Persistent responses can include noise-induced decisions; they are not a causal attribution to change. Transient requests are not automatically false alarms.

## What changed

At n=30 under stable conditions, original persistence requested refits in 205/500 runs (41%), uncorrected Fisher in 10/500 (2%), and corrected Fisher in 1/500 (0.2%). However, under sustained decline corrected Fisher responded in only 5/500 (1%), versus 371/500 (74.2%) for persistence. The corrected gate misses almost all of these constructed small-sample changes within the observation window. Suppression of actions must not be marketed as successful risk reduction.

At n=1000 the reported summaries are identical across gates in these seeds: 1/500 stable runs requested, and 497/500 persistent runs requested. The five-point effect filter plus persistence already dominates the tested statistical thresholds here. Identical summaries do not establish identical trajectories or equivalence under other distributions.

## Interpretation

- Uncertainty control cannot manufacture information absent from sparse feedback. This conservative test has low power in the small-n regime.
- The familywise bound concerns valid null p-values within nine predeclared comparisons. It does not guarantee useful change detection, successful retraining, calibration for dependent transactions, or safety over unlimited future monitoring.
- Fisher tests a difference in capture probability, not a five-point minimum effect. That observed-effect requirement is a separate filter.
- This is established statistical machinery applied to a transparent diagnostic, not a novel statistical test.
- The uncorrected ablation has low observed alarms here, but its empirical frequency does not supply a general familywise guarantee.
- No gate is selected for deployment. Neither fewer alarms alone nor conditional detection time alone is a sufficient objective. No financial savings or final BAF improvements were measured.

## Next research question

Rather than tighten thresholds again, investigate how much mature feedback is required to detect a practically relevant change under an acceptable false-alarm budget. A prospective sample-size/power study or separately validated challenger comparison would be appropriate. It needs its own fixed design; do not tune a new rule on the already consumed BAF holdout.

## Reproduce

```sh
.venv/bin/python -m fraud_model_watch.uncertainty --output artifacts/uncertainty-s2.json
```

Existing output files are rejected. [Machine-readable aggregate results](results/uncertainty-s2.json) include source hashes, seed range and Python version. No raw BAF samples or individual predictions are included. See the protocol for generator assumptions and methodology sources.
