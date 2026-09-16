# Reproduce the complete study

Run commands from the repository root, using Python 3.11–3.13. No API key, external model service, notebook server or dashboard is required. Use a clean checkout for the primary prediction stage. Do not run `git add .` after downloading data; raw files and artifacts must stay ignored.

## 1. Environment and fast checks

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
python3 -m fraud_model_watch.demo
python3 -m fraud_model_watch.demo --json
```

The demo itself is standard-library-only. Scientific dependencies are needed for the tests and remaining studies. CI runs fixture tests on Python 3.11, 3.12 and 3.13 without downloading BAF.

## 2. Independent count and fixture studies

```sh
.venv/bin/python -m fraud_model_watch.stress --output artifacts/reproduction-stress.json
.venv/bin/python -m fraud_model_watch.uncertainty --output artifacts/reproduction-uncertainty.json
.venv/bin/python -m fraud_model_watch.power --output artifacts/reproduction-power.json
.venv/bin/python -m fraud_model_watch.faults --output artifacts/reproduction-faults.json
```

S1 uses seeds 0–199; S2 2000–2499; S3 3000–3499 with its declared numpy seed formula. Each gate pair uses the same series within its setting. No BAF download is needed. Reports include source hashes. Compare aggregate rows with the published [results](results); runtime versions may differ. The S3 seed formula can overlap streams across different settings; do not treat settings as independent replications.

## 3. Acquire the pinned research data

Follow [DATA.md](DATA.md). Review source terms yourself; this repository does not redistribute data or confer permission for other uses. The program checks the exact Base.csv v2 SHA-256 before loading. A different release, edited file or ZIP passed in place of the CSV fails closed. Never bypass the checksum to claim a reproduction.

## 4. Development baseline and primary replay

```sh
.venv/bin/python -m fraud_model_watch.baseline --output artifacts/reproduction-baseline
.venv/bin/python -m fraud_model_watch.replay predict --output artifacts/reproduction-replay
.venv/bin/python -m fraud_model_watch.replay score --output artifacts/reproduction-replay
```

Predict refuses an uncommitted worktree. It saves decisions before fits and target-free predictions, then records file/source hashes in a manifest. Score validates the manifest, full file set, hashes and exact source-row order. Changing hashed source files between stages causes rejection. These checks are reproducibility safeguards, not cryptographic proof against a malicious author.

Expected primary pooled captures: frozen=512, scheduled=530, evidence=512. Each reviews 2,049 cases across final months 6–7. Reproducing an already-published outcome does not create a new untouched holdout. Fit times and checkout/manifest metadata need not match; the recorded machine used Python 3.12.1 and pinned dependencies.

## 5. Secondary analyses and primary diagnostics

```sh
.venv/bin/python -m fraud_model_watch.secondary --output artifacts/reproduction-secondary.json
.venv/bin/python -m fraud_model_watch.diagnostics --replay artifacts/reproduction-replay --output artifacts/reproduction-diagnostics.json
```

Secondary performs six fixed one-factor settings plus one frozen-forest comparison. Fits are cached by identical training months; logical policy refits remain separate. Expected frozen forest final captures: 255 and 278. Primary diagnostic bootstrap: observed difference 18, conditional interval [-1,37] with the pinned environment. Diagnostic bootstrap and S3 generation use numpy; different package versions are not an exact reproduction.

## Output and verification rules

- Every file-producing command requires a **new** path under `artifacts/`; it will not overwrite prior output. On rerun, choose another name rather than deleting earlier evidence.
- Primary/baseline outputs include individual scores and must stay local. Secondary/count/diagnostic reports are aggregate summaries; only reviewed aggregates belong in `docs/results/`.
- Run `git diff --check`, the full test suite and `git status --short` before committing code changes. Never commit data, fitted models, credentials or personal records.
- All published aggregate reports preserve the source hashes used in their generation. Timings are measured local compute, not production estimates. Exact numerical matches are expected in the recorded dependency environment; different platforms may have small floating-point differences.

No command here schedules future runs or manufactures daily contributions. Completed verified work is committed normally.
