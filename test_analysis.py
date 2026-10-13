"""Scientific invariants and leakage boundaries, standard-library unittest."""
import unittest, ast
import numpy as np
from analysis import metrics, match_f1, acoustic, FEATURES

class TestScientificInvariants(unittest.TestCase):
    def test_constant_intervals(self):
        m=metrics(np.arange(0,30,.8))
        self.assertAlmostEqual(m['hr'],75)
        self.assertLess(m['rmssd'],1e-9)
    def test_electromechanical_identity(self):
        rng=np.random.default_rng(7)
        r=np.cumsum(rng.uniform(.5,1,40));d=rng.normal(.06,.01,40);s=r+d
        np.testing.assert_allclose(np.diff(s)-np.diff(r),np.diff(d),atol=1e-14)
    def test_constant_delay_preserves_rmssd(self):
        r=np.arange(3,26,.7)
        self.assertAlmostEqual(metrics(r)['rmssd'],metrics(r+.06)['rmssd'],places=8)
    def test_match_no_duplicate_credit(self):
        self.assertAlmostEqual(match_f1(np.array([1.,1.02]),np.array([1.])),2/3)
    def test_audio_interface_has_no_reference(self):
        import inspect
        self.assertEqual(list(inspect.signature(acoustic).parameters),['x','low','high'])
        self.assertTrue(all('ecg' not in x and 'guided' not in x for x in FEATURES))
    def test_synthetic_audio_period(self):
        fs=1000;t=np.arange(30000)/fs;x=np.zeros_like(t)
        for p in np.arange(.5,30,.8):
            x+=np.exp(-((t-p)/.025)**2)*np.sin(2*np.pi*65*t)
            x+=.6*np.exp(-((t-p-.25)/.020)**2)*np.sin(2*np.pi*85*t)
        events,_,_,_=acoustic(x)
        self.assertLess(abs(metrics(events)['hr']-75),1)
        self.assertLess(metrics(events)['rmssd'],5)

if __name__=='__main__':unittest.main()
