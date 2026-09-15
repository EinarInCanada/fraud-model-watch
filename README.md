# Fraud Model Watch

**When transaction patterns change, can you still trust your fraud model?**

A planned, reproducible data science study of fraud-model performance over time and review decisions under limited analyst capacity.

## Status

The initial feasibility review is complete: **hold implementation**. Existing work substantially overlaps with the broad concept, and none of the reviewed datasets establishes the original real-world, delayed-label transaction scenario. See the [evidence and decision](docs/FEASIBILITY.md). No dataset has been downloaded, no model trained, and no benchmark results produced. A narrower comparative study is proposed, not yet approved.

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

There is no installation command yet because there is no executable implementation.

## Data and privacy

Do not commit credentials, personal transaction records, downloaded datasets, or model artifacts. Dataset licenses and redistribution conditions will be reviewed before use. Any published results must identify the dataset version, split, configuration, and limitations.
