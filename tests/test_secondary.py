import unittest

from fraud_model_watch.evaluation import Evidence, evidence_gate
from fraud_model_watch.secondary import gate, run
from fraud_model_watch.stress import deterministic_scenarios
from test_replay import fixture, FakeModel


class SecondaryTests(unittest.TestCase):
    def test_original_gate_agreement(self):
        for series in deterministic_scenarios().values():
            for decision in range(4, 14):
                history = [e for e in series if 2 < e.month <= decision - 2]
                self.assertEqual(gate(decision, series[0], history)[0],
                                 evidence_gate(decision, series[0], history)[0])

    def test_delay_two_reference_and_future_rejection(self):
        with self.assertRaises(ValueError):
            gate(6, Evidence(2, 1000, 200), [], delay=2)
        with self.assertRaises(ValueError):
            gate(6, Evidence(3, 1000, 200), [Evidence(4, 1000, 100)], delay=2)
        self.assertTrue(gate(8, Evidence(3, 1000, 200),
                       [Evidence(4, 1000, 100), Evidence(5, 1000, 100)], delay=2)[0])

    def test_timing_and_logical_refit_counts(self):
        result = run(fixture(), FakeModel, FakeModel)
        self.assertEqual(len(result['settings']), 6)
        self.assertEqual(len(result['physical_fits']), 7)  # month 0 plus five expanding fits plus forest
        for setting in result['settings']:
            d = setting['delay']
            self.assertEqual(setting['reference_month'], d + 1)
            for decision in setting['decisions']:
                self.assertLessEqual(max(decision['training_months']), decision['month'] - d - 1)
                self.assertTrue(all(m <= decision['month'] - d - 1 for m in decision['evidence_months']))
            scheduled = next(p for p in setting['pooled'] if p['policy'] == 'scheduled')
            self.assertEqual(scheduled['logical_refits'], 5 - d)

    def test_unavailable_labels_cannot_change_decisions_or_scores(self):
        frame = fixture()
        first = run(frame, FakeModel, FakeModel)
        frame.loc[frame.month >= 6, 'fraud_bool'] = 0
        second = run(frame, FakeModel, FakeModel)
        for before, after in zip(first['settings'], second['settings']):
            if before['delay'] >= 1:
                self.assertEqual(before['decisions'], after['decisions'])
                for a, b in zip(before['monthly'], after['monthly']):
                    # Brier with original fixture labels differs; decisions/training remain unchanged.
                    self.assertEqual(a['k'], b['k'])
                    self.assertEqual(a['prediction_sha256'], b['prediction_sha256'])
        # For d=0 only month 7 may use month 6 labels; month 7 labels never feed training.
        d0 = first['settings'][0]
        train7 = next(d for d in d0['decisions'] if d['month'] == 7 and d['policy'] == 'scheduled')
        self.assertEqual(train7['training_months'], list(range(7)))


if __name__ == '__main__':
    unittest.main()
