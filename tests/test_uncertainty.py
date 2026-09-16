import unittest
from fraud_model_watch.evaluation import Evidence
from fraud_model_watch.uncertainty import decline_pvalue, uncertainty_gate, request_interval, ALPHA, COMPARISONS


class UncertaintyTests(unittest.TestCase):
    def test_exact_direction_and_value(self):
        self.assertAlmostEqual(decline_pvalue(10, 10, 10, 0), 1 / 184756)
        self.assertEqual(decline_pvalue(10, 0, 10, 10), 1)

    def test_large_drop_passes(self):
        reference = Evidence(2, 1000, 200)
        history = [Evidence(3, 1000, 120), Evidence(4, 1000, 120)]
        self.assertTrue(uncertainty_gate(6, reference, history)[0])

    def test_small_sample_observed_drop_not_enough(self):
        self.assertFalse(uncertainty_gate(6, Evidence(2, 30, 6),
                         [Evidence(3, 30, 3), Evidence(4, 30, 3)])[0])

    def test_future_and_horizon_rejected(self):
        with self.assertRaises(ValueError):
            uncertainty_gate(14, Evidence(2, 100, 20), [])
        with self.assertRaises(ValueError):
            uncertainty_gate(6, Evidence(2, 100, 20), [Evidence(5, 100, 1)])

    def test_corrected_implies_uncorrected(self):
        for captured in range(0, 200, 10):
            history = [Evidence(3, 1000, captured), Evidence(4, 1000, captured)]
            corrected = uncertainty_gate(6, Evidence(2, 1000, 200), history)[0]
            uncorrected = uncertainty_gate(6, Evidence(2, 1000, 200), history, corrected=False)[0]
            self.assertFalse(corrected and not uncorrected)
        self.assertAlmostEqual((ALPHA / COMPARISONS) * 9, 0.05)

    def test_zero_observed_not_zero_risk(self):
        low, high = request_interval(0, 500)
        self.assertEqual(low, 0)
        self.assertGreater(high, 0)
        self.assertLess(high, 0.01)

    def test_bad_counts(self):
        for args in [(0, 0, 10, 1), (10, 11, 10, 1), (10, 2, 10, -1)]:
            with self.assertRaises(ValueError):
                decline_pvalue(*args)


if __name__ == '__main__':
    unittest.main()
