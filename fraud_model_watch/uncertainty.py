"""S2 fixed-family Fisher gate diagnostics, never a production alarm guarantee."""
import argparse
from functools import lru_cache, partial
import hashlib
import json
from pathlib import Path
import platform

from scipy.stats import binomtest, fisher_exact

from .evaluation import evidence_gate
from .stress import simulate, stochastic_series, summarize

ALPHA = 0.05
COMPARISONS = 9


@lru_cache(maxsize=100000)
def decline_pvalue(ref_positive, ref_captured, positive, captured):
    if any(type(x) is not int for x in (ref_positive, ref_captured, positive, captured)):
        raise ValueError('counts must be integers')
    if min(ref_positive, positive) <= 0 or not 0 <= ref_captured <= ref_positive or not 0 <= captured <= positive:
        raise ValueError('invalid counts')
    return float(fisher_exact([[ref_captured, ref_positive - ref_captured],
                              [captured, positive - captured]], alternative='greater').pvalue)


def uncertainty_gate(decision, reference, history, last_refit=None, *, corrected=True):
    if type(decision) is not int or decision not in range(4, 14):
        raise ValueError('outside predeclared fixed horizon')
    history = tuple(history)
    if any(e.month not in range(3, 12) for e in history):
        raise ValueError('outside predeclared comparison family')
    eligible, reason = evidence_gate(decision, reference, history, last_refit)
    if not eligible:
        return False, reason
    by_month = {e.month: e for e in history}
    recent = [by_month[decision - 3], by_month[decision - 2]]
    threshold = ALPHA / COMPARISONS if corrected else ALPHA
    if all(decline_pvalue(reference.positives, reference.captured, e.positives, e.captured)
           <= threshold for e in recent):
        return True, 'persistent_drop_with_fisher_evidence'
    return False, 'insufficient_statistical_evidence'


def request_interval(count, total):
    interval = binomtest(count, total).proportion_ci(confidence_level=0.95, method='exact')
    return [float(interval.low), float(interval.high)]


def run_suite():
    policies = [('persistence', evidence_gate),
                ('fisher_uncorrected', partial(uncertainty_gate, corrected=False)),
                ('fisher_bonferroni', uncertainty_gate)]
    rows = []
    for n in (30, 1000):
        for regime_index, regime in enumerate(('stable', 'persistent', 'transient')):
            series = [stochastic_series(n, regime_index, seed) for seed in range(2000, 2500)]
            for name, gate in policies:
                runs = [simulate(s, gate) for s in series]
                count = sum(bool(r['requests']) for r in runs)
                rows.append(dict(n=n, regime=regime, policy=name, any_request_count=count,
                                 any_request_ci95=request_interval(count, len(runs)), **summarize(runs)))
    return {'protocol': 'S2', 'python': platform.python_version(), 'seeds': [2000, 2499],
            'alpha': ALPHA, 'unique_comparisons': COMPARISONS, 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/uncertainty-s2.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new file under ./artifacts')
    result = run_suite()
    result['source_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in map(Path,
        ['fraud_model_watch/uncertainty.py', 'fraud_model_watch/stress.py',
         'fraud_model_watch/evaluation.py', 'docs/UNCERTAINTY_PROTOCOL.md', 'requirements.txt'])}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result, indent=2))
