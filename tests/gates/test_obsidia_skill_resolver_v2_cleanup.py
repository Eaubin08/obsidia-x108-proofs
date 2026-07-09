"""test_obsidia_skill_resolver_v2_cleanup — OBSIDIA_TERMINAL_SKILL_RESOLVER_V2_CLEANUP.

Scope : vérifier la classification readonly des skills.
  - readonly contract (resolver_authority=NONE, KX108_ONLY)
  - core skills classés USED
  - deferred skills classés INVENTORIED_ONLY/DEFERRED, jamais activés
  - format contient les markers requis
  - smokes CLI : skill resolver status / skills status / "show skills status"
  - aucun process-spawn
  - aucune autorité resolver
  - aucune décision souveraine émise

Le resolver classe. Il n'active rien. READONLY strict.
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
# TEST 01 — collect_skill_resolver_cleanup_v2 readonly contract
# =============================================================================

def test_01_skill_resolver_cleanup_readonly_contract() -> None:
    result = cli.collect_skill_resolver_cleanup_v2()
    assert result.get("version") == "OBSIDIA_TERMINAL_SKILL_RESOLVER_V2_CLEANUP", (
        f"version inattendue : {result.get('version')}"
    )
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert result.get("resolver_authority") == "NONE", (
        f"resolver_authority attendu NONE, obtenu {result.get('resolver_authority')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("mutation") == "none"
    assert result.get("subprocess") == "none"
    assert "summary" in result
    assert isinstance(result.get("skills"), dict)


# =============================================================================
# TEST 02 — core skills presents et classes USED
# =============================================================================

def test_02_skill_resolver_cleanup_contains_core_skills() -> None:
    result = cli.collect_skill_resolver_cleanup_v2()
    skills = result.get("skills", {})
    for name in ("brody", "obsidure", "sigma", "oie", "domains",
                 "lean_proof", "law_registry"):
        assert name in skills, f"Skill core manquant : {name}"
        assert skills[name].get("status") == "USED", (
            f"Skill '{name}' doit etre USED, obtenu {skills[name].get('status')}"
        )
        assert skills[name].get("surface"), (
            f"Skill '{name}' doit avoir une surface non vide"
        )


# =============================================================================
# TEST 03 — deferred skills classes proprement, jamais USED sans preuve
# =============================================================================

def test_03_skill_resolver_cleanup_classifies_deferred_skills() -> None:
    result = cli.collect_skill_resolver_cleanup_v2()
    skills = result.get("skills", {})
    for name in ("graph-calibrator", "module-mapper", "wiki-brain-bridge"):
        assert name in skills, f"Skill differe manquant : {name}"
        status = skills[name].get("status")
        assert status in ("INVENTORIED_ONLY", "DEFERRED", "MISSING"), (
            f"Skill '{name}' doit etre INVENTORIED_ONLY/DEFERRED/MISSING, "
            f"obtenu {status}"
        )
        assert status != "USED", (
            f"Skill '{name}' ne doit pas etre USED sans preuve reelle de branchement"
        )
        assert skills[name].get("decision") == "DEFERRED", (
            f"Skill '{name}' doit avoir decision=DEFERRED"
        )
        assert skills[name].get("surface") == [], (
            f"Skill '{name}' ne doit avoir aucune surface TUI"
        )


# =============================================================================
# TEST 04 — format contient les markers requis
# =============================================================================

def test_04_skill_resolver_cleanup_format_contains_required_markers() -> None:
    resp = cli.build_skill_resolver_cleanup_response_v2("skills status", _REG)
    text = cli.format_skill_resolver_cleanup_v2(resp)
    for marker in (
        "OBSIDIA_TERMINAL_SKILL_RESOLVER_V2_CLEANUP",
        "READONLY",
        "KX108_ONLY",
        "resolver_authority=NONE",
        "auto_execution=False",
        "COMMANDS_ONLY",
    ):
        assert marker in text, (
            f"Marker '{marker}' manquant dans le format.\nTexte: {text[:500]}"
        )


# =============================================================================
# TEST 05 — smoke CLI : skill resolver status
# =============================================================================

def test_05_cli_skill_resolver_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "skill", "resolver", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "SKILL_RESOLVER" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "resolver_authority=NONE" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 06 — smoke CLI : skills status
# =============================================================================

def test_06_cli_skills_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "skills", "status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "USED" in out, f"Sortie: {out[:400]}"
    assert "INVENTORIED_ONLY" in out, f"Sortie: {out[:400]}"
    assert "COMMANDS_ONLY" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 07 — smoke runtime : "show skills status"
# =============================================================================

def test_07_runtime_show_skills_status_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "show skills status"],
        capture_output=True, text=True, timeout=60,
    )
    out = result.stdout
    assert result.returncode == 0, f"Stderr: {result.stderr[:300]}"
    assert "SKILL" in out, f"Sortie: {out[:400]}"
    assert "READONLY" in out, f"Sortie: {out[:400]}"
    assert "auto_execution=False" in out, f"Sortie: {out[:400]}"


# =============================================================================
# TEST 08 — aucun process-spawn dans le CLI source
# =============================================================================

def test_08_no_subprocess_or_process_spawn() -> None:
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
# TEST 09 — aucune autorite donnee au resolver
# =============================================================================

def test_09_no_resolver_authority() -> None:
    resp = cli.build_skill_resolver_cleanup_response_v2("skills status", _REG)
    text = cli.format_skill_resolver_cleanup_v2(resp)
    assert "resolver_authority=NONE" in text, (
        f"resolver_authority=NONE doit etre visible.\nTexte: {text[:400]}"
    )
    etat = resp.get("etat_technique", {})
    assert etat.get("resolver_authority") == "NONE"
    outils = resp.get("outils_panel", {})
    assert outils.get("resolver_authority") == "NONE"
    resolver = resp.get("skill_resolver", {})
    assert resolver.get("resolver_authority") == "NONE"


# =============================================================================
# TEST 10 — aucune emission souveraine dans la sortie
# =============================================================================

def test_10_no_terminal_sovereign_action() -> None:
    resp = cli.build_skill_resolver_cleanup_response_v2("skills status", _REG)
    text = cli.format_skill_resolver_cleanup_v2(resp)
    combined = text + resp.get("reponse", "")
    for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                            "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                            "EMIT_ACT"):
        assert forbidden_token not in combined, (
            f"'{forbidden_token}' ne doit pas apparaitre dans la reponse resolver.\n"
            f"Texte: {combined[:300]}"
        )
    assert "no sovereign decision" in text, (
        "Le format doit rappeler 'no sovereign decision' dans FORBIDDEN"
    )
    assert "no automatic skill execution" in text, (
        "Le format doit rappeler 'no automatic skill execution' dans FORBIDDEN"
    )
