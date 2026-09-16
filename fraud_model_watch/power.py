"""S3 fixed-design sample-size diagnostics; not production sample-size advice."""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from .evaluation import Evidence, evidence_gate
from .stress import simulate, summarize
from .uncertainty import request_interval, uncertainty_gate

SIZES = (30, 60, 100, 200, 400, 800, 1600)
REGIMES = ('stable', 'four_point_drop', 'eight_point_drop')
POLICIES = (('persistence', evidence_gate), ('fisher_bonferroni', uncertainty_gate))


def generate_series(n, regime_index, seed):
    if type(n) is not int or n <= 0 or regime_index not in range(3):
        raise ValueError('invalid sample size or regime')
    rng = np.random.default_rng(300000000 + 10000 * n + 1000000 * regime_index + seed)
    probabilities = [(.20, .16, .12)[regime_index] if month >= 5 else .20
                     for month in range(2, 12)]
    return [Evidence(month, n, int(captured)) for month, captured in
            zip(range(2, 12), rng.binomial(n, probabilities))]


def summarize_requests(runs):
    result = summarize(runs)
    counts = {
        'any_request': sum(bool(r['requests']) for r in runs),
        'pre_change_request': sum(any(d < 7 for d in r['requests']) for r in runs),
        'post_change_request': sum(any(d >= 7 for d in r['requests']) for r in runs),
    }
    for name, count in counts.items():
        result[name + '_count'] = count
        result[name + '_ci95'] = request_interval(count, len(runs))
    result['no_post_change_request_count'] = len(runs) - counts['post_change_request']
    result['first_post_change_decision_counts'] = {
        str(d): sum(next((t for t in r['requests'] if t >= 7), None) == d for r in runs)
        for d in range(7, 14)
    }
    return result


def design_candidates(rows):
    """Point estimates only; do not interpolate or choose a winning policy."""
    result = []
    for policy, _ in POLICIES:
        stable = {r['n']: r['any_request_fraction'] for r in rows
                  if r['policy'] == policy and r['regime'] == 'stable'}
        for regime in REGIMES[1:]:
            eligible = sorted(r['n'] for r in rows if r['policy'] == policy
                              and r['regime'] == regime
                              and r['post_change_request_fraction'] >= .80
                              and stable[r['n']] <= .05)
            result.append({'policy': policy, 'regime': regime,
                           'first_tested_n_meeting_point_criteria': eligible[0] if eligible else None})
    return result


def run_suite(sizes=SIZES, seeds=range(3000, 3500)):
    seeds = tuple(seeds)
    if not seeds:
        raise ValueError('at least one seed required')
    rows = []
    for n in sizes:
        for regime_index, regime in enumerate(REGIMES):
            paired = [generate_series(n, regime_index, seed) for seed in seeds]
            for policy, gate in POLICIES:
                rows.append(dict(n=n, regime=regime, policy=policy,
                                 **summarize_requests([simulate(s, gate) for s in paired])))
    return {'protocol': 'S3', 'python': platform.python_version(), 'numpy': np.__version__,
            'seed_first': seeds[0], 'seed_last': seeds[-1], 'runs_per_setting': len(seeds),
            'scope': 'independent binomial positive-label counts, no model fitting or bank outcomes',
            'rows': rows, 'design_candidates': design_candidates(rows)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/power-s3.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new file under ./artifacts')
    result = run_suite()
    result['source_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in map(Path, [
        'fraud_model_watch/power.py', 'fraud_model_watch/uncertainty.py',
        'fraud_model_watch/stress.py', 'fraud_model_watch/evaluation.py',
        'docs/COMPLETION_PLAN.md', 'requirements.txt'])}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result['design_candidates'], indent=2))
