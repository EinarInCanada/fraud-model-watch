"""Predeclared exploratory BAF sensitivities; primary final labels already seen."""
import argparse
import hashlib
import json
import platform
import time
import warnings
from importlib.metadata import version
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, brier_score_loss
from threadpoolctl import threadpool_limits

from .baseline import DATA_SHA, features, load_base, make_model, sha256
from .evaluation import Evidence, available_training_months, capacity_metrics
from .replay import write_json
from .uncertainty import ALPHA, COMPARISONS, decline_pvalue

CONFIGS = ((0, .01), (1, .01), (2, .01), (1, .005), (1, .02), (1, .05))
POLICIES = ('frozen', 'scheduled', 'evidence', 'fisher_bonferroni')


def gate(decision, reference, history, last_refit=None, *, delay=1, corrected=False):
    available = available_training_months(decision, delay)
    history = tuple(history)
    if reference.month != delay + 1 or reference.month not in available:
        raise ValueError('invalid or unavailable reference')
    if any(e.month not in available or e.month <= reference.month for e in history):
        raise ValueError('invalid or unavailable history')
    if len({e.month for e in history}) != len(history):
        raise ValueError('duplicate history')
    if last_refit is not None:
        if last_refit >= decision:
            raise ValueError('invalid last refit')
        if decision - last_refit < 2:
            return False, 'cooldown'
    by_month = {e.month: e for e in history}
    latest = decision - delay - 1
    if latest - 1 <= reference.month or not all(m in by_month for m in (latest - 1, latest)):
        return False, 'insufficient_post_reference_evidence'
    recent = [by_month[latest - 1], by_month[latest]]
    if min(e.positives for e in (reference, *recent)) < 30:
        return False, 'insufficient_positive_labels'
    if not all(20 * (reference.captured * e.positives - e.captured * reference.positives)
               >= reference.positives * e.positives for e in recent):
        return False, 'hold'
    if corrected and not all(decline_pvalue(reference.positives, reference.captured,
                                            e.positives, e.captured) <= ALPHA / COMPARISONS
                             for e in recent):
        return False, 'insufficient_statistical_evidence'
    return True, 'persistent_drop_with_fisher_evidence' if corrected else 'persistent_drop'


def make_forest():
    model = make_model()
    model.set_params(model=RandomForestClassifier(n_estimators=100, max_depth=8,
                     min_samples_leaf=20, class_weight=None, random_state=42, n_jobs=1))
    return model


def metrics(labels, probabilities, fraction):
    result = capacity_metrics(labels.tolist(), probabilities.tolist(), fraction)
    result.pop('selected_positions')
    return dict(result, prediction_sha256=hashlib.sha256(np.asarray(probabilities, dtype='<f8').tobytes()).hexdigest(),
                average_precision=float(average_precision_score(labels, probabilities))
                if sum(labels) else None, brier_score=float(brier_score_loss(labels, probabilities)))


def run(frame, model_factory=make_model, forest_factory=make_forest):
    if not frame.index.is_unique or set(frame.month) != set(range(8)):
        raise ValueError('unique positions and all eight months required')
    # Feature-only batches; labels are accessed by fit/feedback only after maturity checks.
    batches = {m: features(frame.loc[frame.month == m]) for m in range(8)}
    cache, scores, physical_fits = {}, {}, []

    def fit(months, decision, delay, kind='logistic'):
        if any(m not in available_training_months(decision, delay) for m in months):
            raise ValueError('future training label')
        key = (kind, tuple(months))
        if key not in cache:
            train = frame.loc[frame.month.isin(months)]
            if set(train.fraud_bool) != {0, 1}:
                raise ValueError('training needs both labels')
            model = model_factory() if kind == 'logistic' else forest_factory()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                started = time.perf_counter()
                model.fit(features(train), train.fraud_bool)
                seconds = time.perf_counter() - started
            cache[key] = model
            physical_fits.append(dict(kind=kind, training_months=list(months), rows=len(train),
                                      seconds=seconds, warnings=[str(w.message) for w in caught]))
        return key

    def predict(key, month):
        token = (key, month)
        if token not in scores:
            value = cache[key].predict_proba(batches[month])[:, 1]
            if not np.isfinite(value).all() or ((value < 0) | (value > 1)).any():
                raise ValueError('invalid probabilities')
            scores[token] = value
        return scores[token]

    settings = []
    with threadpool_limits(limits=1):
        for delay, fraction in CONFIGS:
            reference_month = delay + 1
            initial = fit((0,), reference_month, delay)
            keys = {p: initial for p in POLICIES}
            last = {p: None for p in POLICIES}
            decisions, predictions, evidence = [], {}, {}
            for month in range(reference_month, 8):
                available = available_training_months(month, delay)
                for previous in range(reference_month, month):
                    if previous in available and previous not in evidence:
                        y = frame.loc[frame.month == previous, 'fraud_bool']
                        counts = capacity_metrics(y.tolist(), predict(initial, previous).tolist(), fraction)
                        evidence[previous] = Evidence(previous, counts['positives'], counts['captured'])
                for policy in POLICIES:
                    trigger, reason = False, 'frozen_or_warmup'
                    if policy == 'scheduled' and month >= reference_month + 2:
                        trigger, reason = True, 'calendar'
                    elif policy in ('evidence', 'fisher_bonferroni'):
                        if reference_month not in evidence:
                            reason = 'reference_not_available'
                        else:
                            trigger, reason = gate(month, evidence[reference_month],
                                [e for m, e in evidence.items() if m > reference_month], last[policy],
                                delay=delay, corrected=policy == 'fisher_bonferroni')
                    training = tuple(available) if trigger else keys[policy][1]
                    decisions.append(dict(month=month, policy=policy, refit=trigger, reason=reason,
                        training_months=list(training), available_label_months=list(available),
                        evidence_months=sorted(evidence) if policy in ('evidence', 'fisher_bonferroni') else []))
                    if trigger:
                        keys[policy] = fit(training, month, delay)
                        last[policy] = month
                    if month in (6, 7):
                        predictions[policy, month] = predict(keys[policy], month)
            # Outcomes used after this setting's decisions; no tuning/selection from metrics.
            monthly, pooled = [], []
            for policy in POLICIES:
                rows = [dict(policy=policy, month=m, **metrics(frame.loc[frame.month == m, 'fraud_bool'],
                        predictions[policy, m], fraction)) for m in (6, 7)]
                monthly.extend(rows)
                totals = {k: sum(r[k] for r in rows) for k in ('n', 'positives', 'k', 'captured', 'false_positives')}
                pooled.append(dict(policy=policy, **totals,
                    recall_at_k=totals['captured'] / totals['positives'] if totals['positives'] else None,
                    precision_at_k=totals['captured'] / totals['k'] if totals['k'] else None,
                    logical_refits=sum(d['refit'] for d in decisions if d['policy'] == policy)))
            settings.append(dict(delay=delay, capacity_fraction=fraction, reference_month=reference_month,
                                 decisions=decisions, monthly=monthly, pooled=pooled))
        forest = fit((0,), 2, 1, kind='forest')
        initial = fit((0,), 2, 1)
        complexity = [dict(model=kind, month=m, **metrics(frame.loc[frame.month == m, 'fraud_bool'],
                      predict(key, m), .01)) for kind, key in [('logistic', initial), ('forest', forest)]
                      for m in (6, 7)]
    return dict(scope='exploratory; primary final outcomes already seen; no winning setting selected',
                settings=settings, complexity=complexity, physical_fits=physical_fits,
                cache_note='identical training-month sets reuse a deterministic fitted model; logical refits count policy actions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/Base.csv')
    parser.add_argument('--output', default='artifacts/secondary.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new file under ./artifacts')
    result = run(load_base(args.data))
    result.update(dataset_sha256=DATA_SHA, python=platform.python_version(),
                  packages={p: version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'scipy']},
                  source_sha256={p: sha256(p) for p in ['fraud_model_watch/secondary.py',
                      'fraud_model_watch/baseline.py', 'fraud_model_watch/evaluation.py',
                      'fraud_model_watch/uncertainty.py', 'docs/COMPLETION_PLAN.md', 'requirements.txt']})
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, result)
    print(json.dumps({'settings': [{k: v for k, v in s.items() if k in
          ('delay', 'capacity_fraction', 'pooled')} for s in result['settings']],
          'complexity': result['complexity'], 'physical_fits': result['physical_fits']}, indent=2))
