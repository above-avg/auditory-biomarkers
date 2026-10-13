"""Behavioral tests for participant separation and held-out target isolation."""
import unittest
import numpy as np
import pandas as pd
from analysis import FEATURES
from extended_analysis import predict_fold


class TestHeldOutGate(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(23)
        self.data = pd.DataFrame(rng.normal(size=(24, len(FEATURES))), columns=FEATURES)
        self.data['subject'] = np.repeat([1,2,3,4],6)
        self.data['abs_rmssd_error'] = rng.uniform(0,80,24)
        self.train = self.data[self.data.subject != 4].copy()
        self.test = self.data[self.data.subject == 4].copy()

    def test_heldout_targets_cannot_change_scores_or_threshold(self):
        score, threshold = predict_fold(self.train, self.test)
        self.test['abs_rmssd_error'] = 1e9
        new_score, new_threshold = predict_fold(self.train, self.test)
        np.testing.assert_array_equal(score, new_score)
        self.assertEqual(threshold,new_threshold)

    def test_heldout_features_cannot_change_training_threshold(self):
        _, threshold = predict_fold(self.train, self.test)
        self.test.loc[:,FEATURES] *= 1000
        _, new_threshold = predict_fold(self.train,self.test)
        self.assertEqual(threshold,new_threshold)

    def test_overlapping_participants_are_rejected(self):
        with self.assertRaises(ValueError):
            predict_fold(self.train,self.train.iloc[:2])

    def test_rule_does_not_need_error_targets(self):
        a,t = predict_fold(self.train,self.test,rule='periodicity')
        b,u = predict_fold(self.train.drop(columns='abs_rmssd_error'),
                           self.test.drop(columns='abs_rmssd_error'),rule='periodicity')
        np.testing.assert_array_equal(a,b)
        self.assertEqual(t,u)


if __name__ == '__main__':
    unittest.main()
