import unittest

from path_compute_v0.boundary import PATH_COMPUTE_V0_BOUNDARY as B


class TestPathComputeV0NoMutation(unittest.TestCase):
    def test_no_state_mutation(self):
        self.assertFalse(B.mutates_kernel)
        self.assertFalse(B.mutates_domain_state)
        self.assertFalse(B.writes_memory)


if __name__ == "__main__":
    unittest.main()
