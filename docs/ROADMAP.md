# Roadmap

## 0. Initialize — complete

- Establish the research question, scope, and publication workflow.
- Publish the initial repository without claiming implemented capabilities.

## 1. Feasibility and overlap — complete; revised scope approved

See [FEASIBILITY.md](FEASIBILITY.md). The broad product was rejected; the owner subsequently approved a non-commercial comparative study with synthetic data and a modest experimental extension. [Protocol v1](PROTOCOL.md) governs implementation.

- Inspect candidate data sources for license, timestamps, labels, and leakage risks.
- Compare existing open-source implementations against the same proposed task.
- Record a go/no-go decision: reuse existing work, identify a measurable contribution, or stop.
- Do not build a dashboard before this gate passes.

## 2. Reproducible baseline — complete (reference/development only)

Pinned Base.csv verified; conservative feature contract and pre-fit timing correction recorded; logistic regression trained on month 0 and scored on months 2–5. See [results](BASELINE_RESULTS.md). Subsequent three-policy replay and held-out scoring are now complete; see FINAL_RESULTS.md.

- Document acquisition without redistributing restricted data.
- Add schema checks, chronological split tests, a simple model, and reproducible evaluation.
- Freeze the test period before tuning.

## 3. Time-based evaluation

- Compare performance and calibration across periods.
- Quantify uncertainty and explain limitations of the observation window.
- Handle delayed labels only if supported by data, or explicitly simulate the delay.

## 4. Decision experiment — primary run complete

See [final results](FINAL_RESULTS.md). Scheduled retraining captured 18 more positive labels than frozen/evidence under equal capacity. The proposed gate did not fire; no advantage demonstrated. Sensitivity, uncertainty and subgroup analyses remain unperformed.

- Compare frozen, monthly retrained, and evidence-triggered policies under equal review capacity.
- Choose policies using only information available at the decision time.
- Report hypothetical cost sensitivity rather than invented financial savings.

## 5. Failure analysis and delivery

S2 uncertainty diagnostic is complete: [results](UNCERTAINTY_RESULTS.md). Fixed-horizon statistical filtering reduces sparse-data false alarms but misses most simulated persistent changes at n=30. No superiority or deployment claim. Power/sample-size analysis and end-to-end policy benefit remain unverified.

S1 aggregate gate diagnostics are complete: [results](STRESS_RESULTS.md). They demonstrate small-sample false alarms, delayed responses and missing-feedback limitations, not improved model performance. Transaction-level fault studies, uncertainty-aware policy validation and subgroup analyses remain future work; no new policy has been selected from these outcomes.

- Evaluate controlled faults separately from real temporal changes.
- Publish reproducible results, limitations, and a concise demonstration.

## Commit and push policy

After each coherent increment: run relevant checks, inspect the diff and staged files for secrets or data, commit an honest summary, and push to GitHub. Documentation-only steps should check links and formatting; executable steps must include appropriate tests. Failed or incomplete work must be labeled accurately. Do not backdate commits, create empty activity commits, or imply automated daily work is scheduled.
