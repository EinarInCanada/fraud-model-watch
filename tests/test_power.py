import unittest

from fraud_model_watch.power import generate_series, run_suite, summarize_requests, design_candidates


class PowerTests(unittest.TestCase):
    def test_generator_matches_declared_rng_and_is_reproducible(self):
        import numpy as np
        actual = generate_series(100, 1, 3000)
        expected = np.random.default_rng(302003000).binomial(100, [.20] * 3 + [.16] * 7)
        self.assertEqual([e.captured for e in actual], expected.tolist())
        self.assertEqual(actual, generate_series(100, 1, 3000))
        self.assertEqual([e.month for e in actual], list(range(2, 12)))

    def test_counts_use_runs_not_number_of_requests(self):
        rows = [{'requests': [6, 8, 10], 'count': 3}, {'requests': [], 'count': 0}]
        result = summarize_requests(rows)
        self.assertEqual(result['any_request_count'], 1)
        self.assertEqual(result['pre_change_request_count'], 1)
        self.assertEqual(result['post_change_request_count'], 1)
        self.assertEqual(result['no_post_change_request_count'], 1)
        self.assertEqual(result['median_first_post_change_decision'], 8)
        self.assertEqual(result['first_post_change_decision_counts']['8'], 1)
        self.assertLess(result['any_request_ci95'][0], .5)
        self.assertGreater(result['any_request_ci95'][1], .5)

    def test_no_responses_have_no_conditional_timing(self):
        result = summarize_requests([{'requests': [], 'count': 0}])
        self.assertIsNone(result['median_first_post_change_decision'])
        self.assertEqual(sum(result['first_post_change_decision_counts'].values()), 0)

    def test_candidate_requires_both_criteria_and_uses_smallest_n(self):
        rows = []
        for n, stable, power in [(100, .06, 1), (200, .05, .8), (400, .01, .9)]:
            rows.extend([{'n': n, 'policy': 'persistence', 'regime': 'stable', 'any_request_fraction': stable},
                         {'n': n, 'policy': 'persistence', 'regime': 'eight_point_drop',
                          'post_change_request_fraction': power}])
        candidates = design_candidates(rows)
        self.assertIsNone(candidates[0]['first_tested_n_meeting_point_criteria'])
        self.assertEqual(candidates[1]['first_tested_n_meeting_point_criteria'], 200)

    def test_small_suite_complete_and_deterministic(self):
        result = run_suite(sizes=(30,), seeds=range(3000, 3003))
        self.assertEqual(len(result['rows']), 6)
        self.assertTrue(all(r['runs'] == 3 for r in result['rows']))
        self.assertEqual(result, run_suite(sizes=(30,), seeds=range(3000, 3003)))
        with self.assertRaises(ValueError):
            run_suite(seeds=[])


if __name__ == '__main__':
    unittest.main()
