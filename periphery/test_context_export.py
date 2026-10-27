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
class TestContextExport(unittest.TestCase):
    def test_context_export(self):
        retrieve = load_module("retrieve_mod", "14_CONTEXT_EXPORT_X108_BOUNDARY/retrieve_context.py")
        export = load_module("export_mod", "14_CONTEXT_EXPORT_X108_BOUNDARY/export_for_x108.py")
        packet = retrieve.retrieve("demo")
        out = export.export(packet)
        self.assertTrue(out["non_decision"])
        self.assertEqual(out["export_target"], "X-108")
        self.assertNotIn("decision", out)
if __name__ == "__main__":
    unittest.main()
