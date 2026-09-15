# Feasibility and overlap review

Review date: 2026-09-15. This is a bounded first-pass review, not an exhaustive novelty search or a reproduced benchmark.

## Decision

**Hold implementation of the broad fraud-monitoring product.** Existing work already covers substantial parts of temporal validation, delayed labels, adaptation decisions, and capacity-constrained review. No claim of an unserved market or a novel algorithm is supported.

There is a feasible alternative: an independently reproducible comparative study of decision policies on synthetic bank-account applications. That changes both the data provenance and the task from real payment transactions. Obtain a scope decision before downloading data or training models.

## Dataset screen

| Candidate | Verified source characteristics | Limitation for this project | Decision |
| --- | --- | --- | --- |
| ULB/Worldline credit-card data | Public anonymized transaction dataset; short two-day observation window; final fraud labels and elapsed-time field | Cannot establish long-term degradation; no observed label-arrival timeline established in this review; repeated monitoring windows would not create new independent months | Not the main temporal benchmark |
| Feedzai BAF | Six synthetic account-opening fraud datasets generated from a real-world source; one million rows per variant; month field; author distribution lists CC BY-NC-SA 4.0 | Applications, not payments; month granularity cannot justify daily review throughput; synthetic provenance; actual label-arrival times not established | Candidate for non-commercial monthly study only |
| Fraud Detection Handbook simulator | Explicitly simulated transactions; reproducible generation and temporal evaluation with a modeled feedback delay | Known simulated dynamics are useful for tests, not evidence of bank deployment benefit; baseline methodology already exists | Reuse/reference for methodology and fault fixtures, not a novelty claim |
| FiFAR / OpenL2D | Synthetic fraud analyst predictions and capacity-aware deferral experiments; older FiFAR repository directs users to an upgraded release | Expert decisions are synthetic, not actual analyst outcomes; this is already a research benchmark for capacity-constrained review | Related work, not a new project concept |

BAF's non-commercial/share-alike terms are not an MIT data license. Do not redistribute raw data, derived datasets, or model artifacts without reviewing the applicable terms. Source code and data licensing are separate. ULB's author page lists Open Database / Database Contents terms; exact conditions must be checked before acquisition or reuse. Other candidate licenses have not been fully cleared.

No raw files were acquired. Counts and field descriptions above are source-reported, not locally profiled. No label maturity, entity independence, row ordering within a month, or feature availability at decision time has been verified from raw data.

## Existing solutions and actual evidence level

### Fraud Detection Handbook

Its baseline and validation chapters already cover chronological training, a modeled delay before labels become available, and repeated temporal assessment. Reimplementing these alone would be a reproduction, not a distinct contribution.

- [Baseline and label delay](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/BaselineModeling.html)
- [Validation strategies](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html)
- [Repository snapshot](https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook/tree/81cf7d1714bb7b2f5b496407d9055d91dc68dc25)

### Adaptive Reliability Layer (ARL)

The author describes drift monitoring, delayed-feedback learning, and choosing whether adaptation is warranted. This directly overlaps with the proposed broad concept. Its README distinguishes operational proxy metrics from fraud detection quality; do not reinterpret reported proxy improvements as improved fraud recall or money saved.

Repository tree inspection confirmed benchmark/configuration files and delayed-runtime tests exist. This review did not run those tests or audit their correctness. Published results remain author claims, not independently reproduced evidence. **ARL is source-available under BUSL-1.1, not currently open source**; its license restricts production use and provides a future change license. Do not copy it into a permissively licensed project without complying with its terms.

- [Reviewed snapshot and README](https://github.com/pberlizov/adaptive-reliability-layer/tree/f126303035b4d2dc9c5488667729fadf50cbf2d8)
- [Reviewed license](https://github.com/pberlizov/adaptive-reliability-layer/blob/f126303035b4d2dc9c5488667729fadf50cbf2d8/LICENSE)

### FiFAR and OpenL2D

The authors already provide experiments concerning limited expert availability and assignment under capacity constraints. The older FiFAR release explicitly recommends an upgraded dataset. Do not present human-AI capacity allocation itself as a new idea, and do not silently mix release versions.

- [FiFAR repository and upgrade notice](https://github.com/feedzai/fifar-dataset)
- [OpenL2D reviewed snapshot](https://github.com/feedzai/openl2d/tree/cfe5fd00850684a321187e41bdd49719a96a0ba1)
- [Updated dataset referenced by its authors](https://doi.org/10.6084/m9.figshare.28351172)

## Proposed alternative — not yet approved

Question: **Under declared monthly review capacity and simulated label-availability assumptions, do policy choices materially change held-out fraud capture compared with a frozen baseline?**

This is an empirical portfolio study, not a new monitoring platform. A negative result is acceptable. BAF would be used as synthetic account-application data, not called real transaction data or Canadian bank data.

Before running:

1. Confirm acquisition terms, version, checksum, schema, month support, and feature meanings; exclude target-derived or post-decision features.
2. Freeze chronological development and final test periods before model selection. Keep all variants derived from a common source out of claims of independent replication.
3. Start with a simple baseline. No dashboard, external AI API, or large hyperparameter search.
4. Specify a monthly capacity fraction instead of inventing daily timestamps. Batch top-k selection is an offline batch assumption, not an online queue guarantee.
5. Recognize that monotone threshold/calibration changes do not alter rankings: under exact equal top-k capacity on the same scores, they select the same cases (subject to ties). Do not manufacture a three-way improvement by comparing equivalent policies.
6. For threshold-only policies, report actual volume and capacity breaches. For ranking comparisons, evaluate frozen versus retrained models at the same budget with deterministic tie handling.
7. Report average precision, precision/recall at capacity, false-positive counts, and calibration with definitions and denominators. Use paired comparisons on identical held-out observations; do not treat a few months as strong evidence of long-term generalization.
8. Treat label delay as an explicit monthly simulation unless actual availability data is found. Train and choose actions only on labels available at the simulated decision time.
9. Report cost sensitivity only under declared hypothetical costs; do not claim prevented losses or causal business benefit.

## Stop conditions

- If synthetic data is unacceptable, do not quietly substitute it for real records.
- If a source offers only final labels, do not claim observed delayed-feedback validation.
- If existing experiments already answer the proposed question under the same assumptions, reproduce or contribute upstream rather than launch a duplicate platform.
- If meaningful differentiation remains unverified, keep implementation on hold instead of inventing novelty.

## Dataset sources

- [ULB/Worldline author distribution](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- [BAF author repository](https://github.com/feedzai/bank-account-fraud)
- [BAF author distribution and license](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022)
- [Handbook simulator](https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook/blob/main/Chapter_3_GettingStarted/SimulatedDataset.ipynb)

Verification performed: read author documentation, inspect repository paths and ARL license, record source links and selected commit identifiers, and check this documentation for formatting and local-link validity. No third-party code was executed and no claimed benchmark score was verified.
