# S2: fixed-horizon uncertainty diagnostic

Declared 2026-09-16 after S1, before executing S2. This is an exploratory extension on independently seeded synthetic counts, not validation on new bank data. Primary BAF outcomes and the S1 policy remain unchanged.

## Fixed candidate

Retain the S1 two-month gate's 5-point observed drop, 30-positive minimum, one-month additional label delay and two-month cooldown. In addition, require each of the latest two months to pass a one-sided Fisher exact test comparing reference captured/not-captured counts to that month's counts. Table rows are reference then current; alternative is greater (reference capture probability higher).

There are nine possible reference comparisons (event months 3–11). Allocate familywise alpha=0.05 across these **nine unique comparisons**, so each uses 0.05/9. Reusing a comparison in consecutive windows does not create a new test, nor refund its budget. Fail closed outside decisions 4–13. No indefinite monitoring or resettable alpha guarantee is claimed.

Fisher tests equality/no decline, **not a decline of at least five points**. The five-point observed-effect filter is separate. Under independent binomial reference/current observations with valid null p-values, the union bound controls the chance of any false rejection over this fixed family even though comparisons share the reference. Requiring two rejections and applying additional filters cannot increase that bound. This does not transfer automatically to dependent financial transactions or adaptive model/reference selection.

Sources: [SciPy Fisher exact documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html), [statsmodels Bonferroni implementation](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/stats/multitest.py). Use already pinned SciPy; no third-party code is copied.

## Comparisons and evaluation

Compare three gates on identical series: original persistence; persistence plus Fisher at 0.05 per comparison (uncorrected ablation); persistence plus Fisher at 0.05/9. No parameter search.

Use S1's stable/persistent/transient generators, n=30 and 1000, but **500 fresh seeds 2000–2499** for each cell. All six cells and all three policies must be reported. Months, probabilities and seed construction otherwise match S1. These seeds were not used to design S1. They remain synthetic experiments, not an independent validation of the data-generating assumptions.

Report count/fraction of runs with any request; 95% exact binomial interval for that run-level probability; pre-change request fraction; post-change request fraction; mean request count; conditional median first post-change decision. Exact intervals describe Monte Carlo uncertainty, not external validity, and are not simultaneous across all reported cells. In stable cells any request is a false alarm; in changed cells a response need not imply successful retraining. Zero alarms does not imply zero risk.

## Stop and limitations

Publish failures to detect true changes as prominently as reduced alarms. No BAF file is read. No model is fitted or repaired. Retain aggregate-binomial limitations, including omitted review-capacity coupling, dependence, selective feedback and unknown causal value of retraining. Do not deploy the corrected gate or call it superior based only on these counts. Any extended horizon or altered reference requires a new declared testing budget/design.
