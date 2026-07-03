"""test_obsidia_aliases_naturels_v2 — ALIASES_NATURELS_V2 (routage/affichage).

Scope : OBSIDIA_TERMINAL_ALIASES_NATURELS_V2_APPLY.
Verifie que les alias ameliorent la CLASSIFICATION sans jamais declencher
d'action, que la lecture locale V2A garde une couche documentaire (pas de
routage brody parasite via "contexte"), et que policy deny / secrets restent
prioritaires. Aucun reseau, aucun subprocess, aucune ecriture.
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


def _answer(raw: str) -> dict:
    return cli.answer_router(raw, _REG)


def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


def test_local_read_priority_beats_brody_context(tmp_path) -> None:
    # "contexte" est un trigger registry de brody ; la lecture locale doit
    # neanmoins afficher une couche file_read, pas brody.
    root = tmp_path
    (root / "docs" / "specs").mkdir(parents=True)
    (root / "docs" / "specs" / "D.md").write_text(
        "\n".join(f"ligne {i} KX108_ONLY" if i % 4 == 0 else f"ligne {i}"
                  for i in range(1, 60)), encoding="utf-8")
    cli.REPO_ROOT = root
    r = _answer("contexte KX108_ONLY dans docs/specs/D.md")
    assert r["output"] == "EXECUTE"
    assert r["detected_layer"].startswith("file_read:")
    assert r["detected_layer"] != "brody"


def test_search_local_keeps_file_layer(tmp_path) -> None:
    root = tmp_path
    (root / "docs").mkdir()
    (root / "docs" / "s.md").write_text("kx108_only ici\nautre\n", encoding="utf-8")
    cli.REPO_ROOT = root
    r = _answer("cherche kx108_only dans docs/s.md")
    assert r["output"] == "EXECUTE"
    assert r["detected_layer"].startswith("file_read:")


def test_thermo_alias() -> None:
    r = _answer("c'est quoi thermo")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert "energy_thermo" in r["detected_layer"]


def test_kernel_judge_alias() -> None:
    # "qui decide" -> couche unknown -> corpus:kernel_x108 servi (ANSWER_LOCAL).
    r = _answer("qui decide")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert "kernel_x108" in r["detected_layer"]
    # "autorite de decision" -> trigger registry "decision" -> couche kernel, GUIDE.
    r2 = _answer("autorite de decision")
    assert r2["output"] in ("GUIDE", "EXECUTE")
    assert r2["detected_layer"] == "kernel"


def test_memory_graphiti_alias() -> None:
    # Alias = trigger registry memory -> route couche memory, sortie GUIDE.
    r = _answer("memoire graphiti")
    assert r["output"] == "GUIDE"
    assert r["detected_layer"] == "memory"


def test_oie_inference_economy_alias() -> None:
    r = _answer("economie d'inference")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert "oie" in r["detected_layer"]


def test_lean_proofs_alias() -> None:
    # "lean" est trigger registry -> couche obsidienne, sortie GUIDE.
    r = _answer("preuves lean")
    assert r["output"] == "GUIDE"
    assert r["detected_layer"] in ("obsidienne", "corpus:lean_proofs")


def test_mutation_words_still_policy_deny() -> None:
    for q in ("commit le kernel", "apply le patch", "push la branche"):
        r = _answer(q)
        assert r["output"] == "POLICY_DENY"


def test_secrets_still_policy_deny(tmp_path) -> None:
    cli.REPO_ROOT = tmp_path
    for q in ("ouvre .env", "lis id_rsa"):
        r = _answer(q)
        assert r["output"] == "POLICY_DENY"


def test_no_subprocess_static_guard() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src
