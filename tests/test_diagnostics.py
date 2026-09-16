import tempfile
import unittest
from pathlib import Path

from fraud_model_watch.diagnostics import calibration, group_metrics, paired_bootstrap, run
from fraud_model_watch.replay import replay, write_json
from test_replay import FakeModel, fixture


class DiagnosticsTests(unittest.TestCase):
    def test_calibration_edges_and_empty_bins(self):
        rows = calibration([0, 1, 1, 0], [0, .1, .95, 1])
        self.assertEqual([rows[i]['count'] for i in (0, 1, 9)], [1, 1, 2])
        self.assertEqual(rows[9]['mean_probability'], .975)
        self.assertEqual(rows[9]['positive_fraction'], .5)
        self.assertIsNone(rows[2]['mean_probability'])
        self.assertEqual(sum(r['count'] for r in rows), 4)

    def test_groups_do_not_rerank(self):
        result = group_metrics([1, 0, 1, 0], [True, True, False, False])
        self.assertEqual(result['captured'], 1)
        self.assertEqual(result['recall'], .5)
        self.assertEqual(result['false_positive_selection_rate'], .5)
        self.assertIsNone(group_metrics([], [])['recall'])

    def test_bootstrap_zero_and_determinism(self):
        self.assertEqual(paired_bootstrap([[0, 0], [0]])['percentile_ci95'], [0, 0])
        first = paired_bootstrap([[1, -1, 0], [1, 0]])
        self.assertEqual(first, paired_bootstrap([[1, -1, 0], [1, 0]]))
        self.assertEqual(first['observed_difference'], 1)
        with self.assertRaises(ValueError):
            paired_bootstrap([[2]])

    def test_full_diagnostics_conserve_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'replay'
            frame = fixture()
            manifest = replay(frame, output, FakeModel)
            write_json(output / 'manifest.json', manifest)
            result = run(frame, output, manifest)
            self.assertEqual(len(result['hypothetical_utility']), 27)
            self.assertEqual(result['bootstrap']['observed_difference'], 0)
            frozen = [r for r in result['pooled_groups'] if r['policy'] == 'frozen']
            self.assertEqual(sum(r['n'] for r in frozen), 200)
            self.assertEqual(sum(r['reviewed'] for r in frozen), 2)


if __name__ == '__main__':
    unittest.main()
