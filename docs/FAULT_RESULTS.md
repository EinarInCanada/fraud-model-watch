# Input-contract failures versus silent shifts

These are generated 200-row fixtures, **not real bank incidents or BAF performance experiments**. [All measured checks](results/faults.json).

| Case | Behavior | What it establishes |
|---|---|---|
| Missing or duplicate column | Reject | Exact schema contract |
| Label outside 0/1, month outside 0–7 | Reject | Domain contract |
| Infinite or NaN numeric value | Reject | Fail closed on nonfinite input |
| Missing category | Reject | No silent categorical imputation |
| Generated file passed to pinned BAF loader | Reject checksum | Only the pinned research file is accepted |
| Unseen category | Accept, finite predictions | Encoder falls back to all-zero; no drift alarm |
| Finite numerical shift | Accept, finite predictions | Schema validity does not establish prediction validity |
| Declared -1 missing sentinel | Accept, train-fitted imputation | Documented missing-value path, not arbitrary repair |

Eight malformed/unapproved cases were rejected; all three valid-looking cases passed. On this artificial fixture, adding 1,000 to velocity_6h changes one score by about 0.9999 without a schema alarm. This is an intentional illustration of a blind spot, not a meaningful estimate of fraud-model degradation. Unknown-category and sentinel paths also change scores. No row is deleted and the source frame is not rewritten.

The pinned checksum would reject *any* modified BAF file, including benign changes. It is a reproducibility guard, not an online data-quality monitor. The schema validator used separately is weaker: finite, valid-looking shifts can pass. Therefore this project can distinguish some **invalid inputs** from **accepted inputs**, but cannot automatically diagnose a shift's cause or infer model damage before labels arrive. No unsupervised drift detector or fault-to-refit policy is claimed.

## Reproduce without BAF

```sh
.venv/bin/python -m fraud_model_watch.faults --output artifacts/faults-new.json
python3 -m fraud_model_watch.demo
python3 -m fraud_model_watch.demo --json
```

The demo needs only the standard library and shows stable, persistent-drop, recovery and sparse-label traces. A simulated request is not executed retraining: the recovery scenario still requests at decision 8 after recovery starts at event month 7, because labels arrive two clock months after the event. Sparse-label silence is not a health certificate.
