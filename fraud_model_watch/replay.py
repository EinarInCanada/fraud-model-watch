"""Primary d=1 replay. Predict first; score held-out labels in a separate command."""
import argparse
import json
import platform
import subprocess
import time
import warnings
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss
from threadpoolctl import threadpool_limits

from .baseline import DATA_SHA, features, load_base, make_model, sha256
from .evaluation import Evidence, available_training_months, capacity_metrics, evidence_gate

POLICIES = ('frozen', 'scheduled', 'evidence')
MONTHS = tuple(range(2, 8))


def write_json(path, content):
    with Path(path).open('x') as stream:
        json.dump(content, stream, indent=2, allow_nan=False)
        stream.write('\n')


def replay(frame, output, model_factory=make_model):
    """Persist decisions/predictions with no final target access after boundary split.

    Public CLI additionally requires the exact dataset checksum and clean git tree.
    This frame entry point also supports tiny synthetic integration-test fixtures.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    # Hard boundary: downstream fitting and feedback get labels only through 5.
    past = frame.loc[frame.month <= 5].copy()
    batches = {m: frame.loc[frame.month == m].drop(columns='fraud_bool').copy() for m in MONTHS}
    del frame
    if any(b.empty for b in batches.values()) or not past.index.is_unique:
        raise ValueError('nonempty monthly batches and unique source positions required')
    fits, decisions, files, sentinel = [], [], {}, {}

    def fit(months, policy, at):
        train = past.loc[past.month.isin(months)]
        if set(train.fraud_bool) != {0, 1}:
            raise ValueError('training needs both labels')
        if any(m not in available_training_months(at) for m in months):
            raise ValueError('future training label')
        model = model_factory()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            started = time.perf_counter()
            model.fit(features(train), train.fraud_bool)
            elapsed = time.perf_counter() - started
        fits.append({'policy': policy, 'decision_month': at, 'training_months': list(months),
                     'rows': len(train), 'seconds': elapsed,
                     'warnings': [str(w.message) for w in caught]})
        return model

    with threadpool_limits(limits=1):
        initial = fit((0,), 'shared_initial', 2)
        models = {p: initial for p in POLICIES}
        trained_on = {p: [0] for p in POLICIES}
        last_refit = None
        for month in MONTHS:
            available = available_training_months(month)
            feedback = []
            for previous in sorted(sentinel):
                if previous not in available:
                    continue
                labels = past.loc[past.month == previous, 'fraud_bool'].tolist()
                metrics = capacity_metrics(labels, sentinel[previous].tolist())
                feedback.append(Evidence(previous, metrics['positives'], metrics['captured']))
            reference = next((e for e in feedback if e.month == 2), None)
            if reference is None:
                trigger, reason = False, 'reference_not_available'
            else:
                trigger, reason = evidence_gate(month, reference,
                    [e for e in feedback if e.month > 2], last_refit)
            for policy in POLICIES:
                refit = (policy == 'scheduled' and month >= 4) or (policy == 'evidence' and trigger)
                decision = {
                    'month': month, 'policy': policy, 'action': 'refit' if refit else 'hold',
                    'available_label_months': list(available),
                    'evidence_months': [e.month for e in feedback] if policy == 'evidence' else [],
                    'reason': reason if policy == 'evidence' else ('calendar' if refit else 'frozen_or_warmup'),
                    'training_months': list(available) if refit else trained_on[policy],
                }
                # Persist the action before fitting or predicting the current batch.
                decision_name = f'decision-{policy}-{month}.json'
                write_json(output / decision_name, decision)
                files[decision_name] = sha256(output / decision_name)
                decisions.append(decision)
                if refit:
                    models[policy] = fit(available, policy, month)
                    trained_on[policy] = list(available)
                    if policy == 'evidence':
                        last_refit = month
                batch = batches[month]
                probabilities = models[policy].predict_proba(features(batch))[:, 1]
                if not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
                    raise ValueError('invalid predicted probabilities')
                name = f'predictions-{policy}-{month}.csv'
                pd.DataFrame({'source_position': batch.index, 'score': probabilities}).to_csv(
                    output / name, index=False)
                files[name] = sha256(output / name)
                if policy == 'frozen':
                    sentinel[month] = probabilities.copy()
    return {'protocol': '1.1', 'delay': 1, 'capacity_fraction': 0.01,
            'dataset_sha256': DATA_SHA, 'final_labels_used_in_decisions': False,
            'fits': fits, 'decisions': decisions, 'files': files}


def score_final(frame, output, manifest):
    """Validate artifacts, then score saved predictions without fitting anything."""
    output = Path(output)
    expected = {f'{kind}-{p}-{m}.{ext}' for p in POLICIES for m in MONTHS
                for kind, ext in [('decision', 'json'), ('predictions', 'csv')]}
    if set(manifest['files']) != expected or manifest['dataset_sha256'] != DATA_SHA:
        raise ValueError('unexpected manifest')
    for name, digest in manifest['files'].items():
        if sha256(output / name) != digest:
            raise ValueError('artifact changed since prediction: ' + name)
    rows = []
    for policy in POLICIES:
        for month in (6, 7):
            batch = frame.loc[frame.month == month]
            stored = pd.read_csv(output / f'predictions-{policy}-{month}.csv', float_precision='round_trip')
            if stored.columns.tolist() != ['source_position', 'score'] or stored.source_position.tolist() != batch.index.tolist():
                raise ValueError('prediction/source alignment failure')
            y, scores = batch.fraud_bool.tolist(), stored.score.tolist()
            metrics = capacity_metrics(y, scores)
            metrics.pop('selected_positions')
            metrics.update(policy=policy, month=month,
                           average_precision=float(average_precision_score(y, scores)) if sum(y) else None,
                           brier_score=float(brier_score_loss(y, scores)))
            rows.append(metrics)
    pooled = []
    for policy in POLICIES:
        subset = [row for row in rows if row['policy'] == policy]
        total = {key: sum(r[key] for r in subset) for key in
                 ('n', 'positives', 'k', 'captured', 'false_positives')}
        total.update(policy=policy,
                     precision_at_k=total['captured'] / total['k'] if total['k'] else None,
                     recall_at_k=total['captured'] / total['positives'] if total['positives'] else None,
                     refits=sum(f['policy'] == policy for f in manifest['fits']),
                     refit_seconds=sum(f['seconds'] for f in manifest['fits'] if f['policy'] == policy))
        pooled.append(total)
    return {'protocol': '1.1', 'months': [6, 7], 'monthly': rows, 'pooled_counts': pooled,
            'note': 'Synthetic BAF, two held-out months; no causal savings or significance claim. '
                    'Refit costs cover the entire replay, months 4–7; initial fit excluded.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['predict', 'score'])
    parser.add_argument('--data', default='data/Base.csv')
    parser.add_argument('--output', default='artifacts/replay-v1.1')
    args = parser.parse_args()
    output = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if output.resolve() == root or not output.resolve().is_relative_to(root):
        raise ValueError('output must be a subdirectory of ./artifacts')
    if args.stage == 'predict':
        if subprocess.check_output(['git', 'status', '--porcelain']).strip():
            raise ValueError('commit the implementation before generating final predictions')
        frame = load_base(args.data)
        manifest = replay(frame, output)
        manifest.update(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                        python=platform.python_version(),
                        packages={p: version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'threadpoolctl']},
                        source_hashes={str(p): sha256(p) for p in [Path('requirements.txt'), Path('docs/PROTOCOL.md'),
                            Path('fraud_model_watch/replay.py'), Path('fraud_model_watch/baseline.py'),
                            Path('fraud_model_watch/evaluation.py')]})
        write_json(output / 'manifest.json', manifest)
        print(json.dumps({'stage': 'predicted', 'manifest_sha256': sha256(output / 'manifest.json'),
                          'fits': manifest['fits'], 'final_metrics': 'not computed'}, indent=2))
    else:
        if (output / 'final-report.json').exists():
            raise ValueError('final report already exists')
        manifest = json.loads((output / 'manifest.json').read_text())
        for name, digest in manifest['source_hashes'].items():
            if sha256(name) != digest:
                raise ValueError('implementation changed after predictions')
        result = score_final(load_base(args.data), output, manifest)
        result['manifest_sha256'] = sha256(output / 'manifest.json')
        write_json(output / 'final-report.json', result)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
