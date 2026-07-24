"""test_obsidia_tui_unification_v2 — OBSIDIA_TERMINAL_TUI_UNIFICATION_V2.

Scope : vérifier la surface unifiée du cockpit terminal.
  - readonly contract (tui_authority=NONE, KX108_ONLY)
  - tabs principales présentes
  - aliases TUI présents
  - format contient les markers requis
  - smokes CLI : tui status / tui help / cockpit status / "terminal cockpit status"
  - aucun process-spawn
  - aucune autorité TUI
  - aucune décision souveraine émise
  - anciens panneaux non cassés (gates tab, skill resolver, law registry)

Le TUI affiche. Il ne décide pas. READONLY strict.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_CLI = _CLI_DIR / "obsidia_cli.py"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli

_REG = cli.load_registry(cli.REGISTRY_PATH)


# =============================================================================
# TEST 01 — get_terminal_tui_command_surface_v2 readonly contract
# =============================================================================

def test_01_tui_unification_readonly_contract() -> None:
    result = cli.get_terminal_tui_command_surface_v2()
    assert result.get("version") == "OBSIDIA_TERMINAL_TUI_UNIFICATION_V2", (
        f"version inattendue : {result.get('version')}"
    )
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("tui_authority") == "NONE", (
        f"tui_authority attendu NONE, obtenu {result.get('tui_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("mutation") == "none"
    assert result.get("subprocess") == "none"


# =============================================================================
# TEST 02 — tabs principales presentes
# =============================================================================

def test_02_tui_unification_contains_required_tabs() -> None:
    result = cli.get_terminal_tui_command_surface_v2()
    tabs = result.get("tabs", {})
    for name in ("CORE", "GATES", "TOOLS", "STATUS", "PROOF", "LAWS",
                 "SKILLS", "DOMAINS", "BRODY", "OBSIDURE", "SIGMA_OIE"):
        assert name in tabs, f"Tab manquante : {name}"
        tab = tabs[name]
        for field in ("label", "status", "command", "readonly", "authority", "panel"):
            assert field in tab, f"Champ '{field}' manquant dans tab {name}"
        assert tab.get("readonly") is True, f"Tab {name} doit etre readonly"
        assert tab.get("authority") == "NONE", f"Tab {name} doit avoir authority=NONE"
        assert tab.get("status") == "AVAILABLE"


# =============================================================================
# TEST 03 — aliases TUI presents
# =============================================================================

def test_03_tui_unification_contains_required_aliases() -> None:
    result = cli.get_terminal_tui_command_surface_v2()
    aliases = result.get("aliases", {})
    for alias in ("/gates", "/tools", "/status", "/proof", "/laws", "/skills",
                  "/domains", "/brody", "/obsidure", "/sigma", "/oie"):
        assert alias in aliases, f"Alias manquant : {alias}"
        assert aliases[alias] in result.get("tabs", {}), (
            f"Alias {alias} pointe vers tab inconnue : {aliases[alias]}"
        )


# =============================================================================
# TEST 04 — format contient les markers requis
# =============================================================================

def test_04_tui_unification_format_contains_required_markers() -> None:
    resp = cli.build_terminal_tui_unification_response_v2("tui status", _REG)
    text = cli.format_terminal_tui_unification_v2(resp)
    for marker in (
        "OBSIDIA_TERMINAL_TUI_UNIFICATION_V2",
        "READONLY",
        "KX108_ONLY",
        "tui_authority=NONE",
        "auto_execution=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )


# =============================================================================
# TEST 05 — smoke CLI : tui status
# =============================================================================

def test_05_cli_tui_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "tui", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "TUI_UNIFICATION" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "tui_authority=NONE" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 06 — smoke CLI : tui help
# =============================================================================

def test_06_cli_tui_help_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "tui", "help"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    for alias in ("/gates", "/proof", "/laws", "/skills"):
        assert alias in out, f"Alias '{alias}' manquant.\nSortie: {out[:400]}"


# =============================================================================
# TEST 07 — smoke CLI : cockpit status
# =============================================================================

def test_07_cli_cockpit_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "cockpit", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert ("COCKPIT" in out or "TUI" in out), f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 08 — smoke runtime : "terminal cockpit status"
# =============================================================================

def test_08_runtime_terminal_cockpit_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "terminal cockpit status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "TUI" in out, f"Sortie: {out[:400]}"
    assert "COMMANDS_ONLY" in out, f"Sortie: {out[:400]}"
    assert "auto_execution=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 09 — aucun process-spawn dans le CLI source
# =============================================================================

def test_09_no_subprocess_or_process_spawn() -> None:
    src = _CLI.read_text(encoding="utf-8")
    assert "import " + "subprocess" not in src, (
        "import de module process interdit dans le CLI"
    )
    assert re.search(r'os\.system\s*\(', src) is None, (
        "execution de commande OS interdite dans le CLI"
    )
    assert re.search(r'shell\s*=\s*True', src) is None, (
        "execution shell interdite dans le CLI"
    )
    assert re.search(r'Start-Process\b', src) is None, (
        "process-spawn interdit dans le CLI"
    )


# =============================================================================
# TEST 10 — aucune autorite donnee au TUI
# =============================================================================

def test_10_no_tui_authority() -> None:
    resp = cli.build_terminal_tui_unification_response_v2("tui status", _REG)
    text = cli.format_terminal_tui_unification_v2(resp)
    assert "tui_authority=NONE" in text, (
        f"tui_authority=NONE doit etre visible.\nTexte: {text[:400]}"
    )
    etat = resp.get("etat_technique", {})
    assert etat.get("tui_authority") == "NONE"
    outils = resp.get("outils_panel", {})
    assert outils.get("tui_authority") == "NONE"
    surface = resp.get("tui_surface", {})
    assert surface.get("tui_authority") == "NONE"


# =============================================================================
# TEST 11 — aucune emission souveraine dans la sortie
# =============================================================================

def test_11_no_terminal_sovereign_action() -> None:
    resp = cli.build_terminal_tui_unification_response_v2("tui status", _REG)
    text = cli.format_terminal_tui_unification_v2(resp)
    help_text = cli.format_terminal_tui_help_v2(cli.get_terminal_tui_command_surface_v2())
    combined = text + resp.get("reponse", "") + help_text
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse TUI.\n"
            f"Texte: {combined[:300]}"
        )
    assert "no sovereign decision" in text, (
        "Le format doit rappeler 'no sovereign decision' dans FORBIDDEN"
    )
    assert "no automatic action" in text, (
        "Le format doit rappeler 'no automatic action' dans FORBIDDEN"
    )


# =============================================================================
# TEST 12 — /gates reste disponible (tab existante non cassee)
# =============================================================================

def test_12_existing_gates_tab_still_available() -> None:
    assert "/gates" in cli._TAB_COMMANDS, "/gates doit rester dans _TAB_COMMANDS"
    assert cli._TAB_COMMANDS["/gates"] == "GATES"
    surface = cli.get_terminal_tui_command_surface_v2()
    assert surface["aliases"].get("/gates") == "GATES"


# =============================================================================
# TEST 13 — skill resolver status reste disponible
# =============================================================================

def test_13_existing_skill_resolver_status_still_available() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "skill", "resolver", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "OBSIDIA_TERMINAL_SKILL_RESOLVER_V2_CLEANUP" in out, (
        f"skill resolver status doit garder son panneau.\nSortie: {out[:400]}"
    )


# =============================================================================
# TEST 14 — law status reste disponible
# =============================================================================

def test_14_existing_law_status_still_available() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "law", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "OBSIDIA_TERMINAL_LAW_REGISTRY_V1" in out, (
        f"law status doit garder son panneau.\nSortie: {out[:400]}"
    )
