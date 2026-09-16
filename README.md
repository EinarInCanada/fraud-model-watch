# Fraud Model Watch

**When transaction patterns change, can you still trust your fraud model?**

A reproducible data science study of fraud-model performance over time and review decisions under limited analyst capacity.

## Status

The **primary non-commercial study on synthetic BAF account applications is complete**. [Final results](docs/FINAL_RESULTS.md): scheduled retraining captured 530 positive labels versus 512 for frozen/evidence-triggered models at identical review capacity. The evidence gate never fired; **no advantage for the proposed extension was demonstrated**. Final months 6–7 have now been scored. Any subsequent tuning on them is exploratory.

The [feasibility review](docs/FEASIBILITY.md), [protocol v1.1](docs/PROTOCOL.md), [development baseline](docs/BASELINE_RESULTS.md), and [pre-scoring manifest anchor](docs/RUN_RECORD.md) preserve the research timeline. This is not a novel banking product or a production fraud adjudicator.

The subsequent [S1 stress study](docs/STRESS_RESULTS.md) exposes a limitation: with only 30 positive labels per month, the two-month gate requested refitting in 45% of 200 simulated stable runs. These are aggregate-count diagnostics, not real transaction outcomes. Persistence alone does not provide statistical uncertainty control.

The [S2 uncertainty study](docs/UNCERTAINTY_RESULTS.md), on 500 fresh seeds per setting, reduces small-sample stable-run requests from 41% to 0.2% with fixed-horizon Fisher/Bonferroni filtering, **but responds to only 1% of persistent-decline runs at that sample size**. This is a false-alarm/power tradeoff, not a demonstrated superior policy. Both positive and negative results are published.

## Research questions

- Does performance deteriorate on later transactions, compared with a frozen baseline?
- Can input-quality problems be distinguished from distribution shifts? A shift alone does not prove performance degradation.
- Under a fixed review budget, how do threshold changes, retraining, and an unchanged model compare?
- What can be responsibly reported before outcome labels arrive?

## Planned evaluation

- Use chronological splits when trustworthy timestamps are available, and prevent future information from entering features or decisions.
- Compare a simple baseline with more complex models on identical held-out data.
- Measure precision-recall performance, calibration, and precision/recall at a declared review capacity; include denominators and uncertainty.
- Declare assumptions about label availability, transaction sampling, and hypothetical error costs.
- Separate observed data from injected faults or simulated shifts. Never present synthetic experiments as bank incidents.
- Report negative results and limitations, not just successful demonstrations.

## Scope

This is a research portfolio project, not a banking product or an automated fraud adjudicator. It will not move money, block accounts, or make decisions about real customers. AI agents and external model APIs are not required for the initial study.

## Development

See [the roadmap](docs/ROADMAP.md) and [contribution guidance](CONTRIBUTING.md). Each completed, verified increment should be committed and pushed with an accurate description. Commits reflect real work, not an artificial daily activity target.

Use Python 3.11–3.13. Timing/gate primitives are standard-library only; the baseline requires pinned scientific packages:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Acquire Base.csv using [DATA.md](docs/DATA.md), then run:

```sh
.venv/bin/python -m fraud_model_watch.baseline --output artifacts/baseline-v1.1
```

The command validates the exact data hash, trains on month 0, and scores only months 2–5. Each run requires a new output directory; it never overwrites prior runs. Predictions stay in ignored local artifacts.

The primary three-policy replay is implemented as separate prediction and scoring stages:

```sh
.venv/bin/python -m fraud_model_watch.replay predict --output artifacts/replay-v1.1
.venv/bin/python -m fraud_model_watch.replay score --output artifacts/replay-v1.1
```

Prediction requires a clean committed checkout. It saves each decision before fitting/predicting, stores predictions without targets, and records source/dependency and artifact hashes. Scoring verifies those hashes and source-row alignment before reading final labels. These are reproducibility checks, not tamper-proof signatures. Only the primary one-month additional label delay is implemented. Sensitivity runs need their own temporally valid reference design; the two-month delay cannot reuse a month-2 reference trained on month 0.

Original code is [MIT licensed](LICENSE); BAF data is not. See the license discrepancy and restrictions in DATA.md.

Run the independent gate diagnostics without downloading BAF:

```sh
python3 -m fraud_model_watch.stress --output artifacts/stress-s1.json
```

See [the diagnostic protocol](docs/STRESS_PROTOCOL.md) for the fixed scenarios, seeds and limitations.

Run the separate uncertainty diagnostic after installing requirements:

```sh
.venv/bin/python -m fraud_model_watch.uncertainty --output artifacts/uncertainty-s2.json
```

## Data and privacy

Do not commit credentials, personal transaction records, downloaded datasets, or model artifacts. Dataset licenses and redistribution conditions will be reviewed before use. Any published results must identify the dataset version, split, configuration, and limitations.
