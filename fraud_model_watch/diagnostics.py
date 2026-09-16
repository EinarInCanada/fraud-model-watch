"""Exploratory diagnostics of saved primary predictions; no refitting or tuning."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .baseline import load_base, sha256
from .evaluation import capacity_metrics
from .replay import score_final, write_json


def calibration(labels, scores):
    labels, scores = np.asarray(labels), np.asarray(scores)
    capacity_metrics(labels.tolist(), scores.tolist())  # shared input validation
    bins = np.minimum((scores * 10).astype(int), 9)
    rows = []
    for index in range(10):
        selected = bins == index
        rows.append(dict(lower=index / 10, upper=(index + 1) / 10,
            upper_inclusive=index == 9, count=int(selected.sum()),
            mean_probability=float(scores[selected].mean()) if selected.any() else None,
            positive_fraction=float(labels[selected].mean()) if selected.any() else None))
    return rows


def group_metrics(labels, selected):
    labels, selected = np.asarray(labels, dtype=int), np.asarray(selected, dtype=bool)
    n, positives, reviewed = len(labels), int(labels.sum()), int(selected.sum())
    captured = int(labels[selected].sum())
    false_positives = reviewed - captured
    return dict(n=n, positives=positives, negatives=n - positives, reviewed=reviewed,
                captured=captured, false_positives=false_positives,
                prevalence=positives / n if n else None,
                selection_rate=reviewed / n if n else None,
                recall=captured / positives if positives else None,
                false_positive_selection_rate=false_positives / (n - positives) if n > positives else None,
                precision=captured / reviewed if reviewed else None)


def paired_bootstrap(differences, repeats=1000, seed=20260916):
    """Multinomial counts exactly implement within-month row resampling of fixed {-1,0,1} differences."""
    rng = np.random.default_rng(seed)
    bootstrap = np.zeros(repeats, dtype=int)
    counts = []
    for values in differences:
        values = np.asarray(values)
        if not len(values) or not np.isin(values, [-1, 0, 1]).all():
            raise ValueError('nonempty fixed-selection differences in {-1,0,1} required')
        category_counts = np.array([(values == v).sum() for v in (-1, 0, 1)])
        sampled = rng.multinomial(len(values), category_counts / len(values), size=repeats)
        bootstrap += sampled[:, 2] - sampled[:, 0]
        counts.append(category_counts.tolist())
    return dict(replicates=repeats, seed=seed, monthly_difference_counts=counts,
                observed_difference=int(sum(np.sum(v) for v in differences)),
                percentile_ci95=np.quantile(bootstrap, [.025, .975], method='linear').tolist(),
                scope='within-month row bootstrap of fixed selections; no reranking, refitting or future-month uncertainty')


def run(frame, output, manifest):
    verified = score_final(frame, output, manifest)  # verifies full artifact file set and source alignment
    monthly, differences, pooled_groups = [], [], {}
    for month in (6, 7):
        batch = frame.loc[frame.month == month]
        y = batch.fraud_bool.to_numpy(dtype=int)
        selections = {}
        for policy in ('frozen', 'scheduled'):
            stored = pd.read_csv(Path(output) / f'predictions-{policy}-{month}.csv', float_precision='round_trip')
            scores = stored.score.to_numpy()
            selected = np.zeros(len(batch), dtype=bool)
            selected[capacity_metrics(y.tolist(), scores.tolist())['selected_positions']] = True
            selections[policy] = selected
            groups = []
            for name, mask in (('age_lt50', batch.customer_age.to_numpy() < 50),
                               ('age_ge50', batch.customer_age.to_numpy() >= 50)):
                groups.append(dict(group=name, **group_metrics(y[mask], selected[mask])))
                accumulator = pooled_groups.setdefault((policy, name), ([], []))
                accumulator[0].extend(y[mask].tolist())
                accumulator[1].extend(selected[mask].tolist())
            monthly.append(dict(month=month, policy=policy, calibration=calibration(y, scores), groups=groups))
        frozen, scheduled = selections['frozen'], selections['scheduled']
        differences.append(y * (scheduled.astype(int) - frozen.astype(int)))
        monthly.append(dict(month=month, capture_overlap={
            'both': int(((y == 1) & frozen & scheduled).sum()),
            'frozen_only': int(((y == 1) & frozen & ~scheduled).sum()),
            'scheduled_only': int(((y == 1) & ~frozen & scheduled).sum()),
            'neither': int(((y == 1) & ~frozen & ~scheduled).sum())}))
    utilities = []
    for value in (1, 10, 100):
        for penalty in (0, 5, 50):
            for p in verified['pooled_counts']:
                utilities.append(dict(value_per_positive=value, cost_per_refit=penalty,
                    cost_per_review=1, policy=p['policy'], captured=p['captured'],
                    refits=p['refits'], reviewed=p['k'],
                    utility=value * p['captured'] - penalty * p['refits'] - p['k']))
    return dict(scope='exploratory diagnostics after primary holdout was scored',
                primary_manifest_sha256=sha256(Path(output) / 'manifest.json'),
                monthly=monthly, bootstrap=paired_bootstrap(differences),
                pooled_groups=[dict(policy=p, group=g, **group_metrics(y, s))
                               for (p, g), (y, s) in pooled_groups.items()],
                hypothetical_utility=utilities,
                utility_warning='assumed units, not dollars or causal savings; entire replay refit count versus final-month captures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/Base.csv')
    parser.add_argument('--replay', default='artifacts/replay-v1.1')
    parser.add_argument('--output', default='artifacts/diagnostics.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new file under ./artifacts')
    replay_path = Path(args.replay)
    manifest = json.loads((replay_path / 'manifest.json').read_text())
    for name, digest in manifest['source_hashes'].items():
        if sha256(name) != digest:
            raise ValueError('primary source changed since prediction')
    result = run(load_base(args.data), replay_path, manifest)
    result['source_sha256'] = {p: sha256(p) for p in ['fraud_model_watch/diagnostics.py',
        'docs/COMPLETION_PLAN.md', 'requirements.txt']}
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, result)
    print(json.dumps({'bootstrap': result['bootstrap'], 'pooled_groups': result['pooled_groups']}, indent=2))
