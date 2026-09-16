# S3: how much positive-label evidence is enough?

Aggregate-binomial diagnostics, not trained-model improvement. Design frozen in [COMPLETION_PLAN.md](COMPLETION_PLAN.md). 500 paired fresh seeds (3000–3499) per setting; seven sample sizes, three regimes, two policies. n is **positive labels per month**, not total applications. Each run samples the reference too.

## Results

Each cell is a request percentage with an exact 95% Monte Carlo interval. Stable uses any request; changed regimes use any request at decision 7 or later (not necessarily correct attribution). Conditional timing and all counts are in [the aggregate JSON](results/power-s3.json).

| n | Policy | Stable request % | Four-point response % | Eight-point response % |
|---:|---|---:|---:|---:|
| 30 | persistence | 45.0 [40.6, 49.5] | 58.6 [54.1, 63.0] | 76.6 [72.6, 80.2] |
| 30 | fisher_bonferroni | 0.2 [0.0, 1.1] | 0.6 [0.1, 1.7] | 0.4 [0.0, 1.4] |
| 60 | persistence | 39.2 [34.9, 43.6] | 62.2 [57.8, 66.5] | 80.6 [76.9, 84.0] |
| 60 | fisher_bonferroni | 0.0 [0.0, 0.7] | 1.2 [0.4, 2.6] | 4.8 [3.1, 7.1] |
| 100 | persistence | 30.6 [26.6, 34.8] | 57.2 [52.7, 61.6] | 87.4 [84.2, 90.2] |
| 100 | fisher_bonferroni | 0.2 [0.0, 1.1] | 1.4 [0.6, 2.9] | 12.4 [9.6, 15.6] |
| 200 | persistence | 14.4 [11.4, 17.8] | 54.2 [49.7, 58.6] | 89.4 [86.4, 92.0] |
| 200 | fisher_bonferroni | 0.2 [0.0, 1.1] | 5.0 [3.3, 7.3] | 36.4 [32.2, 40.8] |
| 400 | persistence | 3.6 [2.1, 5.6] | 44.2 [39.8, 48.7] | 94.2 [91.8, 96.1] |
| 400 | fisher_bonferroni | 0.2 [0.0, 1.1] | 13.0 [10.2, 16.3] | 79.0 [75.2, 82.5] |
| 800 | persistence | 0.0 [0.0, 0.7] | 41.2 [36.8, 45.7] | 99.2 [98.0, 99.8] |
| 800 | fisher_bonferroni | 0.0 [0.0, 0.7] | 39.8 [35.5, 44.2] | 99.2 [98.0, 99.8] |
| 1600 | persistence | 0.0 [0.0, 0.7] | 27.4 [23.5, 31.5] | 99.6 [98.6, 100.0] |
| 1600 | fisher_bonferroni | 0.0 [0.0, 0.7] | 27.4 [23.5, 31.5] | 99.6 [98.6, 100.0] |

## Interpretation and limits

- For an eight-percentage-point persistent decline, the first tested n meeting >=80% response and <=5% stable requests **by point estimate** is 400 for persistence and 800 for the corrected Fisher gate. This is not certification, optimality, interpolation, or production sample-size advice.
- Neither policy meets both criteria for the four-point decline at any tested n. The gate still requires an observed five-point drop: a true four-point decline conflicts with that effect-size filter. More evidence does not repair an incompatible decision rule.
- Fisher filtering trades sparse-data false alarms for missed changes. Keep both the original and corrected policy results; no winner was selected.
- Intervals quantify simulation uncertainty at each setting, not simultaneous coverage across the grid, uncertainty about a real bank, or model-retraining benefit. Independent binomial observations, constant positive-label volume, a fixed reference and horizon, and prescribed changes are strong simplifications.
- Stable runs have a nominal decision-7 split solely for comparable reporting; there is no actual change. Timing is conditional on responding; never interpret it as speed across all runs.

## Reproduce

```sh
.venv/bin/python -m fraud_model_watch.power --output artifacts/power-s3-new.json
.venv/bin/python -m unittest discover -s tests -v
```

No BAF download needed. Results record source hashes and runtime versions. The full 42-row aggregate file contains no individual applications or predictions.
