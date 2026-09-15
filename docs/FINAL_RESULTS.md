# Primary experiment: no demonstrated advantage for the evidence gate

Protocol 1.1; synthetic BAF Base v2; held-out months 6 and 7. Prediction code was committed before generating final predictions, and the [manifest anchor](RUN_RECORD.md) was pushed before the separate scoring command. No hyperparameters or trigger thresholds were changed after viewing final outcomes.

## Main result

All policies processed the same 205,011 applications containing 2,878 positive labels, with 2,049 review slots total (1% rounded down independently each month).

| Policy | Captured fraud labels | False positives in review | Precision@capacity | Recall@capacity | Refits over months 4–7 | Refit seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen | 512 | 1537 | 24.9878% | 17.7901% | 0 | 0 |
| Monthly scheduled | 530 | 1519 | 25.8663% | 18.4156% | 4 | 6.314 |
| Persistent-evidence gate | 512 | 1537 | 24.9878% | 17.7901% | 0 | 0 |

Scheduled retraining captured **18 more positive labels**, a **0.6254 percentage-point** absolute increase in pooled recall. The evidence gate never triggered, so it retained exactly the frozen model. This does **not** demonstrate that the proposed gate improves fraud detection or makes better adaptation decisions.

Fit times include preprocessing and estimator fitting, exclude file loading/scoring, and are machine-dependent single-thread measurements. The shared initial fit took 0.304 seconds and is excluded from all refit totals. Four refits span development and final replay, not four fits within the two final months. Total refit compute was small: do not translate avoiding it into a material business saving.

## Monthly detail

| Month | Policy | Positive labels | Review slots | Captured | False positives | Average precision | Brier score |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | Frozen / evidence | 1450 | 1081 | 251 | 830 | 0.136210 | 0.012297 |
| 6 | Scheduled | 1450 | 1081 | 262 | 819 | 0.144196 | 0.012383 |
| 7 | Frozen / evidence | 1428 | 968 | 261 | 707 | 0.175838 | 0.013282 |
| 7 | Scheduled | 1428 | 968 | 268 | 700 | 0.181298 | 0.013446 |

Scheduled ranking metrics improve descriptively, while Brier score is slightly worse in both months. Better ranking at fixed capacity does not imply better probability quality. No significance test, confidence interval, production validation, or causal financial-impact estimate is claimed.

## What the experiment actually establishes

- A reproducible decision/review evaluation on a fixed synthetic benchmark with explicit delayed-label assumptions.
- The declared degradation gate remains inactive on this trajectory; these observations cannot validate its behavior after a real trigger.
- In this run, periodic retraining improves captured labels relative to the other two strategies. The gate watches degradation, not the potential benefit of refitting, so it can miss an opportunity even when performance looks stable.
- The control flow protects final outcomes from fitting/decision logic: changing final labels in integration tests leaves decisions and predictions unchanged. This is a software check, not proof that all source features are point-in-time correct.

## Limitations and next decisions

Only two held-out months, one synthetic dataset, one linear model, one capacity and one simulated delay were evaluated. Protected attributes were retained for research; subgroup effects are not yet assessed. Final labels have now been seen: any changed rule evaluated on the same months is exploratory, not a fresh confirmatory test.

Do not reduce the 5-point threshold after seeing these results just to produce a favorable outcome. A useful next step is a **separately declared diagnostic study** of smaller/gradual changes, limited feedback and gate firing, with ablations on development data or an independently frozen test. Treat source-related BAF variants as related stress conditions, not independent real-bank replications. A two-month delay requires a revised initial/reference calendar before it can be tested.

## Reproduce

Use README setup and DATA.md acquisition. Run `fraud_model_watch.replay predict` followed by `fraud_model_watch.replay score` in a new local artifact directory. The score stage checks file/source hashes and source-row alignment. No individual application data or predictions are redistributed.

Measured run manifest SHA-256: `bd91b3d41382cb0c475abba07b480fd2403768a22e1f319e042f6b02296b42ac`.

Source attribution: Jesus et al., *Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets for ML Evaluation*, NeurIPS 2022; [author repository](https://github.com/feedzai/bank-account-fraud). Dataset rights remain separate from MIT-licensed project code; see DATA.md for the license discrepancy.
