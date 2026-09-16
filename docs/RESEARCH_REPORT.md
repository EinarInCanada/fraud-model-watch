# Fraud Model Watch: final research report

## Question and contribution

Under delayed outcome feedback and fixed monthly review capacity, does an evidence-triggered retraining rule outperform an unchanged or calendar-retrained fraud model? The answer in the primary experiment is **no demonstrated advantage**. The gate did not fire. The contribution is a reproducible negative-result study, accompanied by controlled experiments that explain why the gate can either overreact to sparse evidence or miss changes after statistical filtering.

This is a completed empirical research deliverable, not a production-ready system. Existing chronological-validation, monitoring and adaptation work substantially overlaps with the broad idea; the [feasibility review](FEASIBILITY.md) records that overlap. No claim of a uniquely original algorithm is made.

## Evidence hierarchy

1. **Primary BAF experiment:** frozen protocol, pinned data, saved target-free predictions and a pre-scoring manifest. Month-0 training; reference month 2; final months 6–7. The first protocol's timing error was corrected before fitting, not concealed. See [protocol](PROTOCOL.md), [run record](RUN_RECORD.md) and [primary results](FINAL_RESULTS.md).
2. **S1–S3 count experiments:** deliberately constructed or independent-binomial capture counts, not model training. These diagnose decision-rule behavior under stated assumptions. They do not establish that requested retraining fixes a deteriorated model.
3. **Secondary BAF diagnostics:** delay/capacity/model and error/subgroup/calibration analyses were declared after the final outcome was known. All are exploratory, even though settings were fixed before executing these particular analyses.
4. **Fault fixtures:** generated input-contract examples. They demonstrate deterministic rejection and accepted blind spots, not observed bank incidents or measured BAF shift robustness.

## Primary finding

At identical 1% monthly capacity, 2,049 out of 205,011 final applications are selected. There are 2,878 positive labels. Frozen and evidence-triggered policies capture 512, while four scheduled refits capture 530. Recall is 17.79% versus 18.42%; neither a large effect nor causal loss prevention follows from this comparison.

The paired analysis makes the tradeoff explicit: scheduled gains 61 captures but loses 43, net 18. A conditional, within-month bootstrap of fixed selected rows gives [-1, 37]. It does not rerank or refit, establish independence of the source observations, or quantify future-period uncertainty. A useful conclusion is **do not recommend the new gate based on this evidence**, not “all retraining is useless.”

## Why monitoring needs enough evidence

The original two-month persistence rule is not an uncertainty guarantee. In S2, with 30 positive labels per month, stable-run refit requests occur in 41% of 500 runs. Fisher/Bonferroni filtering cuts that to 0.2%, but persistent eight-point-change response falls from 74% to 1%. Quiet monitoring can therefore mean either stability or low power.

S3 fixes the rule and varies evidence volume. For an eight-point drop, the first tested point meeting >=80% post-change response and <=5% stable requests is 400 positive labels/month for persistence and 800 for corrected Fisher. Those are grid-point simulation findings, not minimum production sample sizes or confidence-bound certifications. No tested size works for a four-point drop under both criteria; retaining a five-point observed-effect filter explains the mismatch. The predeclared RNG seed formula also reuses some streams across different settings; per-setting binomial intervals are not simultaneous or independent-grid guarantees.

See [S1](STRESS_RESULTS.md), [S2](UNCERTAINTY_RESULTS.md) and [S3](POWER_RESULTS.md) for all settings, intervals, timing, missed responses and limitations.

## Operational tradeoffs

- **Label timing:** scheduled captures at d=0/1/2 are 521/530/523 at 1% capacity. The reference and warmup change with delay; these are not causal estimates of faster labels. The d=0 month-7 model uses month-6 labels and is an adaptive test.
- **Capacity:** at d=1, scheduled capture rises from 336 at 0.5% review capacity to 1,341 at 5%, while review volume rises from 1,024 to 10,250. More review is not free model improvement. Both evidence policies still never trigger.
- **Model complexity:** one fixed frozen forest captures 533 versus logistic regression's 512, but has worse Brier scores in both final months. This is one declared comparison, not tuned optimal performance or an established superior retraining policy.
- **Hypothetical costs:** scheduled-minus-frozen utility is 18V−4C with equal review counts. It is positive only when C<4.5V. Unknown capture uncertainty, review effectiveness and real costs prevent an actual ROI claim.
- **Subgroups:** scheduled gains 19 captures below age 50 and loses one at 50+. Global top-k selection is preserved; label prevalence and false-positive selection rates differ. This is descriptive synthetic evidence, not discrimination or fairness certification.

Full tables: [secondary analyses](SECONDARY_RESULTS.md) and [diagnostics](DIAGNOSTIC_RESULTS.md).

## What the software can and cannot detect

Hash, schema, label-domain and nonfinite checks reject eight generated invalid/unapproved inputs. Unknown categories, a large finite numerical shift and declared missing sentinels pass the schema contract and produce finite scores. A probability can be numerically valid and operationally unreliable. Checksums enforce an exact research input, not drift diagnosis. No autonomous repair, row deletion, unsupervised drift detector or automatic root-cause attribution is implemented. See [fault results](FAULT_RESULTS.md).

## Relevance to a data science portfolio

This work demonstrates the ability to define a measurable decision problem, preserve temporal availability, compare baselines at equal capacity, quantify uncertainty, inspect errors and subgroup effects, and communicate where the evidence does not support action. A model-risk or fraud-analytics discussion can use these artifacts to review assumptions and request further validation. Actual institutional usefulness would still require authorized representative data, observed label timestamps, production constraints and stakeholder review.

It does not prove production engineering experience, deployment savings, regulatory expertise or a positive novel-method result. Do not write a resume bullet claiming those outcomes.

## Limits and justified next research

Synthetic account applications are not real payments or Canadian-bank records. The eight-month horizon and two final months are short. Upstream feature extraction is proprietary, entity independence is not established, labels reflect source selection mechanisms, and simulated arrival times cannot validate actual feedback latency. Offline monthly top-k assumes the whole batch is available; no online queue or analyst action is modeled. Age is a retained predictor, not a production-admissibility endorsement. Dataset-license discrepancies remain disclosed; no restricted row-level artifacts are published.

A separate future study could preregister a rule aligned to a smaller meaningful drop, use new data with actual availability timestamps, or test whether triggered retraining repairs a known deteriorating model. Those are **future hypotheses**, not unfinished obligations of this scoped study, and should not reuse these final outcomes as fresh confirmation.

## Reproducibility and completion

Use [REPRODUCE.md](REPRODUCE.md) for commands and [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) for the requirement mapping. Aggregate JSON, source/data hashes, deterministic tests and CI are public. Raw data, individual predictions and model objects remain local and ignored. Code is MIT; external data terms are separate.
