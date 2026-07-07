"""test_obsidia_sigma_oie_status_panel_v1 — OBSIDIA_TERMINAL_SIGMA_OIE_STATUS_PANEL_V1.

Scope : vérifier le panneau de statut Sigma/OIE readonly dans le terminal.
  - collect_sigma_status_v1 retourne les bons champs
  - collect_oie_reports_v1 retourne les bons champs
  - build_sigma_oie_status_response_v1 retourne mode=READONLY + KX108_ONLY
  - format_sigma_oie_status_v1 contient SIGMA/OIE + COMMANDS_ONLY
  - smokes CLI : status sigma / status oie / sigma status / oie status
  - aucun subprocess / no auto-act

Aucun serveur. Aucun apply. READONLY strict.
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
# TEST 01 — collect_sigma_status_v1 retourne guidance, label, mode=READONLY
# =============================================================================

def test_01_collect_sigma_status_v1_returns_required_fields() -> None:
    result = cli.collect_sigma_status_v1(_REG)
    assert "guidance" in result, "guidance doit etre present"
    assert "labels" in result, "labels doit etre present"
    assert isinstance(result["labels"], dict), "labels doit etre un dict"
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )


# =============================================================================
# TEST 02 — collect_oie_reports_v1 retourne status + reports_found
# =============================================================================

def test_02_collect_oie_reports_v1_returns_required_fields() -> None:
    result = cli.collect_oie_reports_v1()
    assert "status" in result, "status doit etre present"
    assert "reports_found" in result, "reports_found doit etre present"
    assert isinstance(result["reports_found"], int), "reports_found doit etre un int"
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )


# =============================================================================
# TEST 03 — build_sigma_oie_status_response_v1 retourne mode=READONLY + KX108_ONLY
# =============================================================================

def test_03_build_sigma_oie_status_response_v1_structure() -> None:
    sigma_resp = cli.build_status_response("sigma status", "sigma", _REG)
    data = cli.build_sigma_oie_status_response_v1(sigma_resp, _REG)
    assert data.get("mode_reponse") == "ANSWER_STATUS", (
        f"mode_reponse attendu ANSWER_STATUS, obtenu {data.get('mode_reponse')}"
    )
    assert data.get("output") == "COMMANDS", (
        f"output attendu COMMANDS, obtenu {data.get('output')}"
    )
    etat = data.get("etat_technique", {})
    assert etat.get("mode") == "READONLY"
    assert etat.get("decision_authority") == "KX108_ONLY"
    assert etat.get("auto_execution") is False


# =============================================================================
# TEST 04 — format_sigma_oie_status_v1 contient SIGMA, COMMANDS_ONLY, FORBIDDEN
# =============================================================================

def test_04_format_sigma_oie_status_v1_markers() -> None:
    sigma_resp = cli.build_status_response("sigma status", "sigma", _REG)
    data = cli.build_sigma_oie_status_response_v1(sigma_resp, _REG)
    text = cli.format_sigma_oie_status_v1(data)
    assert "SIGMA" in text, f"format doit contenir SIGMA.\nTexte: {text[:400]}"
    assert "COMMANDS_ONLY" in text, f"format doit contenir COMMANDS_ONLY.\nTexte: {text[:400]}"
    assert "FORBIDDEN" in text or "forbidden" in text.lower(), (
        f"format doit contenir FORBIDDEN.\nTexte: {text[:400]}"
    )
    assert "auto_execution=False" in text, (
        f"format doit contenir auto_execution=False.\nTexte: {text[:400]}"
    )
    assert "KX108_ONLY" in text, (
        f"format doit contenir KX108_ONLY.\nTexte: {text[:400]}"
    )


# =============================================================================
# TEST 05 — smoke CLI : status sigma
# =============================================================================

def test_05_cli_status_sigma_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "sigma"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, (
        f"Exit code doit etre 0.\nStderr: {result.stderr[:300]}"
    )
    for marker in ("SIGMA", "OBSIDIA_TERMINAL_SIGMA_OIE_STATUS_PANEL_V1", "READONLY",
                   "auto_execution=False", "KX108_ONLY"):
        assert marker in out, (
            f"Marker '{marker}' manquant dans la sortie.\nSortie: {out[:500]}"
        )


# =============================================================================
# TEST 06 — smoke CLI : status oie
# =============================================================================

def test_06_cli_status_oie_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "status", "oie"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, (
        f"Exit code doit etre 0.\nStderr: {result.stderr[:300]}"
    )
    for marker in ("OIE", "OBSIDIA_TERMINAL_SIGMA_OIE_STATUS_PANEL_V1", "READONLY",
                   "auto_execution=False", "KX108_ONLY"):
        assert marker in out, (
            f"Marker '{marker}' manquant dans la sortie.\nSortie: {out[:500]}"
        )


# =============================================================================
# TEST 07 — aucun subprocess dans le CLI source (guard statique regex)
# =============================================================================

def test_07_static_no_subprocess_in_sigma_oie_block() -> None:
    src = _CLI.read_text(encoding="utf-8")
    assert "import subprocess" not in src, "import subprocess interdit dans le CLI"
    assert re.search(r'os\.system\s*\(', src) is None, "os.system() interdit dans le CLI"
    assert re.search(r'shell\s*=\s*True', src) is None, "shell=True interdit dans le CLI"
    assert re.search(r'Start-Process\b', src) is None, "Start-Process interdit dans le CLI"


# =============================================================================
# TEST 08 — aucune emission souveraine ALLOW/BLOCK/HOLD/ACT dans les reponses Sigma/OIE
# =============================================================================

def test_08_no_authority_emission_sigma_oie() -> None:
    for layer in ("sigma", "oie"):
        resp = cli.build_status_response(f"{layer} status", layer, _REG)
        data = cli.build_sigma_oie_status_response_v1(resp, _REG)
        text = cli.format_sigma_oie_status_v1(data)
        for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                                "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                                "EMIT_ACT"):
            assert forbidden_token not in text, (
                f"'{forbidden_token}' ne doit pas apparaitre dans la reponse {layer}.\n"
                f"Texte: {text[:300]}"
            )
