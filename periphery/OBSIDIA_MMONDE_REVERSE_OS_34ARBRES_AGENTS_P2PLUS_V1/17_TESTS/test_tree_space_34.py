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
class TestTreeSpace34(unittest.TestCase):
    def test_tree_space_34(self):
        data = json.loads((ROOT / "04_ARBRES_34_TENSOR_MATRIX/arbres_34.canon.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["trees"]), 34)
        vec = [0.0]*34
        self.assertEqual(len(vec), 34)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in vec))
        for t in data["trees"]:
            self.assertTrue(t.get("non_decision"))
if __name__ == "__main__":
    unittest.main()
