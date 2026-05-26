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
class TestMCP(unittest.TestCase):
    def test_mcp(self):
        mod = load_module("mcp_mod", "09_MCP_BRIDGE_OBSIDIA_IR/mcp_bridge.py")
        out = mod.convert_request({"intent":"demo","domain":"test","scope":"read","cost":1,"risk":0.2})
        self.assertTrue(out["non_decision"])
        self.assertEqual(out["intent"], "demo")
if __name__ == "__main__":
    unittest.main()
