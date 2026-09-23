import unittest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "04_SANDBOX_ENGINE"))
from sandbox_engine import System, State, step

class TestSandboxEngine(unittest.TestCase):
    def test_on_real_low_assist(self):
        s = System(pin_raw=10, paux=0, L_M2=0.5, topology_loss_base=0.5, state=State.START)
        s = step(s)
        self.assertIn(s.state, {State.ON, State.HOLD})
        self.assertLess(s.assisted_ratio, 0.2)
        self.assertGreaterEqual(s.truth_score, 0.5)

    def test_false_on_assisted(self):
        s = System(pin_raw=1, paux=10, L_M2=0.1, topology_loss_base=0.1, state=State.START)
        s = step(s)
        self.assertIn(s.state, {State.FALSE_ON, State.REJECTED})
        self.assertGreater(s.assisted_ratio, 0.5)

    def test_hold_low_input(self):
        s = System(pin_raw=0.3, paux=0, L_M2=0.0, state=State.ON)
        s = step(s)
        self.assertIn(s.state, {State.HOLD, State.OFF})

    def test_saturation_loss(self):
        s = System(pin_raw=100, M3_sat_high=10, L_M2=0, topology_loss_base=0, state=State.START)
        s = step(s)
        self.assertLess(s.delta_g, 1.0)

if __name__ == "__main__":
    unittest.main()
