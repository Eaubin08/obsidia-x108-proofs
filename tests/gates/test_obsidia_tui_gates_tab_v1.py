"""test_obsidia_tui_gates_tab_v1 — OBSIDIA_TERMINAL_TUI_GATES_TAB_V1.

Scope : verifier que /gates est branche dans _TAB_COMMANDS et que
extract_gates_panel retourne un contenu advisory valide.

Aucun serveur. Aucun subprocess. Analyse statique + fonctions pures.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli

_REG = cli.load_registry(cli.REGISTRY_PATH)


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# =============================================================================
# TEST 01 — /gates est present dans _TAB_COMMANDS
# =============================================================================

def test_01_gates_in_tab_commands() -> None:
    assert hasattr(cli, "_TAB_COMMANDS"), "_TAB_COMMANDS doit exister"
    assert "/gates" in cli._TAB_COMMANDS, "/gates doit etre dans _TAB_COMMANDS"
    assert cli._TAB_COMMANDS["/gates"] == "GATES", "valeur attendue : 'GATES'"


# =============================================================================
# TEST 02 — GATES est dans tous les onglets connus
# =============================================================================

def test_02_gates_in_all_known_tabs() -> None:
    for tab in ("PLAN", "STATUS", "TOOLS", "PROOF", "GATES"):
        assert tab in cli._TAB_COMMANDS.values(), (
            f"Tab '{tab}' doit etre dans les valeurs de _TAB_COMMANDS"
        )


# =============================================================================
# TEST 03 — extract_gates_panel existe et est callable
# =============================================================================

def test_03_extract_gates_panel_exists() -> None:
    assert hasattr(cli, "extract_gates_panel"), "extract_gates_panel doit exister"
    assert callable(cli.extract_gates_panel), "extract_gates_panel doit etre callable"


# =============================================================================
# TEST 04 — extract_plan_panel delègue à extract_gates_panel pour GATES
# =============================================================================

def test_04_extract_plan_panel_delegates_gates() -> None:
    r = _a("obsidure prépare un patch lean")
    lines_via_plan = cli.extract_plan_panel(r, active_tab="GATES")
    lines_direct = cli.extract_gates_panel(r)
    assert lines_via_plan == lines_direct, (
        "extract_plan_panel(active_tab='GATES') doit retourner "
        "le meme resultat que extract_gates_panel()"
    )


# =============================================================================
# TEST 05 — extract_gates_panel contient GATE_PLAN ou OBSIDIA_TERMINAL_GATE_PLANNER_V1
# =============================================================================

def test_05_gates_panel_contains_gate_plan_marker() -> None:
    r = _a("obsidure prépare un patch lean")
    lines = cli.extract_gates_panel(r)
    combined = "\n".join(lines)
    assert "GATE_PLAN" in combined or "OBSIDIA_TERMINAL_GATE_PLANNER_V1" in combined, (
        f"extract_gates_panel doit contenir GATE_PLAN ou OBSIDIA_TERMINAL_GATE_PLANNER_V1.\n"
        f"Contenu : {combined[:300]}"
    )


# =============================================================================
# TEST 06 — extract_gates_panel contient NONE_GATE_PLANNER_IS_ADVISORY_ONLY
# =============================================================================

def test_06_gates_panel_advisory_only_marker() -> None:
    r = _a("obsidure prépare un patch lean")
    lines = cli.extract_gates_panel(r)
    combined = "\n".join(lines)
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in combined, (
        f"extract_gates_panel doit contenir NONE_GATE_PLANNER_IS_ADVISORY_ONLY.\n"
        f"Contenu : {combined[:300]}"
    )


# =============================================================================
# TEST 07 — extract_gates_panel contient auto_execution=False
# =============================================================================

def test_07_gates_panel_auto_execution_false() -> None:
    r = _a("obsidure prépare un patch lean")
    lines = cli.extract_gates_panel(r)
    combined = "\n".join(lines)
    assert "auto_execution=False" in combined, (
        f"extract_gates_panel doit contenir auto_execution=False.\n"
        f"Contenu : {combined[:300]}"
    )


# =============================================================================
# TEST 08 — extract_gates_panel retourne une liste non vide
# =============================================================================

def test_08_gates_panel_returns_list() -> None:
    r = _a("obsidure prépare un patch lean")
    lines = cli.extract_gates_panel(r)
    assert isinstance(lines, list), "extract_gates_panel doit retourner une list"
    assert len(lines) > 0, "extract_gates_panel ne doit pas retourner une liste vide"


# =============================================================================
# TEST 09 — extract_gates_panel ne contient aucun ALLOW/BLOCK/HOLD/ACT émis
# =============================================================================

def test_09_gates_panel_no_act_emission() -> None:
    r = _a("obsidure prépare un patch lean")
    lines = cli.extract_gates_panel(r)
    combined = "\n".join(lines)
    for forbidden in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD", "X108Gate.ACT",
                      "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD", "EMIT_ACT"):
        assert forbidden not in combined, (
            f"extract_gates_panel ne doit pas emettre '{forbidden}' (hors KX108).\n"
            f"Contenu : {combined[:200]}"
        )


# =============================================================================
# TEST 10 — extract_gates_panel fonctionne sans gate_plan dans la reponse
# =============================================================================

def test_10_gates_panel_fallback_when_no_gate_plan() -> None:
    r_empty: dict = {}
    lines = cli.extract_gates_panel(r_empty)
    combined = "\n".join(lines)
    assert "GATE_PLAN" in combined or "OBSIDIA_TERMINAL_GATE_PLANNER_V1" in combined, (
        "extract_gates_panel doit retourner un fallback valide meme sans gate_plan"
    )
    assert "NONE_GATE_PLANNER_IS_ADVISORY_ONLY" in combined, (
        "Le fallback de extract_gates_panel doit contenir NONE_GATE_PLANNER_IS_ADVISORY_ONLY"
    )


# =============================================================================
# TEST 11 — extract_gates_panel fonctionne pour une requete ANSWER_STATUS
# =============================================================================

def test_11_gates_panel_works_for_status_query() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_gates_panel(r)
    combined = "\n".join(lines)
    assert "GATE_PLAN" in combined or "OBSIDIA_TERMINAL_GATE_PLANNER_V1" in combined


# =============================================================================
# TEST 12 — aucun subprocess dans le CLI source
# =============================================================================

def test_12_no_subprocess_call_in_cli() -> None:
    import re
    src = (Path(_CLI_DIR) / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src, "import subprocess interdit dans le CLI"
    assert re.search(r'os\.system\s*\(', src) is None, "os.system() interdit dans le CLI"
    assert re.search(r'shell\s*=\s*True', src) is None, "shell=True interdit dans le CLI"


# =============================================================================
# TEST 13 — /gates present dans la source du TUI interactif
# =============================================================================

def test_13_gates_tab_in_tui_source() -> None:
    src = (Path(_CLI_DIR) / "obsidia_cli.py").read_text(encoding="utf-8")
    tui_start = src.find("def interactive_tui_shell")
    assert tui_start >= 0, "interactive_tui_shell doit exister"
    tui_end = src.find("\ndef interactive_shell", tui_start)
    tui_end = tui_end if tui_end > tui_start else tui_start + 12000
    tui_body = src[tui_start:tui_end]
    # /gates doit apparaitre dans le corps du TUI (welcome plan + hints aide + suite)
    assert "/gates" in tui_body, "/gates doit etre mentionne dans interactive_tui_shell"
    # _TAB_COMMANDS est defini au niveau module — on verifie la valeur via le module importe
    assert "GATES" in cli._TAB_COMMANDS.values(), (
        "GATES doit etre dans les valeurs de _TAB_COMMANDS"
    )
