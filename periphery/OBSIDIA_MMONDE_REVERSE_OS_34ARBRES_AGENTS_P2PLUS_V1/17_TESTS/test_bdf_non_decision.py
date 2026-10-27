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
class TestBDF(unittest.TestCase):
    def test_bdf(self):
        mod = load_module("bdf_mod", "07_BDF_DOUBLE_CERVEAU/bdf_response.py")
        self.assertEqual(mod.compute_response(0.5,0.5,1,1), 1.0)
        self.assertTrue(mod.compute_bdf()["non_decision"])
if __name__ == "__main__":
    unittest.main()
