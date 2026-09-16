# Fraud Model Watch

**When should a fraud model be retrained—and when is there too little evidence to tell?**

A reproducible, non-commercial data science study of delayed fraud feedback, limited review capacity and retraining decisions. Built on **1 million synthetic bank-account applications**, with separate controlled simulations to expose failure modes.

[Research report](docs/RESEARCH_REPORT.md) · [Reproduce every study](docs/REPRODUCE.md) · [Results](#what-the-experiments-found) · [Scope and limitations](#what-this-is-not)

## Why this question matters

A model can keep producing valid scores while its useful capture rate changes. Labels arrive late, reviewing more cases costs capacity, and frequent retraining is not automatically better. Before recommending an intervention, an analyst needs to ask:

- Is this invalid input, a distribution change, or measured prediction degradation?
- Are enough mature positive labels available to distinguish noise from a meaningful drop?
- Does a retraining policy improve capture at the **same** review capacity?
- Does the apparent gain survive uncertainty, subgroup checks and explicit cost assumptions?

This repository makes those questions executable. It does **not** claim a new fraud-detection algorithm or demonstrate bank deployment value.

## Try it in 30 seconds

From the repository root, no dataset or API key required:

```sh
python3 -m fraud_model_watch.demo
```

```text
Scenario    Request decisions   Interpretation
stable      []                  No observed decline.
abrupt      [8, 10, 12]         Change starts at event 5; first request is decision 8.
recovery    [8]                 Recovery starts at event 7, but stale feedback still requests at decision 8.
sparse      []                  Too few positive labels; silence is not evidence of health.
```

These are **hand-specified aggregate counts**, not measured bank incidents. A request does not execute retraining. Add `--json` to inspect the event, label-availability and decision timeline.

## What the experiments found

The scoped research implementation is complete. Negative findings are part of the deliverable.

| Experiment | Observed result | Interpretation |
|---|---|---|
| Primary BAF replay, final months 6–7 | Frozen/evidence: **512** captures; scheduled: **530**, each reviewing **2,049** cases | Evidence gate never fired; no demonstrated extension benefit |
| Paired fixed-selection bootstrap | Scheduled-minus-frozen **18**, interval **[-1, 37]** | Small observed gain is not robust evidence of superiority |
| S2, 30 positive labels/month | Statistical filtering reduces stable-run requests **41% → 0.2%**, but persistent-change response **74% → 1%** | False-alarm control can destroy sensitivity |
| S3, persistent 8-point decline | First tested size meeting point criteria: **400** positives/month for persistence, **800** for corrected Fisher | Simulation-specific evidence-volume requirement, not production advice |
| S3, persistent 4-point decline | No tested size meets both criteria | The retained 5-point effect filter conflicts with the smaller true change |
| Frozen random forest vs logistic | **533 vs 512** captures; forest Brier score worse in both months | More complexity does not improve every metric |
| Controlled input fixtures | **8 rejected**, **3 accepted** including an unknown category and a finite shift | Schema validity is not a model-health guarantee |

Primary evaluation has **205,011 applications and 2,878 positive labels**. Capture means a positive label selected into the review batch, not prevented fraud or saved money. The bootstrap conditions on fixed selections and does not estimate future-month or refitting uncertainty. S1/S2/S3 use simulated positive-label counts, not fitted BAF outcomes.

Read the complete [primary results](docs/FINAL_RESULTS.md), [S1 failures](docs/STRESS_RESULTS.md), [S2 tradeoff](docs/UNCERTAINTY_RESULTS.md), [S3 power study](docs/POWER_RESULTS.md), [delay/capacity/model comparison](docs/SECONDARY_RESULTS.md), [error/calibration/subgroup/cost analysis](docs/DIAGNOSTIC_RESULTS.md), and [fault study](docs/FAULT_RESULTS.md). Full secondary aggregates are in [docs/results](docs/results).

## How the study works

1. **Pin and validate:** verify BAF v2 checksum, exact schema, label domain and finite inputs. Fit preprocessing on training data only.
2. **Respect simulated time:** event-month m labels arrive at m+1+d. The primary d=1 model starts with month 0, observes a month-2 reference, and uses only mature labels for later decisions.
3. **Keep capacity equal:** select monthly top 1% with deterministic tie handling. Compare frozen, calendar-retrained and evidence-triggered policies.
4. **Separate decisions from primary scoring:** persist decisions and target-free predictions, anchor a manifest, then verify hashes and row alignment before scoring final months 6–7.
5. **Try to falsify the idea:** simulate stable/noisy/delayed feedback, measure statistical power, change delay/capacity, inspect paired errors and subgroup outcomes, and expose validator blind spots.

The primary final period was frozen before fitting. Follow-up BAF analyses are explicitly **exploratory**, because those final outcomes had already been seen. The [pre-scoring record](docs/RUN_RECORD.md) and [fixed completion plan](docs/COMPLETION_PLAN.md) preserve that distinction.

## Run the research

Python **3.11–3.13**; pinned scientific dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m fraud_model_watch.power --output artifacts/power-local.json
```

The tests, demo, count studies and generated-fixture checks require **no BAF download**. For BAF runs, acquire Base.csv using [DATA.md](docs/DATA.md), then follow [REPRODUCE.md](docs/REPRODUCE.md). Commands refuse existing output paths; raw data and individual predictions remain in ignored local directories. Primary prediction requires a clean committed checkout.

There is no API service, dashboard, external LLM dependency or secret key to configure.

## What this demonstrates

- **Experimental design:** chronological evaluation, explicit availability assumptions, fixed baselines, leakage precautions and honest post-holdout exploration.
- **Statistical reasoning:** paired comparisons, Monte Carlo intervals, multiplicity versus power, and negative results that constrain conclusions.
- **Operational evaluation:** recall/precision under fixed review capacity, logical refits versus cached compute, and hypothetical utility break-even analysis.
- **Research engineering:** reproducible commands, source/data/artifact hashes, deterministic fixtures, test coverage and CI on three Python versions.

A defensible portfolio description: *“Built a reproducible fraud-model monitoring study on 1M synthetic applications; evaluated delayed-label retraining policies, review-capacity tradeoffs and uncertainty, and documented when the proposed trigger failed to improve outcomes.”*

## What this is not

Not a new monitoring platform, production fraud adjudicator, Canadian-bank dataset, financial-savings claim, fairness certification or evidence of long-term generalization. Only eight monthly periods exist; final performance covers two. Label delays are simulated, upstream feature timing cannot be fully audited, and independent application sampling is not established. Accepted input shifts are not automatically diagnosed.

The small contribution is an **auditable comparative experiment and failure analysis**, not an originality or superiority claim. Existing methods and overlapping projects are discussed in [FEASIBILITY.md](docs/FEASIBILITY.md).

## License and data handling

Original code: [MIT](LICENSE). External BAF data is **not MIT**. Its current distribution and older author datasheet contain different non-commercial license labels; see [DATA.md](docs/DATA.md). No raw/processed datasets, individual predictions or model artifacts are published. This repository is not legal clearance for downstream data use.

See [the roadmap](docs/ROADMAP.md), [completion audit](docs/COMPLETION_AUDIT.md) and [contributing guidance](CONTRIBUTING.md). Commits represent verified work; no artificial daily activity or backdating.
