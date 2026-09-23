"""test_obsidia_domain_bridge_readonly_v1 — OBSIDIA_TERMINAL_DOMAIN_BRIDGE_READONLY_V1.

Scope : vérifier la visibilité readonly des domain bridges Bank/Trading/GPS.
  - contracts readonly par domaine (BANK, TRADING, GPS_DEFENSE_AVIATION)
  - collect_all contient les trois domaines
  - format contient les markers requis
  - smokes CLI : status domains / status bank / status trading / status gps
  - domaine inconnu safe
  - aucun subprocess / no auto-act
  - aucune commande d'action domaine proposée
  - aucune décision souveraine émise

Aucune transaction. Aucun trade. Aucun ordre GPS/aviation/defense. READONLY strict.
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


def _assert_readonly_contract(result: dict) -> None:
    assert result.get("version") == "OBSIDIA_TERMINAL_DOMAIN_BRIDGE_READONLY_V1"
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("api_role") == "BRIDGE_ONLY", (
        f"api_role attendu BRIDGE_ONLY, obtenu {result.get('api_role')}"
    )
    assert result.get("emits_act") is False, (
        f"emits_act doit etre False, obtenu {result.get('emits_act')}"
    )
    assert result.get("memory_write") is False, (
        f"memory_write doit etre False, obtenu {result.get('memory_write')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )


# =============================================================================
# TEST 01 — collect_domain_bridge_readonly_v1("bank") readonly contract
# =============================================================================

def test_01_domain_bridge_bank_readonly_contract() -> None:
    result = cli.collect_domain_bridge_readonly_v1("bank")
    _assert_readonly_contract(result)
    assert result.get("domain") == "BANK"
    assert result.get("status") in ("OK", "PARTIAL", "MISSING", "READ_ERROR")


# =============================================================================
# TEST 02 — collect_domain_bridge_readonly_v1("trading") readonly contract
# =============================================================================

def test_02_domain_bridge_trading_readonly_contract() -> None:
    result = cli.collect_domain_bridge_readonly_v1("trading")
    _assert_readonly_contract(result)
    assert result.get("domain") == "TRADING"
    assert result.get("status") in ("OK", "PARTIAL", "MISSING", "READ_ERROR")


# =============================================================================
# TEST 03 — collect_domain_bridge_readonly_v1("gps") readonly contract
# =============================================================================

def test_03_domain_bridge_gps_readonly_contract() -> None:
    for alias in ("gps", "aviation", "defense"):
        result = cli.collect_domain_bridge_readonly_v1(alias)
        _assert_readonly_contract(result)
        assert result.get("domain") == "GPS_DEFENSE_AVIATION", (
            f"alias '{alias}' doit normaliser vers GPS_DEFENSE_AVIATION, "
            f"obtenu {result.get('domain')}"
        )


# =============================================================================
# TEST 04 — collect_all contient les trois domaines
# =============================================================================

def test_04_domain_bridge_all_contains_three_domains() -> None:
    result = cli.collect_all_domain_bridges_readonly_v1()
    domains = result.get("domains", {})
    for name in ("BANK", "TRADING", "GPS_DEFENSE_AVIATION"):
        assert name in domains, f"'{name}' doit etre dans domains"
    assert result.get("api_role") == "BRIDGE_ONLY"
    assert result.get("emits_act") is False
    assert result.get("memory_write") is False
    assert result.get("auto_execution") is False


# =============================================================================
# TEST 05 — format contient les markers requis
# =============================================================================

def test_05_domain_bridge_format_contains_required_markers() -> None:
    resp = cli.build_domain_bridge_status_response_v1("status domains", _REG)
    text = cli.format_domain_bridge_status_v1(resp)
    for marker in (
        "OBSIDIA_TERMINAL_DOMAIN_BRIDGE_READONLY_V1",
        "READONLY",
        "KX108_ONLY",
        "BRIDGE_ONLY",
        "emits_act=False",
        "memory_write=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )


# =============================================================================
# TEST 06 — smoke CLI : status domains
# =============================================================================

def test_06_cli_status_domains_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "domains"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, (
        f"Exit code doit etre 0.\nStderr: {result.stderr[:300]}"
    )
    assert "DOMAIN_BRIDGE_READONLY_V1" in out, f"Sortie: {out[:400]}"
    assert "BRIDGE_ONLY" in out, f"Sortie: {out[:400]}"
    assert "emits_act=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 07 — smoke CLI : status bank
# =============================================================================

def test_07_cli_status_bank_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "bank"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "BANK" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 08 — smoke CLI : status trading
# =============================================================================

def test_08_cli_status_trading_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "trading"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "TRADING" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 09 — smoke CLI : status gps
# =============================================================================

def test_09_cli_status_gps_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "gps"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert ("GPS" in out or "GPS_DEFENSE_AVIATION" in out), f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 10 — domaine inconnu est safe (status MISSING, pas d'exception)
# =============================================================================

def test_10_missing_domain_is_safe() -> None:
    result = cli.collect_domain_bridge_readonly_v1("nuclear_submarine_xyz")
    assert result.get("status") == "MISSING", (
        f"status attendu MISSING pour domaine inconnu, obtenu {result.get('status')}"
    )
    assert result.get("emits_act") is False
    assert result.get("memory_write") is False
    assert result.get("auto_execution") is False
    result_empty = cli.collect_domain_bridge_readonly_v1("")
    assert result_empty.get("status") == "MISSING"


# =============================================================================
# TEST 11 — aucun subprocess dans le CLI source (guard statique regex)
# =============================================================================

def test_11_no_subprocess_or_process_spawn() -> None:
    src = _CLI.read_text(encoding="utf-8")
    assert "import subprocess" not in src, "import subprocess interdit dans le CLI"
    assert re.search(r'os\.system\s*\(', src) is None, "os.system() interdit dans le CLI"
    assert re.search(r'shell\s*=\s*True', src) is None, "shell=True interdit dans le CLI"
    assert re.search(r'Start-Process\b', src) is None, "Start-Process interdit dans le CLI"


# =============================================================================
# TEST 12 — aucune commande d'action domaine dans les commandes proposees
# =============================================================================

def test_12_no_domain_action_commands() -> None:
    resp = cli.build_domain_bridge_status_response_v1("status domains", _REG)
    text = cli.format_domain_bridge_status_v1(resp)
    cmds: list[str] = []
    for dom in (resp.get("domain_bridge") or {}).get("domains", {}).values():
        cmds += dom.get("commands_only", [])
    in_cmds = False
    for line in text.splitlines():
        if "COMMANDS_ONLY" in line:
            in_cmds = True
            continue
        if in_cmds and line.startswith("  ") and line.strip():
            cmds.append(line.strip())
        elif in_cmds and not line.startswith("  ") and line.strip():
            in_cmds = False
    forbidden_tokens = ("transfer", "transaction", "trade execute", "order execute",
                        "gps command", "deploy", "write memory")
    for cmd in cmds:
        low = cmd.lower()
        for tok in forbidden_tokens:
            assert tok not in low, (
                f"La commande '{cmd}' contient '{tok}' — action domaine interdite."
            )


# =============================================================================
# TEST 13 — aucune emission souveraine ALLOW/BLOCK/HOLD/ACT dans la sortie
# =============================================================================

def test_13_no_terminal_sovereign_action() -> None:
    resp = cli.build_domain_bridge_status_response_v1("status domains", _REG)
    text = cli.format_domain_bridge_status_v1(resp)
    combined = text + resp.get("reponse", "")
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse domain bridge.\n"
            f"Texte: {combined[:300]}"
        )
