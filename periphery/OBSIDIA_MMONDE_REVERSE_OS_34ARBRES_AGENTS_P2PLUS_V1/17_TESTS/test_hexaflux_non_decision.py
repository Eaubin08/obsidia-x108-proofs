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
class TestHexaFlux(unittest.TestCase):
    def test_hexaflux(self):
        mod = load_module("hex_mod", "08_HEXAFLUX_LTCU_MUTATIONS/hexaflux.py")
        self.assertEqual(mod.mutate(42), 42)
        self.assertTrue(mod.symbolic_mutation("x")["non_decision"])
if __name__ == "__main__":
    unittest.main()
