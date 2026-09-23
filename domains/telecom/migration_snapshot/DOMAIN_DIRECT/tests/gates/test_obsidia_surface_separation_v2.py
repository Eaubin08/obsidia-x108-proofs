"""test_obsidia_surface_separation_v2 — OBSIDIA_TERMINAL_SURFACE_SEPARATION_V2_APPLY.

Scope : verifier que le TUI V2 separe correctement les surfaces :
  LEFT  = reponse humaine (sans metadonnees systeme)
  RIGHT = etat technique, outils, plan, preuves
  COMPOSER = invite de saisie

Aucun serveur, aucun subprocess, analyse statique + fonctions pures.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_CLI = _CLI_DIR / "obsidia_cli.py"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli

_REG = cli.load_registry(cli.REGISTRY_PATH)


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


def _src() -> str:
    return _CLI.read_text(encoding="utf-8")


# =============================================================================
# TEST 01 — build_surface_model existe
# =============================================================================

def test_01_build_surface_model_exists() -> None:
    assert hasattr(cli, "build_surface_model")
    assert callable(cli.build_surface_model)


# =============================================================================
# TEST 02 — extract_plan_panel accepte active_tab
# =============================================================================

def test_02_extract_plan_panel_accepts_active_tab() -> None:
    r = _a("obsidure est actif ?")
    import inspect
    sig = inspect.signature(cli.extract_plan_panel)
    params = list(sig.parameters.keys())
    assert "active_tab" in params, "extract_plan_panel doit avoir un parametre active_tab"


# =============================================================================
# TEST 03 — extract_status_panel existe (ou extract_plan_panel STATUS fonctionne)
# =============================================================================

def test_03_extract_status_panel_exists_or_tab_works() -> None:
    r = _a("obsidure est actif ?")
    if hasattr(cli, "extract_status_panel"):
        lines = cli.extract_status_panel(r)
    else:
        lines = cli.extract_plan_panel(r, active_tab="STATUS")
    assert isinstance(lines, list)
    assert len(lines) > 0


# =============================================================================
# TEST 04 — extract_tools_panel existe (ou extract_plan_panel TOOLS fonctionne)
# =============================================================================

def test_04_extract_tools_panel_exists_or_tab_works() -> None:
    r = _a("obsidure est actif ?")
    if hasattr(cli, "extract_tools_panel"):
        lines = cli.extract_tools_panel(r)
    else:
        lines = cli.extract_plan_panel(r, active_tab="TOOLS")
    assert isinstance(lines, list)
    assert len(lines) > 0


# =============================================================================
# TEST 05 — extract_proof_panel existe (ou extract_plan_panel PROOF fonctionne)
# =============================================================================

def test_05_extract_proof_panel_exists_or_tab_works() -> None:
    r = _a("obsidure est actif ?")
    if hasattr(cli, "extract_proof_panel"):
        lines = cli.extract_proof_panel(r)
    else:
        lines = cli.extract_plan_panel(r, active_tab="PROOF")
    assert isinstance(lines, list)
    assert len(lines) > 0


# =============================================================================
# TEST 06 — obsidure est actif ? retourne ANSWER_STATUS
# =============================================================================

def test_06_obsidure_est_actif_returns_answer_status() -> None:
    r = _a("obsidure est actif ?")
    assert r["mode_reponse"] == "ANSWER_STATUS", (
        f"mode_reponse attendu ANSWER_STATUS, obtenu {r['mode_reponse']}"
    )


# =============================================================================
# TEST 07 — main panel de obsidure est actif ? contient une reponse humaine
# =============================================================================

def test_07_obsidure_actif_main_panel_has_human_answer() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    # Doit contenir "Obsidure" (texte humain)
    assert "Obsidure" in combined or "obsidure" in combined.lower(), (
        f"Le panneau principal ne contient pas de reponse humaine sur Obsidure.\n"
        f"Contenu : {combined[:300]}"
    )


# =============================================================================
# TEST 08 — main panel ne contient pas _PATCH_PROPOSALS
# =============================================================================

def test_08_obsidure_actif_main_panel_no_patch_proposals() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    assert "_PATCH_PROPOSALS" not in combined, (
        f"_PATCH_PROPOSALS trouve dans le panneau principal (doit aller a droite).\n"
        f"Lignes problematiques : {[l for l in lines if '_PATCH_PROPOSALS' in l]}"
    )


# =============================================================================
# TEST 09 — main panel ne contient pas scripts/gates
# =============================================================================

def test_09_obsidure_actif_main_panel_no_scripts_gates() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    assert "scripts/gates" not in combined, (
        f"scripts/gates trouve dans le panneau principal (doit aller a droite).\n"
        f"Lignes problematiques : {[l for l in lines if 'scripts/gates' in l]}"
    )


# =============================================================================
# TEST 10 — main panel ne contient pas obsidure_cli.py
# =============================================================================

def test_10_obsidure_actif_main_panel_no_obsidure_cli() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    assert "obsidure_cli.py" not in combined, (
        f"obsidure_cli.py trouve dans le panneau principal (donnee technique).\n"
        f"Lignes : {[l for l in lines if 'obsidure_cli.py' in l]}"
    )


# =============================================================================
# TEST 11 — main panel ne contient pas INTERDIT
# =============================================================================

def test_11_obsidure_actif_main_panel_no_interdit() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    assert "INTERDIT" not in combined, (
        f"INTERDIT trouve dans le panneau principal (doit aller a droite).\n"
        f"Lignes : {[l for l in lines if 'INTERDIT' in l]}"
    )


# =============================================================================
# TEST 12 — main panel ne contient pas ETAT
# =============================================================================

def test_12_obsidure_actif_main_panel_no_etat() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_main_answer_panel(r)
    combined = "\n".join(lines)
    assert "ETAT" not in combined, (
        f"ETAT trouve dans le panneau principal (doit aller a droite).\n"
        f"Lignes : {[l for l in lines if 'ETAT' in l]}"
    )


# =============================================================================
# TEST 13 — status panel de obsidure contient terminal/runtime/workflow/autonomy
# =============================================================================

def test_13_obsidure_actif_status_panel_has_technical_fields() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_plan_panel(r, active_tab="STATUS")
    combined = "\n".join(lines).lower()
    assert "terminal" in combined, "STATUS panel doit contenir 'terminal'"
    assert "runtime" in combined, "STATUS panel doit contenir 'runtime'"
    assert "workflow" in combined, "STATUS panel doit contenir 'workflow'"
    assert "autonomy" in combined, "STATUS panel doit contenir 'autonomy'"


# =============================================================================
# TEST 14 — tools panel de obsidure contient proposals/gates/apply/commit/push
# =============================================================================

def test_14_obsidure_actif_tools_panel_has_tools() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_plan_panel(r, active_tab="TOOLS")
    combined = "\n".join(lines).lower()
    assert "proposals" in combined, "TOOLS panel doit contenir 'proposals'"
    assert "gates" in combined, "TOOLS panel doit contenir 'gates'"
    assert "apply" in combined, "TOOLS panel doit contenir 'apply'"
    assert "commit" in combined, "TOOLS panel doit contenir 'commit'"
    assert "push" in combined, "TOOLS panel doit contenir 'push'"


# =============================================================================
# TEST 15 — plan panel de obsidure contient layer/mode/status/next
# =============================================================================

def test_15_obsidure_actif_plan_panel_has_plan_fields() -> None:
    r = _a("obsidure est actif ?")
    lines = cli.extract_plan_panel(r, active_tab="PLAN")
    combined = "\n".join(lines).lower()
    assert "layer" in combined, "PLAN panel doit contenir 'layer'"
    assert "mode" in combined, "PLAN panel doit contenir 'mode'"
    assert "status" in combined, "PLAN panel doit contenir 'status'"
    assert "next" in combined, "PLAN panel doit contenir 'next'"


# =============================================================================
# TEST 16 — brody est actif ? main panel compact (pas de details techniques longs)
# =============================================================================

def test_16_brody_actif_main_panel_no_long_technical_lines() -> None:
    r = _a("brody est actif ?")
    lines = cli.extract_main_answer_panel(r)
    # La reponse principale doit etre compacte (pas de dump technique)
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) <= 12, (
        f"Le panneau principal de 'brody est actif' est trop long ({len(non_empty)} lignes).\n"
        f"Contenu : {non_empty}"
    )
    combined = "\n".join(lines)
    # Aucun token systeme ne doit apparaitre
    for tok in ("_PATCH_PROPOSALS", "scripts/gates", "INTERDIT", "ETAT", "[OBSIDIA RESPONSE]"):
        assert tok not in combined, f"Token systeme '{tok}' dans le panneau principal"


# =============================================================================
# TEST 17 — brody est actif ? status panel contient api_8000 ou API 8000
# =============================================================================

def test_17_brody_actif_status_panel_has_api_8000() -> None:
    r = _a("brody est actif ?")
    lines = cli.extract_plan_panel(r, active_tab="STATUS")
    combined = "\n".join(lines).lower()
    assert "api" in combined and ("8000" in combined or "api_8000" in combined.replace("_", "")), (
        f"STATUS panel de brody doit contenir api_8000 ou API 8000.\nContenu : {combined}"
    )


# =============================================================================
# TEST 18 — stack active : status panel contient API/KERNEL/GRAPHITI/UI/NEO4J
# =============================================================================

def test_18_stack_active_status_panel_has_services() -> None:
    r = _a("stack active")
    lines = cli.extract_plan_panel(r, active_tab="STATUS")
    combined = "\n".join(lines).upper()
    for svc in ("API", "KERNEL", "GRAPHITI", "UI", "NEO4J"):
        assert svc in combined, (
            f"STATUS panel de 'stack active' doit contenir '{svc}'.\nContenu : {combined[:400]}"
        )


# =============================================================================
# TEST 19 — /plan /status /tools /proof existent dans interactive_tui_shell
# =============================================================================

def test_19_tab_commands_in_tui_shell_source() -> None:
    src = _src()
    tui_start = src.find("def interactive_tui_shell")
    tui_end = src.find("\ndef interactive_shell", tui_start)
    if tui_end == -1:
        tui_end = tui_start + 8000
    tui_body = src[tui_start:tui_end]
    for cmd in ("/plan", "/status", "/tools", "/proof"):
        assert cmd in tui_body, (
            f"La commande '{cmd}' doit etre presente dans interactive_tui_shell"
        )


# =============================================================================
# TEST 20 — suite est traite dans interactive_tui_shell
# =============================================================================

def test_20_suite_handled_in_tui_shell_source() -> None:
    src = _src()
    tui_start = src.find("def interactive_tui_shell")
    tui_end = src.find("\ndef interactive_shell", tui_start)
    if tui_end == -1:
        tui_end = tui_start + 8000
    tui_body = src[tui_start:tui_end]
    # _SUITE_WORDS ou "suite" doit etre mentionne dans la boucle
    assert "_SUITE_WORDS" in tui_body or '"suite"' in tui_body, (
        "interactive_tui_shell doit traiter la commande 'suite'"
    )


# =============================================================================
# TEST 21 — capabilities brody continue de fonctionner
# =============================================================================

def test_21_capabilities_brody_still_works() -> None:
    r = _a("capabilities brody")
    assert r["output"] in ("GUIDE", "EXECUTE", "COMMANDS")
    assert r["mode_reponse"] != "ANSWER_STATUS"


# =============================================================================
# TEST 22 — peux tu coder continue de fonctionner
# =============================================================================

def test_22_peux_tu_coder_still_works() -> None:
    r = _a("peux tu coder")
    assert r["mode_reponse"] == "ANSWER_LOCAL"
    assert r["output"] in ("GUIDE", "EXECUTE")


# =============================================================================
# TEST 23 — runtime continue de fonctionner
# =============================================================================

def test_23_runtime_still_works() -> None:
    r = _a("runtime")
    assert r["mode_reponse"] in ("ANSWER_LOCAL", "ANSWER_LIVE_READONLY", "ANSWER_STATUS")
    assert r["output"] in ("GUIDE", "EXECUTE", "COMMANDS")


# =============================================================================
# TEST 24 — aucun subprocess
# =============================================================================

def test_24_no_subprocess() -> None:
    src = _src()
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


# =============================================================================
# TEST 25 — aucun apply/commit/push automatique
# =============================================================================

def test_25_no_auto_commit_push() -> None:
    import re as _re
    src = _src()
    patterns = [
        r'subprocess\.[a-z]+\s*\(\s*["\'].*git\s+(commit|push|deploy)',
        r'os\.system\s*\(\s*["\'].*git\s+(commit|push|deploy)',
        r'run\s*\(\s*\[["\']git["\'],\s*["\'](?:commit|push|deploy)',
    ]
    for pat in patterns:
        m = _re.search(pat, src, _re.IGNORECASE)
        assert m is None, f"Invocation git detectee dans CLI : {m.group(0)}"


# =============================================================================
# TEST 26 — suite complete des tests gates passe (smoke check imports)
# =============================================================================

def test_26_cli_compiles_and_imports() -> None:
    import py_compile
    py_compile.compile(str(_CLI), doraise=True)
    # Les fonctions V2 sont presentes
    assert hasattr(cli, "build_surface_model")
    assert hasattr(cli, "extract_status_panel")
    assert hasattr(cli, "extract_tools_panel")
    assert hasattr(cli, "extract_proof_panel")
    assert hasattr(cli, "format_surface_response")
    assert hasattr(cli, "_SURFACE_FILTER_TOKENS")
    assert hasattr(cli, "_SUITE_WORDS")
    assert hasattr(cli, "_TAB_COMMANDS")
