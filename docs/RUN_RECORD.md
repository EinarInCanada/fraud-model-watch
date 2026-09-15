# Primary replay record

## Before final scoring

Predictions were generated from clean implementation commit `6efc64a` using protocol 1.1 and the pinned BAF Base.csv. No final performance metrics had been computed when this section was committed.

Local manifest: `artifacts/replay-v1.1/manifest.json`

Manifest SHA-256: `bd91b3d41382cb0c475abba07b480fd2403768a22e1f319e042f6b02296b42ac`

The manifest records individual prediction/decision hashes, the data checksum, implementation hashes, package versions and fit history. It is a reproducibility anchor, not a cryptographically signed audit certificate. Raw samples and individual predictions are not uploaded.

One shared initial model was fitted on month 0. Scheduled refits took place at months 4, 5, 6 and 7, using data through months 2, 3, 4 and 5 respectively. No fit used month 6 or 7 labels. No fitting warnings were captured. Evidence-triggered refits: zero; the predeclared condition did not fire. No threshold was changed to force a trigger.

The next operation is the separate final scoring command; no further model selection will be performed for this primary run.
