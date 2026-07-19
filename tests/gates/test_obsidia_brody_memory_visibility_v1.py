"""test_obsidia_brody_memory_visibility_v1 — OBSIDIA_TERMINAL_BRODY_MEMORY_VISIBILITY_V1.

Scope : vérifier la visibilité readonly Brody Memory dans le terminal.
  - collect_brody_memory_visibility_v1 readonly contract
  - collect_brody_graphiti_guard_visibility_v1 readonly contract
  - collect_brody_rights_visibility_v1 readonly contract
  - format contient les markers requis
  - smokes CLI : status brody memory / brody memory status
  - missing root est safe (monkeypatch)
  - aucun subprocess / no auto-act
  - aucune commande write/create/update/delete proposee
  - aucune decision souveraine emise

Aucun serveur. Aucune ecriture memoire. READONLY strict.
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
# TEST 01 — collect_brody_memory_visibility_v1 retourne le readonly contract
# =============================================================================

def test_01_brody_memory_visibility_readonly_contract() -> None:
    result = cli.collect_brody_memory_visibility_v1()
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("memory_write") is False, (
        f"memory_write doit etre False, obtenu {result.get('memory_write')}"
    )
    assert result.get("sovereign") is False, (
        f"sovereign doit etre False, obtenu {result.get('sovereign')}"
    )
    assert result.get("version") == "OBSIDIA_TERMINAL_BRODY_MEMORY_VISIBILITY_V1"
    assert "status" in result
    assert "root_exists" in result
    assert isinstance(result.get("commands_only"), list)


# =============================================================================
# TEST 02 — collect_brody_graphiti_guard_visibility_v1 readonly contract
# =============================================================================

def test_02_graphiti_guard_visibility_readonly_contract() -> None:
    result = cli.collect_brody_graphiti_guard_visibility_v1()
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("memory_write") is False, (
        f"memory_write doit etre False, obtenu {result.get('memory_write')}"
    )
    assert "status" in result
    assert result.get("status") in ("OK", "MISSING", "PARTIAL", "READ_ERROR")


# =============================================================================
# TEST 03 — collect_brody_rights_visibility_v1 readonly contract
# =============================================================================

def test_03_rights_visibility_readonly_contract() -> None:
    result = cli.collect_brody_rights_visibility_v1()
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("sovereign") is False, (
        f"sovereign doit etre False, obtenu {result.get('sovereign')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert "status" in result
    assert result.get("status") in ("OK", "MISSING", "PARTIAL", "READ_ERROR")


# =============================================================================
# TEST 04 — format_brody_memory_visibility_v1 contient les markers requis
# =============================================================================

def test_04_brody_memory_format_contains_required_markers() -> None:
    resp = cli.build_brody_memory_visibility_response_v1("status brody memory", _REG)
    text = cli.format_brody_memory_visibility_v1(resp)
    for marker in (
        "OBSIDIA_TERMINAL_BRODY_MEMORY_VISIBILITY_V1",
        "READONLY",
        "KX108_ONLY",
        "auto_execution=False",
        "memory_write=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )


# =============================================================================
# TEST 05 — smoke CLI : status brody memory
# =============================================================================

def test_05_cli_status_brody_memory_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "brody", "memory"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, (
        f"Exit code doit etre 0.\nStderr: {result.stderr[:300]}"
    )
    assert "BRODY_MEMORY" in out, f"BRODY_MEMORY manquant.\nSortie: {out[:400]}"
    assert "READONLY" in out, f"READONLY manquant.\nSortie: {out[:400]}"
    assert "memory_write=False" in out, f"memory_write=False manquant.\nSortie: {out[:400]}"


# =============================================================================
# TEST 06 — smoke CLI : brody memory status
# =============================================================================

def test_06_cli_brody_memory_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "brody", "memory", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, (
        f"Exit code doit etre 0.\nStderr: {result.stderr[:300]}"
    )
    assert "BRODY_MEMORY" in out, f"BRODY_MEMORY manquant.\nSortie: {out[:400]}"
    assert "READONLY" in out, f"READONLY manquant.\nSortie: {out[:400]}"
    assert "auto_execution=False" in out, f"auto_execution=False manquant.\nSortie: {out[:400]}"


# =============================================================================
# TEST 07 — missing memory root est safe (status=MISSING, pas d'exception)
# =============================================================================

def test_07_missing_memory_root_is_safe(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
    result = cli.collect_brody_memory_visibility_v1()
    assert result.get("status") == "MISSING", (
        f"status attendu MISSING quand root absent, obtenu {result.get('status')}"
    )
    assert result.get("root_exists") is False
    assert result.get("auto_execution") is False
    assert result.get("memory_write") is False


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
# TEST 09 — aucune commande write/create/update/delete dans commands_only
# =============================================================================

def test_09_no_memory_write_tokens_in_commands() -> None:
    resp = cli.build_brody_memory_visibility_response_v1("status brody memory", _REG)
    text = cli.format_brody_memory_visibility_v1(resp)
    cmds_section = ""
    in_cmds = False
    for line in text.splitlines():
        if "COMMANDS_ONLY" in line:
            in_cmds = True
            continue
        if in_cmds and line.startswith("  ") and "python" in line:
            cmds_section += line.lower() + "\n"
        elif in_cmds and not line.startswith("  ") and line.strip():
            in_cmds = False
    for forbidden in ("write", "create", "update", "delete", "apply", "commit", "push"):
        assert forbidden not in cmds_section, (
            f"Commande avec '{forbidden}' ne doit pas etre dans COMMANDS_ONLY.\n"
            f"Commandes: {cmds_section}"
        )
    mem = cli.collect_brody_memory_visibility_v1()
    for cmd in (mem.get("commands_only") or []):
        for forbidden in ("write", "create", "update", "delete", "apply", "commit"):
            assert forbidden not in cmd.lower(), (
                f"La commande '{cmd}' contient '{forbidden}' — interdit."
            )


# =============================================================================
# TEST 10 — aucune emission souveraine ALLOW/BLOCK/HOLD/ACT dans la sortie
# =============================================================================

def test_10_no_terminal_sovereign_action() -> None:
    resp = cli.build_brody_memory_visibility_response_v1("status brody memory", _REG)
    text = cli.format_brody_memory_visibility_v1(resp)
    reponse_text = resp.get("reponse", "")
    combined = text + reponse_text
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse brody memory.\n"
            f"Texte: {combined[:300]}"
        )
