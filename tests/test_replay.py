import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from fraud_model_watch.baseline import NUMERIC, CATEGORICAL, EXCLUDED
from fraud_model_watch.replay import replay, score_final


class FakeModel:
    def fit(self, x, y):
        self.offset = float(y.mean()) / 100
        return self

    def predict_proba(self, x):
        probability = np.clip(x.income.to_numpy() / 1000 + self.offset, 0, 1)
        return np.column_stack((1 - probability, probability))


def fixture():
    size = 800
    frame = pd.DataFrame({c: np.ones(size) for c in NUMERIC + EXCLUDED})
    for c in CATEGORICAL:
        frame[c] = 'category'
    frame['month'] = np.repeat(np.arange(8), 100)
    frame['fraud_bool'] = np.tile([0, 1], 400)
    frame['income'] = np.arange(size)
    return frame


class ReplayTests(unittest.TestCase):
    def test_future_labels_do_not_change_actions_or_predictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            frame = fixture()
            first = replay(frame, Path(temporary) / 'first', FakeModel)
            changed = frame.copy()
            changed.loc[changed.month >= 6, 'fraud_bool'] = 0
            second = replay(changed, Path(temporary) / 'second', FakeModel)
            self.assertEqual(first['decisions'], second['decisions'])
            self.assertEqual(first['files'], second['files'])
            self.assertEqual([f['decision_month'] for f in first['fits'] if f['policy'] == 'scheduled'], [4, 5, 6, 7])
            for fit in first['fits']:
                self.assertLessEqual(max(fit['training_months']), fit['decision_month'] - 2)
            result = score_final(frame, Path(temporary) / 'first', first)
            self.assertEqual(len(result['monthly']), 6)
            self.assertEqual({r['k'] for r in result['pooled_counts']}, {2})

    def test_artifact_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            manifest = replay(fixture(), output, FakeModel)
            with (output / 'predictions-frozen-6.csv').open('a') as stream:
                stream.write('800,0.5\n')
            with self.assertRaisesRegex(ValueError, 'artifact changed'):
                score_final(fixture(), output, manifest)

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(FileExistsError):
                replay(fixture(), temporary, FakeModel)

    def test_manifest_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            manifest = replay(fixture(), output, FakeModel)
            manifest['files'].pop('decision-frozen-2.json')
            with self.assertRaisesRegex(ValueError, 'manifest'):
                score_final(fixture(), output, manifest)


if __name__ == '__main__':
    unittest.main()
