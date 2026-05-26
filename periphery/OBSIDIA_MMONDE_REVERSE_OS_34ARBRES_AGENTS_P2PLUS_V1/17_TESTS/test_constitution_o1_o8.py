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
class TestConstitution(unittest.TestCase):
    def test_genome(self):
        genome = json.loads((ROOT / "02_CONSTITUTION_LOIS_OBSIDIENNES/genome.json").read_text(encoding="utf-8"))
        self.assertEqual(len(genome), 8)
        self.assertIn("O1", genome)
        required = ["O1_NON_ACTION_LEGITIME.md","O2_IRREVERSIBILITE_STRUCTURELLE.md","O3_EPREUVE_TEMPORELLE_X108.md","O4_NON_ARBITRAGE_CONFLIT.md","O5_ELIMINATION_DECISIONNELLE.md","O6_MEMOIRE_NEGATIVE.md","O7_AUDITABILITE_NATIVE.md","O8_SEPARATION_COGNITION_ACTION.md"]
        for f in required:
            self.assertTrue((ROOT/"02_CONSTITUTION_LOIS_OBSIDIENNES"/f).exists())
if __name__ == "__main__":
    unittest.main()
