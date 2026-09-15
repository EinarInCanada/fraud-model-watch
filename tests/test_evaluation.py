import unittest

from fraud_model_watch.evaluation import (
    Evidence, available_training_months, capacity_metrics,
    evidence_gate, label_available_at,
)


class TimingTests(unittest.TestCase):
    def test_clock(self):
        self.assertEqual(label_available_at(2), 4)
        self.assertEqual(label_available_at(2, 0), 3)

    def test_final_test_labels_excluded(self):
        self.assertEqual(available_training_months(6), (0, 1, 2, 3, 4))
        self.assertNotIn(6, available_training_months(7))

    def test_boundary(self):
        self.assertEqual(available_training_months(0), ())
        self.assertEqual(available_training_months(7, 0)[-1], 6)

    def test_invalid(self):
        for value in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                label_available_at(value)


class RankingTests(unittest.TestCase):
    def test_counts_and_ties(self):
        result = capacity_metrics([0, 1, 1, 0], [0.9, 0.9, 0.8, 0.1], 0.5)
        self.assertEqual(result["selected_positions"], [0, 1])
        self.assertEqual(result["captured"], 1)
        self.assertEqual(result["false_positives"], 1)
        self.assertEqual(result["recall_at_k"], 0.5)

    def test_labels_cannot_change_selection(self):
        first = capacity_metrics([0, 1], [0.5, 0.5], 0.5)
        second = capacity_metrics([1, 0], [0.5, 0.5], 0.5)
        self.assertEqual(first["selected_positions"], second["selected_positions"])

    def test_undefined_and_empty(self):
        result = capacity_metrics([0], [0.2])
        self.assertIsNone(result["precision_at_k"])
        self.assertIsNone(result["recall_at_k"])
        self.assertEqual(capacity_metrics([], [])["n"], 0)

    def test_reject_invalid_inputs(self):
        for labels, scores, budget in [([1], [], 1), ([2], [0.1], 1),
                                      ([1], [float("nan")], 1),
                                      ([1], [1.1], 1), ([1], [0.1], 0)]:
            with self.assertRaises(ValueError):
                capacity_metrics(labels, scores, budget)


class GateTests(unittest.TestCase):
    reference = Evidence(2, 100, 50)

    def test_exact_threshold(self):
        self.assertEqual(evidence_gate(6, self.reference,
                         [Evidence(3, 100, 45), Evidence(4, 100, 45)]),
                         (True, "persistent_recall_drop"))

    def test_single_bad_month_not_enough(self):
        self.assertFalse(evidence_gate(6, self.reference,
                         [Evidence(3, 100, 49), Evidence(4, 100, 30)])[0])

    def test_stale_or_missing_months(self):
        self.assertFalse(evidence_gate(7, self.reference,
                         [Evidence(3, 100, 30), Evidence(4, 100, 30)])[0])

    def test_future_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, "future-label"):
            evidence_gate(6, self.reference, [Evidence(5, 100, 30)])

    def test_small_denominator(self):
        self.assertEqual(evidence_gate(6, self.reference,
                         [Evidence(3, 29, 0), Evidence(4, 100, 30)])[1],
                         "insufficient_positive_labels")

    def test_cooldown(self):
        self.assertEqual(evidence_gate(7, self.reference,
                         [Evidence(4, 100, 30), Evidence(5, 100, 30)], 6)[1],
                         "cooldown")
        self.assertTrue(evidence_gate(7, self.reference,
                        [Evidence(4, 100, 30), Evidence(5, 100, 30)], 5)[0])

    def test_invalid_evidence(self):
        with self.assertRaises(ValueError):
            Evidence(3, 10, 11)
        with self.assertRaises(ValueError):
            evidence_gate(6, self.reference, [Evidence(3, 100, 30)] * 2)


if __name__ == "__main__":
    unittest.main()
