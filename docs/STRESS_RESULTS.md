# S1: persistence reduces reactions, but does not calibrate uncertainty

Exploratory diagnostic run following [the declared S1 protocol](STRESS_PROTOCOL.md). Code was committed as `ef61696` before executing the complete suite. These are generated aggregate counts, **not BAF transactions or an end-to-end retraining experiment**. No primary model, threshold, or BAF outcome was changed.

## Why the primary gate stayed inactive

The BAF reference recall was about 18.6144%; the fixed 5-point rule therefore required two qualifying months at or below about 13.6144%. Development recalls were roughly 18.97%, 18.94%, and 19.28%, above the reference. The gate correctly followed its specification. That specification tests degradation, not whether a fresh model might improve capture. Thus the primary result is a limitation of the decision criterion, not evidence of a broken trigger implementation.

## Deterministic traces

Numbers below are **decision months** requesting refits. Labels from event month m arrive at decision m+2. Requests do not actually refit a model or alter the fixed sentinel in this diagnostic.

| Scenario | Two-month gate | One-month ablation |
| --- | --- | --- |
| Stable | None | None |
| Abrupt persistent drop at month 5 | 8, 10, 12 | 7, 9, 11, 13 |
| One-month shock at month 5 | None | 7 |
| Gradual drop | 9, 11, 13 | 8, 10, 12 |
| Exact 5-point boundary from month 5 | 8, 10, 12 | 7, 9, 11, 13 |
| Drop in months 5–6, recovered at 7 | 8 | 7 |
| Fewer than 30 monthly positive labels | None | None |
| Missing alternating monthly feedback | None | 7, 9, 11, 13 |

Recovery can precede a request because feedback is delayed. A missing month is not a healthy month: requiring consecutive calendar evidence can leave the gate inactive despite a continuing decline. Repeated requests under sustained decline reflect the fixed sentinel plus cooldown, not demonstrated failures of successive trained models.

## All Monte Carlo results

Each row uses 200 paired seeds for the two policies. Reference and later captured counts are sampled binomially. n is the number of positive labels per month, not all applications. Stable p=0.20; persistent p=0.12 from month 5; transient p=0.12 only at month 5. Observed counts contain sampling noise around those probabilities.

| n | Regime | Gate | Any request | Request before decision 7 | Request from decision 7 | Mean requests | Median first request from 7, conditional |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 30 | Stable | Two-month | 45.0% | 17.5% | 43.5% | 0.950 | 8 |
| 30 | Stable | One-month | 75.5% | 46.0% | 72.0% | 2.045 | 8 |
| 30 | Persistent | Two-month | 76.5% | 16.0% | 76.5% | 1.875 | 8 |
| 30 | Persistent | One-month | 91.5% | 47.5% | 90.5% | 3.110 | 7 |
| 30 | Transient | Two-month | 46.0% | 15.5% | 42.5% | 0.940 | 8 |
| 30 | Transient | One-month | 78.5% | 42.5% | 77.5% | 2.025 | 7 |
| 1000 | Stable | Two-month | 0.0% | 0.0% | 0.0% | 0.000 | — |
| 1000 | Stable | One-month | 2.0% | 0.5% | 2.0% | 0.025 | 7.5 |
| 1000 | Persistent | Two-month | 100.0% | 0.0% | 100.0% | 2.940 | 8 |
| 1000 | Persistent | One-month | 100.0% | 1.0% | 100.0% | 3.900 | 7 |
| 1000 | Transient | Two-month | 0.0% | 0.0% | 0.0% | 0.000 | — |
| 1000 | Transient | One-month | 96.0% | 0.5% | 96.0% | 0.970 | 7 |

Before/after fractions may overlap because the same run can request in both periods. Stable rows have no actual change; decision 7 is just the shared reporting boundary. Their any-request rate is a run-level false-alarm frequency over the full horizon, not a per-decision error probability. A transient response is not automatically an error: it responds to a real, short constructed dip.

## Conclusions and limits

1. **A 30-positive floor is not enough to establish reliability.** Under stable n=30 conditions, 90 of 200 two-month runs requested a refit despite constant true capture probability. The noisy fixed reference is reused across decisions, creating dependence between comparisons.
2. **Persistence introduces a tradeoff.** It suppressed the high-n transient response but delayed the persistent response by one decision month in the deterministic case. A policy's value depends on the cost of delay and of unnecessary intervention, neither measured here.
3. **Zero observed alarms is not zero underlying risk.** The n=1000 result is only 200 simulated trajectories under specific assumptions. It cannot certify an operational false-alarm guarantee.
4. **No improved policy has been validated.** This suite does not simulate training gains, analyst queues, selective label availability, or financial costs. Binomial aggregates ignore review-capacity coupling and transaction dependence. The primary study remains negative for the proposed extension.

Next candidate, not yet implemented: an uncertainty-aware or challenger-based decision rule with an explicit false-alarm budget, a declared comparison horizon and a separate validation design. Do not tune it on the consumed BAF final months. Any adaptive comparisons must account for repeatedly checking the same reference rather than treating each check as independent.

## Reproduction

```sh
.venv/bin/python -m fraud_model_watch.stress --output artifacts/stress-s1.json
```

The suite uses only the standard library and can also run with a compatible system Python. It rejects an existing output file. Full traces, source hashes and Python version are stored locally. No BAF download or model fitting is required. Main implementation tests now total 32, including delayed-feedback, recovery, missing-evidence and ablation checks.
