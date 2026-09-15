# Experimental protocol v1.1

Pre-fit amendment: initial training uses month **0 only**, not 0–1. Under d=1, month 1 labels are unavailable at the start of reference month 2. No model was fitted or evaluation outcomes seen before this correction. Fix lbfgs, max_iter=1000, tol=1e-4, random_state=42. The feature contract is in DATA.md. Refit counts exclude the shared initial fit.

Frozen before model fitting or evaluation. Changes require a new version, rationale, and disclosure of which results have already been seen. This repository is not a formal external preregistration.

## Question and contribution

Compare **frozen**, **monthly retrained**, and **persistent-evidence-triggered** fraud models at equal monthly review capacity. The proposed extension is a reproducible persistence gate using only matured historical feedback. This is an experiment, not a claim that the gate or problem is novel. It is acceptable for the gate never to fire or for scheduled retraining to win.

## Data

- BAF Base.csv only, author distribution version 2. Synthetic bank-account applications, not real payment records or Canadian bank data.
- Author metadata checked on 2026-09-15: version 2, updated 2023-11-29; Base.csv advertised as 213,427,735 bytes. Actual checksum/schema must be recorded after acquisition.
- Kaggle metadata states CC BY-NC-SA 4.0, but the older author datasheet states CC BY-NC-ND 4.0. Keep raw/modified data and models local for non-commercial research; no redistribution clearance is claimed. Code licensing does not replace data terms.
- Month 0 through 7 is the expected temporal support; fail validation if not true. Do not invent daily timestamps, IDs identifying actual people, or label-arrival dates.
- Keep row order as a reproducible tie-break only, never as time or a model feature. Exclude month and fraud_bool from predictors. Review remaining feature meanings before training.

Sources: [author repository](https://github.com/feedzai/bank-account-fraud), [distribution](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022), [metadata endpoint](https://www.kaggle.com/api/v1/datasets/view/sgpjesus/bank-account-fraud-dataset-neurips-2022).

## Clock and split

A decision for month t occurs at its start. A label for month m is available at the start of m + 1 + d. Primary d = 1: one **complete additional month** after the event month ends. This delay is simulated and identical for positives/negatives, not observed.

- Initial training: month 0 only, available at start of month 2 under d=1.
- Month 2: initial model's held-out reference for recall at capacity. Its labels become available at start of month 4.
- Months 3–5: development replay, no final results. Fixed settings below avoid a large tuning search.
- Months 6–7: final sequential test. Save predictions and decisions before revealing their labels. Primary d = 1 means neither final month's labels may influence either final decision.
- Retraining at t uses expanding history through t - d - 1, with preprocessing fitted only on that history.
- Final two months are too short to establish long-term effectiveness. Delays d = 0 and 2 are separate, labeled sensitivity runs; d = 0 allows month 6 outcomes to affect month 7, so that is an adaptive evaluation, not an untouched two-month holdout.

## Fixed model and policies

Initial model: regularized logistic regression, C=1, no class weighting, median imputation plus standardization of numeric features, explicit categorical encoding with unknown-category handling. Pin dependencies and seed before fitting. Record convergence warnings rather than hide them. No protected-group fairness claim; report features used and later assess group error rates separately if justified.

All policies share the identical initial model, preprocessing recipe, capacity, and evaluation rows.

1. Frozen: retain initial model throughout.
2. Scheduled: refit at every decision month from 4 onward, even if historical evidence does not deteriorate.
3. Evidence-triggered: monitor the **frozen sentinel's stored predictions**, not retrospectively rescored data, so evidence remains comparable after refits. Refit only if recall@capacity in both latest consecutive matured months is at least 0.05 below month 2 reference and each month (including reference) has at least 30 fraud labels. Require a two-month cooldown after a refit. Otherwise hold, recording why. A 5-point threshold is a heuristic effect-size rule, **not statistical significance**.

Using a frozen sentinel is an explicit limitation: it may request refitting even when the currently deployed adaptive model has recovered. A future ablation may compare alternative evidence definitions, but must not silently change v1 after test outcomes are observed.

## Review capacity and scoring

Primary budget is 1% of each month's rows, k=floor(0.01*n). This is an offline monthly batch ranking, not an online queue or a claim about actual analyst throughput. Rank probability descending, breaking ties by original row position. Label values never participate in ranking.

Report n, positives, k, captured positives, false positives, precision@k, recall@k, average precision, Brier score, refit count, and measured fitting time. Undefined rates use null, not a fabricated zero. Fixed top-k makes monotone threshold changes equivalent for the same ranking; they are not a separate competing method.

Comparison uses identical final observations. Report month-specific and pooled counts rather than only an averaged percentage. If uncertainty intervals are added, name the resampling unit and independence assumptions; do not represent a row bootstrap as evidence of stability over many future months. Do not claim causal financial savings, actual prevented fraud, or correct human adjudication of every selected case.

## Acceptance and failure checks

Before training: test label timing, available training periods, future-feedback rejection, capacity/tie handling, zero-positive behavior, gate thresholds, and cooldown. Before final scoring: freeze dependency versions, data hash, feature list, model configuration, and decision/prediction artifacts. Separate final scoring from action selection.

If the data cannot support the design, record a protocol amendment before looking at final outcomes. A negative result, a non-firing gate, or indistinguishable policies is publishable; do not force an improvement by tuning on months 6–7.
