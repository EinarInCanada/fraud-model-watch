# Gate diagnostic protocol S1

Declared after the primary BAF result, before executing this diagnostic suite. The primary result and gate remain unchanged. This is **post-primary exploratory mechanism analysis**, not another untouched BAF test or evidence of bank utility.

## Failure hypothesis

The primary gate responds to a sustained drop relative to a fixed sentinel reference, not to the potential benefit of retraining. Stable performance can coexist with a better available model. A non-firing gate is therefore not necessarily a software error. We will diagnose its timing, noise sensitivity and abstention behavior before considering a new policy.

## Deterministic fixtures

Generate aggregate monthly counts, not transactions or fitted-model predictions. Reference is month 2, 1000 positives, 200 captured (20%). Subsequent months are 3–11; decisions occur at starts of 4–13 with d=1. Each decision receives only matured counts. Requests update a two-month cooldown but **do not change the sentinel or simulate successful retraining**.

Scenarios (monthly captured positives per 1000):

- Stable: 200 throughout.
- Abrupt persistent: 200 before month 5, then 120.
- One-month shock: 120 only in month 5, otherwise 200.
- Gradual: months 3–11 = 200, 180, 160, 140, 120, 100, 100, 100, 100.
- Exact boundary: 150 from month 5 onward.
- Recovery: 120 in months 5–6, then 200. Delayed feedback may request a refit after recovery already happened.
- Sparse positives: reference 6/30, subsequent 2/25. Shows insufficient denominator even with large constructed decline. Pre-execution correction: the earlier 5/25 specification equaled the 20% reference and did not encode a decline; corrected before the Monte Carlo run, not in response to its results.
- Missing feedback: abrupt persistent scenario with months 6, 8 and 10 omitted. Shows how requiring consecutive calendar months can prevent action.

Report first request, request count, reason trace and observed-month provenance. These are gate behavior checks, not detection accuracy on fraud data.

## One-factor ablation and Monte Carlo

Compare the unchanged two-month gate to an explicitly separate **one-month** ablation. Keep 5-percentage-point threshold, at least 30 positives and two-month cooldown identical. Do not select a winner by adjusting these settings.

- 200 seeds (0–199), paired observations for both gates.
- Binomial captured counts conditional on fixed positive counts; n=30 and n=1000, analyzed separately.
- Reference true capture probability 0.20, sampled independently with the same n.
- Stable probability 0.20; persistent change to 0.12 from month 5; transient change to 0.12 only in month 5.
- Event months 2–11, decisions 4–13, d=1. Synthetic series have no model-training phase.
- Use standard-library Random with seed = seed + 10000*n + 100000000*regime_index, with regimes stable, persistent, transient in that order. Record Python version.
- Report fraction of runs with any request, pre-change requests (decision < 7), fraction with any request from decision 7 onward, mean request count, and median first post-change request month conditional on a request. Use null when absent.
- Under stable conditions, any request is a false alarm relative to the constructed constant probability. Under transient conditions a request is a response to a real brief change, not automatically a false alarm.

No superiority or statistical significance claim. Captured-count binomial sampling ignores review-capacity coupling, transaction dependence, changing prevalence and correlated errors. The experiment probes a gate in isolation; it is not an end-to-end fraud simulation. The missing-feedback scenario tests missing monthly aggregates, not selective label bias. Binomial n=30 tests sparse evidence; it does not establish calibration of uncertainty.

## Exit and interpretation

Publish every scenario and both denominators. Do not modify the main policy from these results alone. If persistence trades noise suppression for late/missed responses, report that tradeoff. An improved policy would need a new protocol and independent test design. No final BAF labels are loaded by this suite; no learned model is trained or updated.
