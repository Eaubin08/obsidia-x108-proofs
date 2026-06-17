import unittest

from path_compute_v0.boundary import PATH_COMPUTE_V0_BOUNDARY as B


class TestPathComputeV0BoundaryNonExecutable(unittest.TestCase):
    def test_authority_is_not_path_compute(self):
        self.assertEqual(B.decision_authority, "KX108_ONLY")
        self.assertEqual(B.path_compute_authority, "NONE")

    def test_runtime_is_disabled(self):
        self.assertFalse(B.runtime_enabled)
        self.assertFalse(B.implementation_allowed_now)
        self.assertFalse(B.activation_allowed_now)


if __name__ == "__main__":
    unittest.main()
