import unittest

from path_compute_v0 import PATH_COMPUTE_V0_ADVISORY_SURFACE
from path_compute_v0.boundary import PATH_COMPUTE_V0_BOUNDARY as B
from path_compute_v0.types import PathCandidateNote


class TestPathComputeV0AdvisoryOnly(unittest.TestCase):
    def test_advisory_surface(self):
        self.assertTrue(B.advisory_only)
        self.assertEqual(
            PATH_COMPUTE_V0_ADVISORY_SURFACE["mode"],
            "ADVISORY_ONLY_NON_SOVEREIGN",
        )

    def test_note_shape_is_readonly_advisory(self):
        note = PathCandidateNote(candidate_id="c0", label="readonly note")
        self.assertTrue(note.advisory_only)
        self.assertEqual(note.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
