"""Generated-fixture input contract checks, not drift detection on bank data."""
import argparse
import json
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .baseline import CATEGORICAL, EXCLUDED, NUMERIC, features, load_base, make_model, sha256, validate_frame
from .replay import write_json


def fixture():
    rng = np.random.default_rng(20260916)
    frame = pd.DataFrame({name: rng.uniform(.1, 1, 200) for name in NUMERIC + EXCLUDED})
    for name in CATEGORICAL:
        frame[name] = np.tile(['a', 'b'], 100)
    frame['month'] = np.repeat([0, 1], 100)
    frame['fraud_bool'] = np.tile([0, 1, 0, 0], 50)
    frame['customer_age'] = rng.choice([20, 30, 40, 50, 60], 200)
    return frame


def run():
    base = fixture()
    validate_frame(base, production=False)
    bad = {}
    bad['missing_column'] = base.drop(columns='income')
    bad['duplicate_column'] = pd.concat([base, base[['income']]], axis=1)
    for name, column, value in [('invalid_label', 'fraud_bool', 2),
                                 ('nonfinite_numeric', 'income', np.inf),
                                 ('missing_numeric', 'income', np.nan),
                                 ('missing_category', 'payment_type', None),
                                 ('invalid_month', 'month', 8)]:
        bad[name] = base.copy()
        bad[name].loc[0, column] = value
    results = []
    for name, frame in bad.items():
        try:
            validate_frame(frame, production=False)
        except (ValueError, TypeError) as error:
            results.append(dict(case=name, rejected=True, reason=str(error)))
        else:
            raise AssertionError('invalid fixture unexpectedly accepted: ' + name)
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'generated-fixture.csv'
        base.to_csv(path, index=False)
        try:
            load_base(path)
        except ValueError as error:
            if 'checksum' not in str(error):
                raise
            results.append(dict(case='unapproved_file_checksum', rejected=True, reason=str(error)))
        else:
            raise AssertionError('fixture passed pinned BAF hash')
    with threadpool_limits(limits=1):
        train = base.loc[base.month == 0]
        test = base.loc[base.month == 1].copy()
        model = make_model().fit(features(train), train.fraud_bool)
        original = model.predict_proba(features(test))[:, 1]
        accepted = []
        for name in ('unknown_category', 'finite_numeric_shift', 'declared_missing_sentinel'):
            changed = test.copy()
            if name == 'unknown_category':
                changed['payment_type'] = 'never_seen_at_fit'
            elif name == 'finite_numeric_shift':
                changed['velocity_6h'] += 1000
            else:
                changed['prev_address_months_count'] = -1
            validate_frame(changed, production=False)
            score = model.predict_proba(features(changed))[:, 1]
            if not np.isfinite(score).all():
                raise AssertionError('nonfinite prediction')
            accepted.append(dict(case=name, rejected=False, finite_scores=True,
                maximum_absolute_score_change=float(np.abs(score - original).max()),
                drift_alarm_implemented=False))
    return dict(provenance='generated 200-row fixture; no BAF applications or real incidents',
                rejected_cases=results, accepted_cases=accepted,
                limitations='Pinned-file hash rejects any different file, not diagnoses drift. '
                'Schema-only checks accept unknown categories and finite shifts. '
                'Finite probabilities do not imply valid predictions or acceptable performance.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/faults.json')
    args = parser.parse_args()
    path = Path(args.output)
    root = (Path.cwd() / 'artifacts').resolve()
    if path.exists() or path.resolve() == root or not path.resolve().is_relative_to(root):
        raise ValueError('choose a new file under ./artifacts')
    result = run()
    result['source_sha256'] = {p: sha256(p) for p in ['fraud_model_watch/faults.py',
        'fraud_model_watch/baseline.py', 'requirements.txt', 'docs/COMPLETION_PLAN.md']}
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, result)
    print(json.dumps(result, indent=2))
