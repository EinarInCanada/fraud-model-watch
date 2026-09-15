# Fraud Model Watch

**When transaction patterns change, can you still trust your fraud model?**

A planned, reproducible data science study of fraud-model performance over time and review decisions under limited analyst capacity.

## Status

The owner approved a **non-commercial empirical study on explicitly synthetic BAF account applications**, with a small experimental extension rather than a claim of a novel product. The historical [feasibility review](docs/FEASIBILITY.md) is retained. The [protocol v1.1](docs/PROTOCOL.md) baseline is now trained and evaluated on reference/development months only. [Initial results](docs/BASELINE_RESULTS.md) do not establish final performance or benefits of adaptive retraining. Final months 6–7 remain unscored.

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

The command validates the exact data hash, trains on month 0, and scores only months 2–5. Each run requires a new output directory; it never overwrites prior runs. Predictions stay in ignored local artifacts. The complete three-policy replay is not implemented yet. The gate rejects unavailable feedback; its caller must supply genuine stored sentinel predictions.

Original code is [MIT licensed](LICENSE); BAF data is not. See the license discrepancy and restrictions in DATA.md.

## Data and privacy

Do not commit credentials, personal transaction records, downloaded datasets, or model artifacts. Dataset licenses and redistribution conditions will be reviewed before use. Any published results must identify the dataset version, split, configuration, and limitations.
