"""test_obsidia_terminal_law_registry_v1 — OBSIDIA_TERMINAL_LAW_REGISTRY_V1.

Scope : vérifier le registre readonly des lois terminales.
  - readonly contract (registry_authority=NONE, KX108_ONLY)
  - lois minimales présentes
  - panneaux récents répertoriés
  - format contient les markers requis
  - smokes CLI : law status / laws / "show terminal laws"
  - aucun process-spawn
  - aucune autorité registry
  - aucune décision souveraine émise

Le registry décrit. Il ne décide pas. READONLY strict.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_CLI = _CLI_DIR / "obsidia_cli.py"
_LAW_MODULE = _CLI_DIR / "obsidia_law_registry_v1.py"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_law_registry_v1 as law_registry


# =============================================================================
# TEST 01 — get_terminal_law_registry_v1 readonly contract
# =============================================================================

def test_01_law_registry_readonly_contract() -> None:
    result = law_registry.get_terminal_law_registry_v1()
    assert result.get("version") == "OBSIDIA_TERMINAL_LAW_REGISTRY_V1", (
        f"version attendu OBSIDIA_TERMINAL_LAW_REGISTRY_V1, obtenu {result.get('version')}"
    )
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("registry_authority") == "NONE", (
        f"registry_authority attendu NONE, obtenu {result.get('registry_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("mutation") == "none"
    assert result.get("subprocess") == "none"


# =============================================================================
# TEST 02 — lois minimales presentes
# =============================================================================

def test_02_law_registry_contains_required_laws() -> None:
    result = law_registry.get_terminal_law_registry_v1()
    law_ids = {law.get("id") for law in result.get("laws", [])}
    required = (
        "LAW_TERMINAL_NON_SOVEREIGN",
        "LAW_KX108_ONLY_DECISION_AUTHORITY",
        "LAW_COMMANDS_ONLY_FOR_RISKY_OPERATIONS",
        "LAW_NO_AUTO_EXECUTION",
        "LAW_MEMORY_IS_NOT_SOVEREIGN",
        "LAW_BRODY_IS_NOT_SOVEREIGN",
        "LAW_OBSIDURE_PROPOSES_ONLY",
        "LAW_SIGMA_ALERTS_ONLY",
        "LAW_OIE_REPORTS_ONLY",
        "LAW_DOMAINS_BRIDGE_ONLY",
        "LAW_LEAN_PROOF_COMMANDS_ONLY",
        "LAW_NO_MUTATION_WITHOUT_HUMAN",
        "LAW_RECEIPTS_ARE_AUDIT_NOT_AUTHORITY",
        "LAW_GATES_ARE_ADVISORY_IN_TERMINAL",
    )
    for law_id in required:
        assert law_id in law_ids, f"Loi manquante : {law_id}"
    for law in result.get("laws", []):
        for field in ("id", "title", "statement", "scope", "status"):
            assert field in law, f"Champ '{field}' manquant dans {law.get('id')}"
        assert law.get("status") == "ACTIVE"


# =============================================================================
# TEST 03 — panneaux recents repertories
# =============================================================================

def test_03_law_registry_panels_are_known() -> None:
    result = law_registry.get_terminal_law_registry_v1()
    panels = result.get("panels", {})
    for name in (
        "OBSIDURE_PROPOSAL_READER_V2",
        "SIGMA_OIE_STATUS_PANEL_V1",
        "BRODY_MEMORY_VISIBILITY_V1",
        "DOMAIN_BRIDGE_READONLY_V1",
        "LEAN_PROOF_PANEL_V1",
    ):
        assert name in panels, f"Panneau manquant : {name}"
        assert panels[name].get("mode") == "readonly", (
            f"Panneau {name} doit etre readonly, obtenu {panels[name].get('mode')}"
        )


# =============================================================================
# TEST 04 — format contient les markers requis
# =============================================================================

def test_04_law_registry_format_contains_required_markers() -> None:
    data = law_registry.get_terminal_law_panel_v1()
    text = law_registry.format_terminal_law_registry_v1(data)
    for marker in (
        "OBSIDIA_TERMINAL_LAW_REGISTRY_V1",
        "READONLY",
        "KX108_ONLY",
        "registry_authority=NONE",
        "auto_execution=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )


# =============================================================================
# TEST 05 — smoke CLI : law status
# =============================================================================

def test_05_cli_law_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "law", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "OBSIDIA_TERMINAL_LAW_REGISTRY_V1" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "registry_authority=NONE" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 06 — smoke CLI : laws
# =============================================================================

def test_06_cli_laws_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "laws"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "LAWS" in out, f"Sortie: {out[:400]}"
    assert "KX108_ONLY" in out, f"Sortie: {out[:400]}"
    assert "COMMANDS_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 07 — smoke runtime : "show terminal laws"
# =============================================================================

def test_07_runtime_show_terminal_laws_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "show terminal laws"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "LAW" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "auto_execution=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 08 — aucun process-spawn dans le module law registry ni le CLI
# =============================================================================

def test_08_no_subprocess_or_process_spawn() -> None:
    for path in (_CLI, _LAW_MODULE):
        src = path.read_text(encoding="utf-8")
        assert "import " + "subprocess" not in src, (
            f"import de module process interdit dans {path.name}"
        )
        assert re.search(r'os\.system\s*\(', src) is None, (
            f"execution de commande OS interdite dans {path.name}"
        )
        assert re.search(r'shell\s*=\s*True', src) is None, (
            f"execution shell interdite dans {path.name}"
        )
        assert re.search(r'Start-Process\b', src) is None, (
            f"process-spawn interdit dans {path.name}"
        )


# =============================================================================
# TEST 09 — aucune autorite donnee au registry
# =============================================================================

def test_09_no_registry_authority() -> None:
    data = law_registry.get_terminal_law_panel_v1()
    text = law_registry.format_terminal_law_registry_v1(data)
    assert "registry_authority=NONE" in text, (
        f"registry_authority=NONE doit etre visible.\nTexte: {text[:400]}"
    )
    etat = data.get("etat_technique", {})
    assert etat.get("registry_authority") == "NONE"
    outils = data.get("outils_panel", {})
    assert outils.get("registry_authority") == "NONE"


# =============================================================================
# TEST 10 — aucune emission souveraine dans la sortie
# =============================================================================

def test_10_no_terminal_sovereign_action() -> None:
    data = law_registry.get_terminal_law_panel_v1()
    text = law_registry.format_terminal_law_registry_v1(data)
    combined = text + data.get("reponse", "")
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse law registry.\n"
            f"Texte: {combined[:300]}"
        )
    assert "no sovereign decision" in text, (
        "Le format doit rappeler 'no sovereign decision' dans FORBIDDEN"
    )
