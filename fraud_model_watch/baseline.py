"""Pinned-data development baseline; intentionally cannot score final months."""
import argparse
import csv
import hashlib
import json
import platform
import time
import warnings
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from .evaluation import capacity_metrics

DATA_SHA = "7bf10a37ce07e72e14c1b09e5efee3d27261baff4facc7da767b0474dcf9b809"
CATEGORICAL = ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']
NUMERIC = [
    'income', 'name_email_similarity', 'prev_address_months_count',
    'current_address_months_count', 'customer_age', 'intended_balcon_amount',
    'zip_count_4w', 'velocity_6h', 'velocity_24h', 'velocity_4w',
    'bank_branch_count_8w', 'date_of_birth_distinct_emails_4w', 'email_is_free',
    'phone_home_valid', 'phone_mobile_valid', 'bank_months_count',
    'has_other_cards', 'proposed_credit_limit', 'foreign_request',
    'session_length_in_minutes', 'keep_alive_session', 'device_distinct_emails_8w',
]
EXCLUDED = ['month', 'fraud_bool', 'days_since_request', 'credit_risk_score', 'device_fraud_count']
MISSING_MINUS_ONE = ['prev_address_months_count', 'current_address_months_count',
                     'bank_months_count', 'session_length_in_minutes', 'device_distinct_emails_8w']


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_frame(frame, production=True):
    if frame.columns.duplicated().any() or set(frame.columns) != set(NUMERIC + CATEGORICAL + EXCLUDED):
        raise ValueError('unexpected BAF schema')
    if frame.empty:
        raise ValueError('empty input')
    for column in NUMERIC + EXCLUDED:
        values = pd.to_numeric(frame[column], errors='raise')
        if not np.isfinite(values).all():
            raise ValueError(f'nonfinite value in {column}')
    if not frame.fraud_bool.isin([0, 1]).all():
        raise ValueError('invalid fraud labels')
    if not frame.month.isin(range(8)).all():
        raise ValueError('invalid month')
    if frame[CATEGORICAL].isna().any().any():
        raise ValueError('missing categorical value')
    if production and (len(frame) != 1_000_000 or set(frame.month) != set(range(8))):
        raise ValueError('unexpected row count or month support')


def load_base(path):
    if sha256(path) != DATA_SHA:
        raise ValueError('BAF v2 Base checksum mismatch')
    with Path(path).open(newline='') as stream:
        header = next(csv.reader(stream))
    if len(header) != len(set(header)):
        raise ValueError('duplicate source column')
    frame = pd.read_csv(path)
    validate_frame(frame)
    return frame


def features(frame):
    result = frame[NUMERIC + CATEGORICAL].copy()
    for column in MISSING_MINUS_ONE:
        result[column] = result[column].mask(result[column] == -1)
    result['intended_balcon_amount'] = result.intended_balcon_amount.mask(result.intended_balcon_amount < 0)
    return result


def make_model():
    numeric = Pipeline([('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
                        ('scale', StandardScaler())])
    preprocess = ColumnTransformer([
        ('numeric', numeric, NUMERIC),
        ('categorical', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL),
    ], remainder='drop')
    return Pipeline([('preprocess', preprocess), ('model', LogisticRegression(
        C=1.0, solver='lbfgs', max_iter=1000, tol=1e-4, class_weight=None, random_state=42))])


def training_frame(frame):
    train = frame.loc[frame.month == 0]
    if set(train.fraud_bool) != {0, 1}:
        raise ValueError('month 0 must contain both classes')
    return train


def run(path, output):
    output = Path(output)
    # Avoid accidentally publishing individual prediction files under tracked paths.
    artifact_root = (Path.cwd() / 'artifacts').resolve()
    if not output.resolve().is_relative_to(artifact_root) or output.resolve() == artifact_root:
        raise ValueError('output must be a new subdirectory of ./artifacts')
    if output.exists():
        raise ValueError('output already exists; use a new run directory')
    frame = load_base(path)
    train = training_frame(frame)
    model = make_model()
    output.mkdir(parents=True)
    with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=1):
        warnings.simplefilter('always')
        started = time.perf_counter()
        model.fit(features(train), train.fraud_bool)
        fit_seconds = time.perf_counter() - started
        results, prediction_hashes = [], {}
        for month in (2, 3, 4, 5):
            batch = frame.loc[frame.month == month]
            probabilities = model.predict_proba(features(batch))[:, 1]
            prediction_path = output / f'sentinel-month-{month}.csv'
            # Store predictions before using outcomes to calculate metrics.
            pd.DataFrame({'source_position': batch.index, 'score': probabilities}).to_csv(
                prediction_path, index=False)
            prediction_hashes[str(month)] = sha256(prediction_path)
            labels = batch.fraud_bool.to_numpy()
            metrics = capacity_metrics(labels.tolist(), probabilities.tolist())
            metrics.pop('selected_positions')
            metrics.update(month=month,
                           average_precision=float(average_precision_score(labels, probabilities)),
                           brier_score=float(brier_score_loss(labels, probabilities)))
            results.append(metrics)
    report = {
        'protocol': '1.1', 'scope': 'reference/development only; NOT final performance',
        'dataset_sha256': DATA_SHA, 'rows_validated': len(frame), 'columns_validated': len(frame.columns),
        'training_months': [0], 'training_rows': len(train), 'scored_months': [2, 3, 4, 5],
        'final_months_scored': [], 'features': NUMERIC + CATEGORICAL,
        'fit_seconds': fit_seconds, 'initial_fits': 1, 'refits': 0,
        'iterations': model['model'].n_iter_.tolist(),
        'warnings': [{'category': w.category.__name__, 'message': str(w.message)} for w in caught],
        'python': platform.python_version(),
        'packages': {name: version(name) for name in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'threadpoolctl']},
        'threads': 1, 'prediction_sha256': prediction_hashes, 'results': results,
    }
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/Base.csv')
    parser.add_argument('--output', default='artifacts/baseline-v1.1')
    args = parser.parse_args()
    run(args.data, args.output)
