"""S1 aggregate-count gate diagnostics. No BAF data, fitting, or financial claims."""
import argparse
import hashlib
import json
import platform
import random
import statistics
from pathlib import Path

from .evaluation import Evidence, available_training_months, evidence_gate


def single_month_gate(decision, reference, history, last_refit):
    """One-factor ablation: one recent month instead of two; all other rules kept."""
    available = available_training_months(decision)
    if reference.month != 2 or any(e.month not in available for e in [reference, *history]):
        raise ValueError('invalid or unavailable reference/evidence')
    if len({e.month for e in history}) != len(history):
        raise ValueError('duplicate evidence month')
    if last_refit is not None:
        if last_refit >= decision:
            raise ValueError('invalid last refit')
        if decision - last_refit < 2:
            return False, 'cooldown'
    latest = next((e for e in history if e.month == available[-1] and e.month > 2), None)
    if latest is None:
        return False, 'insufficient_post_reference_evidence'
    if min(reference.positives, latest.positives) < 30:
        return False, 'insufficient_positive_labels'
    dropped = 20 * (reference.captured * latest.positives - latest.captured * reference.positives) >= reference.positives * latest.positives
    return (True, 'recall_drop') if dropped else (False, 'hold')


def simulate(series, gate=evidence_gate):
    if len({e.month for e in series}) != len(series):
        raise ValueError('duplicate month')
    if any(e.month not in range(2, 12) for e in series):
        raise ValueError('S1 supports event months 2–11 only')
    reference = next(e for e in series if e.month == 2)
    last_refit, trace = None, []
    for decision in range(4, 14):
        available = available_training_months(decision)
        history = [e for e in series if e.month in available and e.month > 2]
        trigger, reason = gate(decision, reference, history, last_refit)
        if trigger:
            last_refit = decision
        trace.append({'decision': decision, 'request': trigger, 'reason': reason,
                      'evidence_months': [e.month for e in history]})
    requests = [row['decision'] for row in trace if row['request']]
    return {'requests': requests, 'first_request': requests[0] if requests else None,
            'count': len(requests), 'trace': trace}


def deterministic_scenarios():
    gradual = dict(zip(range(3, 12), [200, 180, 160, 140, 120, 100, 100, 100, 100]))
    counts = {
        'stable': lambda m: 200,
        'abrupt': lambda m: 120 if m >= 5 else 200,
        'transient': lambda m: 120 if m == 5 else 200,
        'gradual': lambda m: gradual[m],
        'boundary': lambda m: 150 if m >= 5 else 200,
        'recovery': lambda m: 120 if m in (5, 6) else 200,
    }
    scenarios = {name: [Evidence(2, 1000, 200)] + [Evidence(m, 1000, fn(m)) for m in range(3, 12)]
                 for name, fn in counts.items()}
    scenarios['sparse'] = [Evidence(2, 30, 6)] + [Evidence(m, 25, 2) for m in range(3, 12)]
    scenarios['missing'] = [e for e in scenarios['abrupt'] if e.month not in (6, 8, 10)]
    return scenarios


def stochastic_series(n, regime_index, seed):
    rng = random.Random(seed + 10000 * n + 100000000 * regime_index)
    series = []
    for month in range(2, 12):
        changed = (regime_index == 1 and month >= 5) or (regime_index == 2 and month == 5)
        probability = 0.12 if changed else 0.20
        captured = sum(rng.random() < probability for _ in range(n))
        series.append(Evidence(month, n, captured))
    return series


def summarize(runs):
    post = [[d for d in row['requests'] if d >= 7] for row in runs]
    first = [row[0] for row in post if row]
    return {'runs': len(runs),
            'any_request_fraction': sum(bool(r['requests']) for r in runs) / len(runs),
            'pre_change_request_fraction': sum(any(d < 7 for d in r['requests']) for r in runs) / len(runs),
            'post_change_request_fraction': sum(bool(row) for row in post) / len(runs),
            'mean_requests': statistics.mean(r['count'] for r in runs),
            'median_first_post_change_decision': statistics.median(first) if first else None}


def run_suite():
    deterministic = {name: {policy: simulate(series, gate) for policy, gate in
                           [('two_month', evidence_gate), ('one_month', single_month_gate)]}
                     for name, series in deterministic_scenarios().items()}
    stochastic = []
    for n in (30, 1000):
        for regime_index, regime in enumerate(('stable', 'persistent', 'transient')):
            paired = [stochastic_series(n, regime_index, seed) for seed in range(200)]
            for policy, gate in [('two_month', evidence_gate), ('one_month', single_month_gate)]:
                metrics = summarize([simulate(series, gate) for series in paired])
                stochastic.append(dict(n=n, regime=regime, policy=policy, **metrics))
    return {'protocol': 'S1', 'python': platform.python_version(),
            'scope': 'aggregate-count diagnostics, not fitted-model performance',
            'deterministic': deterministic, 'stochastic': stochastic}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/stress-s1.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new output file beneath ./artifacts')
    result = run_suite()
    result['source_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [Path('fraud_model_watch/stress.py'), Path('fraud_model_watch/evaluation.py'), Path('docs/STRESS_PROTOCOL.md')]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'deterministic_requests': {name: {p: x['requests'] for p, x in policies.items()}
          for name, policies in result['deterministic'].items()}, 'stochastic': result['stochastic']}, indent=2))
