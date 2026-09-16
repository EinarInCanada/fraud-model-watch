import unittest

from fraud_model_watch.demo import run as demo
from fraud_model_watch.faults import run as faults


class FaultDemoTests(unittest.TestCase):
    def test_contract_checks_and_silent_shifts(self):
        result = faults()
        self.assertEqual(len(result['rejected_cases']), 8)
        self.assertTrue(all(r['rejected'] for r in result['rejected_cases']))
        self.assertEqual(len(result['accepted_cases']), 3)
        self.assertTrue(all(not r['rejected'] and not r['drift_alarm_implemented']
                            and r['finite_scores'] for r in result['accepted_cases']))
        shifted = next(r for r in result['accepted_cases'] if r['case'] == 'finite_numeric_shift')
        self.assertGreater(shifted['maximum_absolute_score_change'], 0)

    def test_demo_expected_request_timeline(self):
        rows = {r['scenario']: r for r in demo()['scenarios']}
        self.assertEqual(rows['stable']['requests'], [])
        self.assertEqual(rows['abrupt']['requests'], [8, 10, 12])
        self.assertEqual(rows['recovery']['requests'], [8])
        self.assertEqual(rows['sparse']['requests'], [])
        for row in rows.values():
            for obs in row['observations']:
                self.assertEqual(obs['labels_available_at'], obs['event_month'] + 2)


if __name__ == '__main__':
    unittest.main()
