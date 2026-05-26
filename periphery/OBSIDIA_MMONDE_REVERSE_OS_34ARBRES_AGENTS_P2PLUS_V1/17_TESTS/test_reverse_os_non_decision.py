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
class TestReverseOS(unittest.TestCase):
    def test_reverse_os(self):
        mod = load_module("reverse_mod", "06_REVERSE_OS_SSR_JARVIS/reverse_os.py")
        out = mod.project({"agent_name":"A","reason_code":"R","merkle_root":"M","verdict":"NO_KERNEL_DECISION","tree_vector":[0.0]*34})
        self.assertTrue(out["non_decision"])
        self.assertIn("qui", out)
        self.assertNotIn("decision", out)
if __name__ == "__main__":
    unittest.main()
