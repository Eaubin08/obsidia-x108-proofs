import unittest

from path_compute_v0.boundary import PATH_COMPUTE_V0_BOUNDARY as B


class TestPathComputeV0NoExternalCall(unittest.TestCase):
    def test_no_external_surface(self):
        self.assertFalse(B.calls_mcp)
        self.assertFalse(B.binds_graphiti)
        self.assertFalse(B.binds_neo4j)
        self.assertFalse(B.external_network_call)
        self.assertFalse(B.subprocess_allowed)


if __name__ == "__main__":
    unittest.main()
