import json, sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
_REGISTRY_PATH = (
    ROOT
    / "periphery"
    / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1"
    / "10_AGENTS_52"
    / "agents_52.registry.json"
)

def load_module(name, relpath, add_path=None):
    if add_path:
        sys.path.insert(0, str(ROOT / add_path))
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

import unittest
class TestAgentsRegistry(unittest.TestCase):
    def test_agents(self):
        agents = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(agents), 52)
        names = {a["nom"] for a in agents}
        for n in {"OBSIDIA_ATLAS_INGESTOR","CANON_GUARDIAN","GRAPH_BUILDER","TERMINAL_BUILDER","PROOF_SENTINEL"}:
            self.assertIn(n, names)
        for a in agents:
            self.assertTrue(a["input"])
            self.assertTrue(a["output"])
            self.assertTrue(a["boundary"])
            self.assertTrue(a["sortie_principale"])
            self.assertTrue(a["prompt_systeme"])
            self.assertTrue(a["non_decision"])
if __name__ == "__main__":
    unittest.main()
