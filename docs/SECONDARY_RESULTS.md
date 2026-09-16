# Secondary BAF analyses: delay, capacity and complexity

All analyses are **exploratory**: primary months 6–7 had already been scored. Settings were fixed in [COMPLETION_PLAN.md](COMPLETION_PLAN.md) before these runs. This is not a fresh holdout or a policy-selection exercise. [Full aggregate results and decision traces](results/secondary.json).

## Delay and capacity

All settings score 205,011 synthetic applications with 2,878 positive labels. Both evidence policies made zero refit requests in every setting and therefore equal the frozen model. Counts are positive labels selected, not prevented fraud.

| Additional delay | Capacity | Reviewed | Frozen / both evidence | Scheduled | Scheduled logical refits |
|---:|---:|---:|---:|---:|---:|
| 0 | 1% | 2049 | 512 | 521 | 5 |
| 1 | 1% | 2049 | 512 | 530 | 4 |
| 2 | 1% | 2049 | 512 | 523 | 3 |
| 1 | 0.5% | 1024 | 334 | 336 | 4 |
| 1 | 2% | 4099 | 787 | 811 | 4 |
| 1 | 5% | 10250 | 1317 | 1341 | 4 |

Labels from event month m become available at m+1+d. Reference month is d+1, trained only on month 0. Scheduled refits begin at reference+2. With d=0 the month-7 fit uses month-6 labels: this is explicitly an **adaptive** evaluation. Delay changes reference, warmup and training availability, so this is not an isolated causal effect of faster feedback. More recent data did not monotonically improve capture. With d=2 the reference is month 3, avoiding the unavailable-label error of using month 2.

Capacity increases capture but requires more review and lowers precision; it is not free model improvement. At d=1 the scheduled-minus-frozen gain ranges from 2 at 0.5% capacity to 24 at 2% and 5%. Changing capacity also recalculates reference/history recalls. No configuration was selected for deployment.

The primary d=1, 1% setting reproduces the primary 512 versus 530 counts. Each fit is cached by model kind and training months: six logistic fits and one forest fit were physically computed, with zero recorded warnings. Logical policy refits count actions, not cache misses. Timing is machine-specific and is not a deployment-cost estimate. Both evidence gates use frozen-model sentinel feedback; the extension retains alpha/9 but makes **no inferential guarantee** under BAF dependence or adaptive training.

## One fixed model-complexity comparison

Same month-0 training, preprocessing, feature contract, observations and 1% capacity. Random forest: 100 trees, depth 8, minimum leaf 20, seed 42, one thread, no class weights. No tuning or claim this is an optimal forest.

| Model | Month | Captured | Average precision | Brier score (lower better) |
|---|---:|---:|---:|---:|
| logistic | 6 | 251 | 0.136210 | 0.012297 |
| logistic | 7 | 261 | 0.175838 | 0.013282 |
| forest | 6 | 255 | 0.141600 | 0.012537 |
| forest | 7 | 278 | 0.173904 | 0.013698 |

The frozen forest captures 533 positive labels versus 512 for frozen logistic regression at the same 2,049 reviews. But its Brier score is worse in both months, and month-7 average precision is slightly lower. More complexity helps one operating-point metric, not every metric. A forest retraining policy and repeated model-seed uncertainty were not evaluated.

## Reproduce

```sh
.venv/bin/python -m fraud_model_watch.secondary --output artifacts/secondary-new.json
.venv/bin/python -m unittest discover -s tests -v
```

Requires the locally acquired, checksum-verified Base.csv; it is not redistributed. The report records data/source hashes, versions, warning logs, fit costs, all decision traces and aggregate metrics. Training labels and feedback are maturity-checked; tests perturb unavailable labels and confirm unchanged decisions and prediction hashes for d>=1. Unlike the primary replay, secondary decisions are recorded in the final aggregate report, not an independently anchored pre-scoring manifest.
