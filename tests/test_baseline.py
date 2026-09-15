import unittest
import numpy as np
import pandas as pd

from fraud_model_watch.baseline import (
    CATEGORICAL, NUMERIC, EXCLUDED, features, make_model, training_frame, validate_frame,
)


def fixture():
    frame = pd.DataFrame({name: [1., 2., 3., 4.] for name in NUMERIC + EXCLUDED})
    for name in CATEGORICAL:
        frame[name] = ['a', 'b', 'a', 'b']
    frame['month'] = [0, 0, 6, 7]
    frame['fraud_bool'] = [0, 1, 0, 1]
    return frame


class BaselineTests(unittest.TestCase):
    def test_schema(self):
        validate_frame(fixture(), production=False)
        with self.assertRaises(ValueError):
            validate_frame(fixture().drop(columns='income'), production=False)

    def test_invalid_values(self):
        for name, value in [('fraud_bool', 2), ('month', 8), ('income', np.inf)]:
            frame = fixture()
            frame.loc[0, name] = value
            with self.assertRaises(ValueError):
                validate_frame(frame, production=False)

    def test_no_final_training(self):
        self.assertEqual(training_frame(fixture()).index.tolist(), [0, 1])

    def test_exclusions(self):
        self.assertFalse(set(features(fixture()).columns) & set(EXCLUDED))

    def test_sentinels_and_no_mutation(self):
        frame = fixture()
        frame.loc[0, 'prev_address_months_count'] = -1
        frame.loc[0, 'intended_balcon_amount'] = -7
        frame.loc[0, 'velocity_6h'] = -7
        converted = features(frame)
        self.assertTrue(pd.isna(converted.loc[0, 'prev_address_months_count']))
        self.assertTrue(pd.isna(converted.loc[0, 'intended_balcon_amount']))
        self.assertEqual(converted.loc[0, 'velocity_6h'], -7)
        self.assertEqual(frame.loc[0, 'prev_address_months_count'], -1)

    def test_unknown_category_and_train_only_scaling(self):
        frame = fixture()
        model = make_model().fit(features(frame.iloc[:2]), frame.fraud_bool.iloc[:2])
        later = frame.iloc[2:].copy()
        later['payment_type'] = 'unseen'
        score = model.predict_proba(features(later))[:, 1]
        self.assertTrue(np.isfinite(score).all())
        mean = model['preprocess'].named_transformers_['numeric']['scale'].mean_[0]
        self.assertEqual(mean, 1.5)


if __name__ == '__main__':
    unittest.main()
