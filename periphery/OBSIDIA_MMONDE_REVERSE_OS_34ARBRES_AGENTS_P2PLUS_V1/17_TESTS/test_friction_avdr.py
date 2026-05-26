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
class TestFrictionAVDR(unittest.TestCase):
    def test_friction_avdr(self):
        fr = load_module("fr_mod", "12_FRICTION_AVDR_CONTINUUM/friction_symbolique.py")
        avdr = load_module("avdr_mod", "12_FRICTION_AVDR_CONTINUUM/avdr.py")
        chk = load_module("chk_mod", "12_FRICTION_AVDR_CONTINUUM/check_incoherence.py")
        self.assertAlmostEqual(fr.friction(0.9,0.1), 0.8)
        self.assertTrue(avdr.evaluate("agent","task")["non_decision"])
        self.assertTrue(chk.check(0.2, 0.15))
if __name__ == "__main__":
    unittest.main()
