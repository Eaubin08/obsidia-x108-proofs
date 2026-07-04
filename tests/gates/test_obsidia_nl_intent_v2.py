"""test_obsidia_nl_intent_v2 — ANSWER_ROUTER_NL_INTENT_V2.

Scope : OBSIDIA_ANSWER_ROUTER_NL_INTENT_V2_APPLY.
Verifie le mapping des paraphrases humaines vers les intents deja surs :
regarde/montre -> lecture V2A ; ou/trouve -> recherche V2A ;
resume/explique/compare -> GUIDE V2B_REQUIRED (non applique) ;
suite/quoi faire -> ANSWER_PLAN. Aucun droit, aucun subprocess, aucune
lecture complete. Fichiers de test en tmp_path (REPO_ROOT monkeypatche).
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)


def _mkfile(tmp_path):
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    f = tmp_path / "docs" / "specs" / "X.md"
    f.write_text("\n".join(f"ligne {i} KX108 Sigma" if i % 5 == 0 else f"ligne {i}"
                           for i in range(1, 200)), encoding="utf-8")
    (tmp_path / "docs" / "specs" / "Y.md").write_text("autre\n", encoding="utf-8")
    cli.REPO_ROOT = tmp_path


def _a(q):
    return cli.answer_router(q, _REG)


def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


def test_regarde_maps_to_local_read_window(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("regarde docs/specs/X.md")
    assert r["output"] == "EXECUTE"
    assert r["detected_layer"].startswith("file_read:")
    assert r["action_locale"] in ("READ_LOCAL_WINDOW", "READ_LOCAL_RANGE")


def test_montre_lignes_maps_to_local_range(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("montre les lignes 20 a 30 de docs/specs/X.md")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "READ_LOCAL_RANGE"
    assert "20:" in r["reponse"] and "30:" in r["reponse"]


def test_ou_parle_de_maps_to_local_search(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("ou est-ce que ca parle de KX108 dans docs/specs/X.md")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "SEARCH_LOCAL_TEXT"
    assert "kx108" in r["reponse"].lower()


def test_trouve_maps_to_local_search(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("trouve Sigma dans docs/specs/X.md")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "SEARCH_LOCAL_TEXT"


def test_resume_file_is_guide_v2b_required(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("resume docs/specs/X.md")
    assert r["output"] == "GUIDE"
    assert "V2B_REQUIRED" in r["reponse"]


def test_explique_file_is_guide_v2b_required(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("explique docs/specs/X.md")
    assert r["output"] == "GUIDE"
    assert "V2B_REQUIRED" in r["reponse"]


def test_compare_files_is_guide_v2b_required(tmp_path) -> None:
    _mkfile(tmp_path)
    r = _a("compare docs/specs/X.md et docs/specs/Y.md")
    assert r["output"] == "GUIDE"
    assert "V2B_REQUIRED" in r["reponse"]


def test_next_step_maps_to_answer_plan() -> None:
    for q in ("qu'est-ce que je dois faire maintenant", "c'est quoi la suite",
              "prochaine etape", "prepare la suite sans modifier"):
        r = _a(q)
        assert r["output"] == "GUIDE"
        assert r["mode_reponse"] == "ANSWER_PLAN"


def test_corpus_thermo_regression() -> None:
    r = _a("c'est quoi thermo")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert "energy_thermo" in r["detected_layer"]


def test_commit_policy_deny_regression() -> None:
    r = _a("commit le kernel")
    assert r["output"] == "POLICY_DENY"


def test_secret_policy_deny_regression(tmp_path) -> None:
    cli.REPO_ROOT = tmp_path
    for q in ("ouvre .env", "lis id_rsa"):
        r = _a(q)
        assert r["output"] == "POLICY_DENY"


def test_no_subprocess_static_guard() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src
