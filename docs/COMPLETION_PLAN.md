# Completion requirements and fixed remaining experiments

Declared after the negative primary result and S1/S2 diagnostics. All BAF holdout results have already been seen: remaining BAF analyses are **exploratory**, never a second confirmatory test. No search for a winning policy or alteration of the primary experiment.

## Required deliverables

1. S3 sample-size/power curves with Monte Carlo uncertainty, including missed changes and a no-solution outcome.
2. BAF descriptive sensitivity to label delay and review capacity, plus a simple-versus-more-complex model comparison.
3. Primary paired error analysis, calibration tables, rounded-age subgroup review outcomes and explicitly hypothetical cost tradeoffs.
4. Controlled input-fault checks and a clear separation between detected invalid inputs, silent valid-looking shifts, and model performance.
5. A concise executable demonstration with no BAF redistribution, complete reproduction instructions, final research report, and requirement-by-requirement completion audit.
6. Tests, CI, clean repository, public GitHub publication of code and aggregate findings. Raw data/individual predictions stay local; original work MIT, external data terms separate.

## S3: required evidence volume

Use n in [30, 60, 100, 200, 400, 800, 1600] positive labels per event month; reference probability 0.20; stable p=0.20 and persistent p=0.16 or 0.12 from event month 5. Event months 2–11 and decisions 4–13, primary d=1. Compare original two-month persistence and unchanged corrected S2 gate. Seeds 3000–3499 are new; use numpy default_rng(300000000 + 10000*n + 1000000*regime_index + seed) and binomial draws (regime order stable, four-point drop, eight-point drop). n is not total application volume.

Report all settings, any-request/pre-change/post-change frequencies, exact 95% binomial intervals and conditional timing. Candidate design criterion is >=80% post-change response and <=5% stable any-request frequency **by point estimate**, not a statistical certification. Report the first tested n satisfying it, or none. A true four-point decline is below the retained five-point observed-effect filter; failure there is an important design mismatch, not justification for silently lowering the threshold. Do not interpolate or recommend production sample sizes.

## BAF secondary analyses

All remain descriptive and preserve source row ordering and previously declared features. Simulated labels for month m arrive at m+1+d. Use initial training month 0 and reference month d+1, so d=2 uses month 3, not unavailable month 2. Start scheduled refits at reference+2. Score final months 6–7 as exploratory outcomes. d=0 may legitimately train on month 6 at month 7: disclose that it is an adaptive test.

Compare frozen, scheduled, original evidence and S2-style corrected evidence policies under the following one-factor settings: (d=0, capacity=1%), (d=1, 1%), (d=2, 1%), and d=1 with capacity=0.5%, 2%, 5%. Each capacity also defines its own reference and evidence recalls. No setting selected as a winner. Reuse identical deterministic fits where training months are the same; report logical refits separately from physical cached computation. S2-style gate retains alpha/9 without refunds; no inferential guarantee for BAF dependence or adaptive training is claimed.

Complexity comparison: a single frozen random forest, 100 trees, max_depth=8, min_samples_leaf=20, no class weights, random_state=42, n_jobs=1, same month-0 training and preprocessing. Compare to frozen logistic regression at primary capacity on identical final observations. This is not a hyperparameter search or an estimate of optimal random-forest performance.

## Errors, calibration, subgroups and costs

Use the saved primary frozen/scheduled predictions, not newly optimized models. Count positive-label capture overlap and discordance, and use a paired percentile bootstrap of final rows within each month (1000 replicates, seed 20260916) on the **fixed selections** to describe uncertainty in captured-count difference. This does not bootstrap the top-k selection process, model fitting or future-month variability.

Calibration uses ten fixed equal-width probability bins with count, mean probability, positive fraction; empty bins are null. Age groups follow the authors' coarse <50 / >=50 grouping; selections remain the global monthly top-k, never group-specific thresholds. Report denominators, prevalence, recall, false-positive selection rate, and precision. Descriptive gaps do not establish discrimination or legal fairness.

Hypothetical utility units: value per captured positive in [1,10,100], per-refit penalty in [0,5,50], one unit per reviewed case. Compute value*captured - penalty*refits - reviewed. These are assumed utility units, not dollars, actual saved losses or correct human decisions. Also report the break-even arithmetic for scheduled minus frozen.

## Input-fault checks and demo

Test fail-closed hash/schema/label/nonfinite checks on generated fixtures, missing-category handling, and deliberate unknown-category/numerical shifts on fixtures without claiming detected drift. Show the existing count-based stable/drop/recovery/sparse scenarios in a small CLI demo, with explicit provenance and timing; no web dashboard or autonomous agent is required for this research deliverable.
