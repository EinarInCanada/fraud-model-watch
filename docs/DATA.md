# BAF acquisition and pre-fit feature contract

Source: [author BAF v2 distribution](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022).

```sh
mkdir -p data
curl -fL 'https://www.kaggle.com/api/v1/datasets/download/sgpjesus/bank-account-fraud-dataset-neurips-2022/Base.csv?datasetVersionNumber=2' -o data/base-download
unzip -l data/base-download
unzip -n data/base-download Base.csv -d data
```

The downloaded ZIP contains only Base.csv. Verified extracted size: 213427735 bytes. SHA-256:

`7bf10a37ce07e72e14c1b09e5efee3d27261baff4facc7da767b0474dcf9b809`

The loader rejects a different hash, schema, row count, invalid labels, nonfinite numerical fields, or missing months. Final-period schema/month validation is allowed; final target prevalence and prediction metrics are not printed or used for model selection.

## Source limitations

Read [author datasheet](https://github.com/feedzai/bank-account-fraud/blob/main/documents/datasheet.pdf), especially Q7, Q8, Q32, Q35, Q40 and Q44. These are CTGAN-generated applications. Mature labels are not observed label-arrival timestamps. Original feature extraction is proprietary; point-in-time correctness cannot be independently established from the release.

Datasheet hash: `367846738d63ed352183ba5e130809c8a313bd9219aa426c916ac2be709a81b0`.

The older datasheet says CC BY-NC-ND 4.0; Kaggle v2 says CC BY-NC-SA 4.0. Do not redistribute adapted data or model artifacts pending clarification. Publish independently written code and aggregate research reporting only, not individual samples. This is not a legal determination of downstream rights.

## Feature selection before fitting

Exclude fraud_bool (target), month (split only), device_fraud_count (no as-of label history), credit_risk_score (opaque preexisting model), and days_since_request (decision instant unclear). These exclusions are caution, not findings that those fields necessarily leak.

Retain other author-provided application/behavioral fields with the explicit limitation that original event-time construction cannot be reconstructed. Age, income and employment status are research predictors; no fairness or production-admissibility claim is made.

Convert documented missing sentinels only: -1 in previous/current address months, bank months, session length and device email count; all negative intended balances. Median imputation fits on training only. Other negative numbers are preserved. The CSV uses device_distinct_emails_8w where Q7 abbreviates the field name.

Categoricals: payment_type, employment_status, housing_status, source, device_os. Unknown categories map to all-zero. No row removal, resampling, class weighting or use of row positions as features.

The development baseline fits month 0 and scores reference/development months 2–5 only. At the time this contract was declared, final months 6–7 remained unscored; the subsequent primary replay has now scored them, and follow-up BAF analyses are explicitly exploratory. This differs from the authors' published split and must not be presented as directly comparable performance.
