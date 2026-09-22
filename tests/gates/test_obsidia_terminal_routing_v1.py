"""test_obsidia_terminal_routing_v1 — TERMINAL_ROUTING_FIXES_V1.

Scope : Phase A1 — policy word-boundary fix (A2), terminal_self route (A3),
capabilities/diagnostic corpus (A4), coder routing (A4), unknown fallback (A8).
Aucun subprocess. Aucune mutation. Aucun appel reseau.
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


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------
def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# ---------------------------------------------------------------------------
# A2 — policy_check word-boundary : faux positifs corriges
# ---------------------------------------------------------------------------
def test_policy_no_false_positive_actuelle() -> None:
    """'actuelle' ne doit pas declencher deny 'act'."""
    r = _a("quelle est la configuration actuelle")
    assert r["output"] != "POLICY_DENY", (
        f"Faux positif 'act' sur 'actuelle' — output={r['output']}")


def test_policy_no_false_positive_action() -> None:
    r = _a("quelle action prendre pour sigma")
    assert r["output"] != "POLICY_DENY", (
        f"Faux positif 'act' sur 'action' — output={r['output']}")


def test_policy_no_false_positive_impact() -> None:
    r = _a("quel est l impact de cette modification")
    assert r["output"] != "POLICY_DENY"


def test_policy_real_deny_commit() -> None:
    """'commit' doit toujours etre refuse."""
    r = _a("commit ces fichiers")
    assert r["output"] == "POLICY_DENY"


def test_policy_real_deny_push() -> None:
    r = _a("push vers main")
    assert r["output"] == "POLICY_DENY"


def test_policy_real_deny_deploy() -> None:
    r = _a("deploie la version 2")
    assert r["output"] == "POLICY_DENY"


# ---------------------------------------------------------------------------
# A3 — terminal_self route
# ---------------------------------------------------------------------------
def test_self_route_qui_es_tu() -> None:
    """'qui es tu' doit router vers terminal_self et retourner GUIDE."""
    r = _a("qui es tu")
    assert r["detected_layer"] == "terminal_self", f"layer={r['detected_layer']}"
    assert r["output"] == "GUIDE"


def test_self_route_que_peux_tu_faire() -> None:
    r = _a("que peux tu faire")
    assert r["detected_layer"] == "terminal_self"
    assert r["output"] == "GUIDE"


def test_self_route_quelles_sont_tes_capacites() -> None:
    r = _a("quelles sont tes capacites")
    assert r["detected_layer"] == "terminal_self"
    assert r["output"] == "GUIDE"


# ---------------------------------------------------------------------------
# A4 — corpus terminal_self : contenu de la reponse
# ---------------------------------------------------------------------------
def test_self_answer_contains_non_souverain() -> None:
    """La reponse doit mentionner que le terminal est non souverain."""
    r = _a("qui es tu")
    assert r["output"] == "GUIDE"
    low = r["reponse"].lower()
    assert "non souverain" in low or "kx108" in low or "readonly" in low, (
        f"Reponse terminal_self manque identite : {r['reponse'][:200]}")


def test_self_answer_contains_decision_authority() -> None:
    r = _a("que fais tu")
    low = r["reponse"].lower()
    assert "kx108" in low or "x108" in low or "autorite" in low


def test_capabilities_answer_lists_layers() -> None:
    """La reponse capabilities doit lister les couches connues."""
    r = _a("quelles sont tes capacites")
    low = r["reponse"].lower()
    assert "brody" in low or "sigma" in low or "obsidure" in low, (
        f"Reponse capabilities ne liste pas les couches : {r['reponse'][:200]}")


# ---------------------------------------------------------------------------
# A4 — obsidure / coder routing
# ---------------------------------------------------------------------------
def test_coder_routes_obsidure_or_guide() -> None:
    """'peux tu coder' doit router vers obsidure (COMMANDS ou GUIDE), jamais EXECUTE."""
    r = _a("peux tu coder un patch pour sigma")
    assert r["output"] in ("COMMANDS", "GUIDE"), (
        f"Unexpected output for 'peux tu coder' : {r['output']}")
    assert r["output"] != "POLICY_DENY"


# ---------------------------------------------------------------------------
# A8 — build_unknown_answer : contenu ameliore
# ---------------------------------------------------------------------------
def test_unknown_answer_lists_layers() -> None:
    """Un STOP_UNKNOWN doit lister les couches disponibles."""
    r = _a("plop incomprehensible zzz")
    if r["output"] == "STOP_UNKNOWN":
        low = r["reponse"].lower()
        assert "brody" in low or "sigma" in low or "couche" in low, (
            f"STOP_UNKNOWN ne liste pas les couches : {r['reponse'][:300]}")


def test_unknown_answer_contains_examples() -> None:
    """Un STOP_UNKNOWN doit proposer des exemples de formulations."""
    r = _a("aaabbbccc xyz inconnu")
    if r["output"] == "STOP_UNKNOWN":
        low = r["reponse"].lower()
        assert ("exemple" in low or "->" in low or "→" in low or
                "formulation" in low or "precise" in low), (
            f"STOP_UNKNOWN sans exemples : {r['reponse'][:300]}")


# ---------------------------------------------------------------------------
# Gardes statiques : non-souverain inchange
# ---------------------------------------------------------------------------
def test_static_no_subprocess() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_static_decision_authority_unchanged() -> None:
    """KX108_ONLY doit rester la seule autorite dans le code."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "KX108_ONLY" in src
    assert "decision_authority" in src


def test_static_terminal_self_in_plan_organes() -> None:
    """terminal_self doit etre dans PLAN_ORGANES."""
    assert "terminal_self" in cli.PLAN_ORGANES


def test_static_terminal_self_in_plan_tooling() -> None:
    """terminal_self doit etre dans PLAN_TOOLING."""
    assert "terminal_self" in cli.PLAN_TOOLING
