import json, sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load_module(name, relpath, add_path=None):
    if add_path:
        sys.path.insert(0, str(ROOT / add_path))
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

import unittest
class TestShazam(unittest.TestCase):
    def test_shazam(self):
        mod = load_module("shazam_mod", "05_SHAZAM_COGNITIF/shazam_cognitif.py", "05_SHAZAM_COGNITIF")
        out = mod.shazam("urgence cohérence preuve graphe X-108")
        self.assertIn("spectral_hash", out)
        self.assertEqual(len(out["tree_activation"]), 34)
        self.assertIn("metadata", out)
        self.assertIn("shazam_trees", out["metadata"])
        self.assertTrue(out["non_decision"])
if __name__ == "__main__":
    unittest.main()
