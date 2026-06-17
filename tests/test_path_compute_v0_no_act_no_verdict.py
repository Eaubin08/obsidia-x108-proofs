import unittest

from path_compute_v0.boundary import PATH_COMPUTE_V0_BOUNDARY as B


class TestPathComputeV0NoActNoVerdict(unittest.TestCase):
    def test_no_action_or_gate_output(self):
        self.assertFalse(B.emits_act)
        self.assertFalse(B.emits_verdict)
        self.assertFalse(B.emits_allow_hold_block)
        self.assertFalse(B.constructs_canonical_envelope)


if __name__ == "__main__":
    unittest.main()
