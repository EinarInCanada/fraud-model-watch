import unittest
from fraud_model_watch.evaluation import Evidence
from fraud_model_watch.stress import deterministic_scenarios, simulate, single_month_gate, stochastic_series, summarize


class StressTests(unittest.TestCase):
    def test_abrupt_delay_and_cooldown(self):
        series = deterministic_scenarios()['abrupt']
        self.assertEqual(simulate(series)['requests'], [8, 10, 12])
        self.assertEqual(simulate(series, single_month_gate)['requests'], [7, 9, 11, 13])

    def test_stable_and_transient(self):
        self.assertEqual(simulate(deterministic_scenarios()['stable'])['count'], 0)
        series = deterministic_scenarios()['transient']
        self.assertEqual(simulate(series)['count'], 0)
        self.assertEqual(simulate(series, single_month_gate)['requests'], [7])

    def test_sparse_and_missing(self):
        scenarios = deterministic_scenarios()
        self.assertEqual(simulate(scenarios['sparse'])['count'], 0)
        self.assertEqual(simulate(scenarios['missing'])['count'], 0)

    def test_recovery_is_detected_late(self):
        self.assertEqual(simulate(deterministic_scenarios()['recovery'])['requests'], [8])

    def test_future_change_does_not_affect_earlier_actions(self):
        first = deterministic_scenarios()['stable']
        second = [Evidence(e.month, e.positives, 0) if e.month >= 8 else e for e in first]
        self.assertEqual(simulate(first)['trace'][:6], simulate(second)['trace'][:6])
        for row in simulate(second)['trace']:
            self.assertTrue(all(m <= row['decision'] - 2 for m in row['evidence_months']))

    def test_reproducibility_and_summary(self):
        self.assertEqual(stochastic_series(30, 0, 42), stochastic_series(30, 0, 42))
        result = summarize([{'requests': [], 'count': 0}])
        self.assertIsNone(result['median_first_post_change_decision'])
        self.assertEqual(result['any_request_fraction'], 0)

    def test_future_ablation_evidence_rejected(self):
        with self.assertRaises(ValueError):
            single_month_gate(6, Evidence(2, 1000, 200), [Evidence(5, 1000, 120)], None)


if __name__ == '__main__':
    unittest.main()
