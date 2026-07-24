"""test_obsidia_lean_proof_panel_v1 — OBSIDIA_TERMINAL_LEAN_PROOF_PANEL_V1.

Scope : vérifier le panneau Lean/Proof readonly + COMMANDS_ONLY.
  - inventory readonly contract
  - missing root safe (monkeypatch)
  - format contient les markers requis
  - smokes CLI : proof status / lean status / status proof / "check lean proofs"
  - aucun subprocess / no auto-act
  - aucune exécution Lean automatique
  - aucune commande de mutation proof
  - aucune décision souveraine émise

Aucune exécution Lean. Aucun lake build. Aucune mutation proof. READONLY strict.
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
# TEST 01 — collect_lean_proof_inventory_v1 readonly contract
# =============================================================================

def test_01_lean_proof_inventory_readonly_contract() -> None:
    result = cli.collect_lean_proof_inventory_v1()
    assert result.get("version") == "OBSIDIA_TERMINAL_LEAN_PROOF_PANEL_V1"
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("proof_write") is False, (
        f"proof_write doit etre False, obtenu {result.get('proof_write')}"
    )
    assert result.get("subprocess") == "none"
    assert result.get("mutation") == "none"
    assert (result.get("labels") or {}).get("proof_check") == "COMMANDS_ONLY"
    assert result.get("status") in ("OK", "PARTIAL", "MISSING", "READ_ERROR")


# =============================================================================
# TEST 02 — missing root est safe (status=MISSING, pas d'exception)
# =============================================================================

def test_02_lean_proof_inventory_missing_safe(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    result = cli.collect_lean_proof_inventory_v1()
    assert result.get("status") == "MISSING", (
        f"status attendu MISSING quand root absent, obtenu {result.get('status')}"
    )
    assert result.get("root_exists") is False
    assert result.get("auto_execution") is False
    assert result.get("proof_write") is False


# =============================================================================
# TEST 03 — format contient les markers requis
# =============================================================================

def test_03_lean_proof_format_contains_required_markers() -> None:
    resp = cli.build_lean_proof_panel_response_v1("proof status", _REG)
    text = cli.format_lean_proof_panel_v1(resp)
    for marker in (
        "OBSIDIA_TERMINAL_LEAN_PROOF_PANEL_V1",
        "READONLY",
        "KX108_ONLY",
        "auto_execution=False",
        "proof_write=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )
    assert "WAITING_FOR_HUMAN" in text, (
        f"WAITING_FOR_HUMAN manquant.\nTexte: {text[:500]}"
    )


# =============================================================================
# TEST 04 — smoke CLI : proof status
# =============================================================================

def test_04_cli_proof_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "proof", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "LEAN_PROOF_PANEL" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "COMMANDS_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 05 — smoke CLI : lean status
# =============================================================================

def test_05_cli_lean_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "lean", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "LEAN" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "auto_execution=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 06 — smoke CLI : status proof
# =============================================================================

def test_06_cli_status_proof_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "proof"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert ("PROOF" in out or "LEAN" in out), f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 07 — smoke runtime : "check lean proofs"
# =============================================================================

def test_07_runtime_check_lean_proofs_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "check lean proofs"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "COMMANDS_ONLY" in out, f"Sortie: {out[:400]}"
    assert "auto_execution=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 08 — aucun subprocess dans le CLI source (guard statique regex)
# =============================================================================

def test_08_no_subprocess_or_process_spawn() -> None:
    src = _CLI.read_text(encoding="utf-8")
    assert "import subprocess" not in src, "import subprocess interdit dans le CLI"
    assert re.search(r'os\.system\s*\(', src) is None, "os.system() interdit dans le CLI"
    assert re.search(r'shell\s*=\s*True', src) is None, "shell=True interdit dans le CLI"
    assert re.search(r'Start-Process\b', src) is None, "Start-Process interdit dans le CLI"


# =============================================================================
# TEST 09 — aucune exécution Lean automatique
# =============================================================================

def test_09_no_automatic_lean_execution() -> None:
    inv = cli.collect_lean_proof_inventory_v1()
    resp = cli.build_lean_proof_panel_response_v1("proof status", _REG)
    text = cli.format_lean_proof_panel_v1(resp)
    # lake build / lake env / lean n'apparaissent que sous COMMANDS_ONLY
    before_cmds = text.split("COMMANDS_ONLY", 1)[0]
    assert "lake build" not in before_cmds, (
        "lake build ne doit apparaitre que sous COMMANDS_ONLY"
    )
    assert "lake env" not in before_cmds, (
        "lake env ne doit apparaitre que sous COMMANDS_ONLY"
    )
    # Le contrat inventory affirme subprocess=none et auto_execution=False
    assert inv.get("subprocess") == "none"
    assert inv.get("auto_execution") is False
    # Les commandes proposées existent bien mais uniquement en commands_only
    cmds = inv.get("commands_only") or []
    assert any("lake build" in c for c in cmds), "lake build doit etre propose en COMMANDS_ONLY"


# =============================================================================
# TEST 10 — aucune commande de mutation proof proposee
# =============================================================================

def test_10_no_proof_mutation_commands() -> None:
    inv = cli.collect_lean_proof_inventory_v1()
    for cmd in (inv.get("commands_only") or []):
        low = cmd.lower()
        for forbidden in ("write proof", "modify proof", "apply proof", "commit", "push"):
            assert forbidden not in low, (
                f"La commande '{cmd}' contient '{forbidden}' — mutation proof interdite."
            )


# =============================================================================
# TEST 11 — aucune emission souveraine ALLOW/BLOCK/HOLD/ACT dans la sortie
# =============================================================================

def test_11_no_terminal_sovereign_action() -> None:
    resp = cli.build_lean_proof_panel_response_v1("proof status", _REG)
    text = cli.format_lean_proof_panel_v1(resp)
    combined = text + resp.get("reponse", "")
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse lean proof.\n"
            f"Texte: {combined[:300]}"
        )
