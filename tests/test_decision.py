# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('watch', Path(__file__).parents[1] / 'tools/edge_watch.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
def state(gen=1, width=4, target=2, training=False):
    return dict(gen=gen, width=width, target=target, training=training)
class DecisionTests(unittest.TestCase):
    def test_transition(self):
        self.assertEqual(w.decision(1, state(), state()), 'retrain')
    def test_no_transition(self):
        self.assertEqual(w.decision(2, state(), state()), 'wait')
    def test_already_gen2(self):
        self.assertEqual(w.decision(1, state(gen=2), state(gen=2)), 'already-gen2')
    def test_training(self):
        self.assertEqual(w.decision(1, state(training=True), state()), 'wait')
    def test_reject_bad_states(self):
        for gpu,root in [(state(width=1),state()),(state(gen=15),state()),(state(),state(gen=2)),(state(),state(target=3))]:
            with self.assertRaises(RuntimeError): w.decision(1,gpu,root)
if __name__ == '__main__': unittest.main()
