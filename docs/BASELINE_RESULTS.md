# Initial frozen baseline — reference/development only

Dataset: BAF Base v2, **synthetic account applications**. Protocol 1.1. These are actual local measurements, not final test results or results from a bank deployment.

## Verified run

- Full-file integrity/schema validation: 1,000,000 rows, 32 columns; hash in [DATA.md](DATA.md).
- Training: month 0, 132,440 rows, 27 explicitly selected predictors.
- Logistic regression: C=1, lbfgs, no class weighting, 20 iterations, no captured warnings.
- Single-thread fit: 0.368 seconds on the local host; excludes loading, validation and scoring. This timing is machine-dependent, not a latency guarantee.
- Python 3.12.1; dependencies in requirements.txt.
- Local run: artifacts/baseline-v1.1/report.json. Stored prediction files contain source positions and scores, no targets. They are not published.

| Month | Role | Rows | Fraud labels | Review slots | Captured fraud labels | False positives | Precision@capacity | Recall@capacity | Average precision | Brier score |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | Reference | 136979 | 1198 | 1369 | 223 | 1146 | 0.162893 | 0.186144 | 0.106220 | 0.008232 |
| 3 | Development | 150936 | 1392 | 1509 | 264 | 1245 | 0.174950 | 0.189655 | 0.119565 | 0.008750 |
| 4 | Development | 127691 | 1452 | 1276 | 275 | 1001 | 0.215517 | 0.189394 | 0.134603 | 0.010524 |
| 5 | Development | 119323 | 1411 | 1193 | 272 | 921 | 0.227997 | 0.192771 | 0.140810 | 0.010840 |

## Interpretation without overclaiming

The frozen model's recall at a 1% review budget has not fallen by five percentage points from reference in these months. Thus the predefined persistence condition has no qualifying pair here; do not change its threshold to force a trigger. This table alone does not compare policy effectiveness, establish statistical equivalence, or show that retraining is unnecessary in general.

Precision rises while recall is roughly stable. Fraud prevalence also varies, so a rising precision or average precision is not by itself proof of better ranking. Brier score likewise depends on prevalence; calibration requires more analysis than this scalar.

Offline measurement is not feedback availability: month 5 labels may be read by a decision policy only at month 7 under d=1. The later replay must enforce that boundary even though these development results are now visible to the researcher. Months 6–7 have been schema-validated but not scored, summarized by target, or used to fit preprocessing.

## Reproduction

Run the README commands using the pinned file and dependencies. Existing output directories are rejected. On the same environment, compare prediction-file SHA-256 values; cross-platform floating-point changes can affect exact byte equality.

| Stored sentinel predictions | SHA-256 |
| --- | --- |
| Month 2 | a4856a578f6be192a47a61f8d3c6814850ab4e67e1744c02b9860804bb75e889 |
| Month 3 | 297a4a46007314f8908802becf8a6bb6be3db07ceb459f21eb32f21db1dfc7c4 |
| Month 4 | 6d96d2c2217cd41cfe35e93ec358616b0b8958a23fce608936bf70bea5dfa284 |
| Month 5 | 14041024120bc6fab2388de2f38d805fd2eb6fba789dd3dd4036f6d27922a21f |

The experiment does not estimate financial savings or assume that selecting a case guarantees prevention of fraud. Original dataset citation: Jesus et al., *Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets for ML Evaluation*, NeurIPS 2022; [author repository](https://github.com/feedzai/bank-account-fraud).
