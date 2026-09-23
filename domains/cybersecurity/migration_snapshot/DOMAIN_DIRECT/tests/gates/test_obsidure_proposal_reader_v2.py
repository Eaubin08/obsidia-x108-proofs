"""test_obsidure_proposal_reader_v2 — OBSIDURE_PROPOSAL_READER_V2.

Scope : verifier le lecteur readonly des proposals Obsidure.
  - listing readonly
  - sécurité ID
  - read de proposal inexistante (safe)
  - diff commands COMMANDS_ONLY
  - forbidden actions visibles
  - smokes CLI
  - aucun subprocess / no auto-act

Aucun serveur. Aucun apply. READONLY strict.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_CLI = _CLI_DIR / "obsidia_cli.py"

sys.path.insert(0, str(_CLI_DIR))
import obsidia_cli as cli


# =============================================================================
# TEST 01 — list_obsidure_proposals_v2 retourne mode=READONLY
# =============================================================================

def test_01_proposal_reader_lists_readonly() -> None:
    result = cli.list_obsidure_proposals_v2()
    assert result.get("version") == "OBSIDURE_PROPOSAL_READER_V2", (
        f"version attendu OBSIDURE_PROPOSAL_READER_V2, obtenu {result.get('version')}"
    )
    assert result.get("mode") == "READONLY", (
        f"mode attendu READONLY, obtenu {result.get('mode')}"
    )
    assert result.get("auto_execution") is False, (
        f"auto_execution doit etre False, obtenu {result.get('auto_execution')}"
    )
    assert result.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority attendu KX108_ONLY, obtenu {result.get('decision_authority')}"
    )
    assert "items" in result, "items doit etre présent dans le retour"
    assert isinstance(result["items"], list), "items doit etre une liste"


# =============================================================================
# TEST 02 — IDs invalides sont rejetés proprement
# =============================================================================

def test_02_proposal_reader_rejects_unsafe_ids() -> None:
    unsafe_ids = [
        "../bad",
        "../../etc/passwd",
        "foo/bar",
        "foo\\bar",
        "C:\\Windows",
        "foo:bar",
        "foo*",
        "foo?",
        "/absolute",
        "",
        "a" * 200,
    ]
    for bad_id in unsafe_ids:
        safe = cli._safe_obsidure_proposal_id_v2(bad_id)
        assert safe == "", (
            f"_safe_obsidure_proposal_id_v2('{bad_id}') doit retourner '' "
            f"mais a retourné '{safe}'"
        )


# =============================================================================
# TEST 03 — IDs valides sont acceptés
# =============================================================================

def test_03_proposal_reader_accepts_safe_ids() -> None:
    safe_ids = [
        "my_proposal",
        "proposal-2024-01-01",
        "ABC_123",
        "lean-v2.fix",
        "short",
    ]
    for good_id in safe_ids:
        safe = cli._safe_obsidure_proposal_id_v2(good_id)
        assert safe == good_id, (
            f"_safe_obsidure_proposal_id_v2('{good_id}') doit retourner '{good_id}' "
            f"mais a retourné '{safe}'"
        )


# =============================================================================
# TEST 04 — read d'un ID inexistant est safe (pas d'exception, found=False)
# =============================================================================

def test_04_proposal_reader_read_missing_id_is_safe() -> None:
    result = cli.read_obsidure_proposal_v2("definitely_does_not_exist_xyz_9999")
    assert result.get("found") is False, (
        f"found doit etre False pour un ID inexistant, obtenu {result.get('found')}"
    )
    assert result.get("auto_execution") is False
    assert result.get("decision_authority") == "KX108_ONLY"
    assert result.get("mode") == "READONLY"


# =============================================================================
# TEST 05 — read d'un ID invalide retourne INVALID_PROPOSAL_ID
# =============================================================================

def test_05_proposal_reader_invalid_id_returns_proper_reason() -> None:
    result = cli.read_obsidure_proposal_v2("../bad/../id")
    assert result.get("found") is False
    assert result.get("reason") == "INVALID_PROPOSAL_ID", (
        f"reason attendu INVALID_PROPOSAL_ID, obtenu {result.get('reason')}"
    )
    assert result.get("auto_execution") is False
    assert result.get("mode") == "READONLY"


# =============================================================================
# TEST 06 — diff commands contient COMMANDS_ONLY et WAITING_FOR_HUMAN
# =============================================================================

def test_06_proposal_reader_commands_only_diff() -> None:
    cmds = cli.build_obsidure_proposal_diff_commands_v2({
        "proposal_id": "test_proposal_xyz",
        "scope_files": ["scripts/obsidia_cli.py"],
    })
    assert isinstance(cmds, list), "build_obsidure_proposal_diff_commands_v2 doit retourner une list"
    combined = "\n".join(cmds)
    assert "COMMANDS_ONLY" in combined, "Le résultat doit contenir COMMANDS_ONLY"
    assert "WAITING_FOR_HUMAN" in combined, "Le résultat doit contenir WAITING_FOR_HUMAN"
    # Vérifier qu'aucune commande n'est exécutée (pas de subprocess côté test)
    assert len(cmds) > 0


# =============================================================================
# TEST 07 — forbidden_actions visibles dans read_obsidure_proposal_v2
# =============================================================================

def test_07_proposal_reader_forbidden_actions_visible() -> None:
    result = cli.read_obsidure_proposal_v2("nonexistent_proposal_xyz")
    forbidden = result.get("forbidden_actions") or []
    for action in ("apply", "commit", "push", "deploy"):
        assert action in forbidden, (
            f"'{action}' doit etre dans forbidden_actions, obtenu {forbidden}"
        )


# =============================================================================
# TEST 08 — build_obsidure_proposal_reader_response_v2 retourne les champs clés
# =============================================================================

def test_08_proposal_reader_response_v2_structure() -> None:
    import obsidia_cli as _cli
    registry = _cli.load_registry(_cli.REGISTRY_PATH)
    resp = _cli.build_obsidure_proposal_reader_response_v2("proposal list", registry)
    assert resp.get("panel") == "OBSIDURE_PROPOSAL_READER_V2"
    assert resp.get("mode_reponse") == "ANSWER_LOCAL"
    assert resp.get("output") == "COMMANDS"
    etat = resp.get("etat_technique", {})
    assert etat.get("auto_execution") is False
    assert etat.get("decision_authority") == "KX108_ONLY"
    assert etat.get("subprocess") == "none"
    assert etat.get("mutation") == "none"


# =============================================================================
# TEST 09 — smoke CLI : proposal list
# =============================================================================

def test_09_cli_proposal_list_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "proposal", "list"],
        capture_output=True, text=True, timeout=30,
    )
    out = result.stdout
    assert "OBSIDURE_PROPOSAL_READER_V2" in out, (
        f"La sortie doit contenir OBSIDURE_PROPOSAL_READER_V2.\nSortie: {out[:400]}"
    )
    assert "READONLY" in out, f"La sortie doit contenir READONLY.\nSortie: {out[:400]}"
    assert "auto_execution=False" in out, (
        f"La sortie doit contenir auto_execution=False.\nSortie: {out[:400]}"
    )


# =============================================================================
# TEST 10 — smoke CLI : proposal read avec ID invalide
# =============================================================================

def test_10_cli_proposal_invalid_id_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "proposal", "read", "../bad"],
        capture_output=True, text=True, timeout=30,
    )
    out = result.stdout
    assert "INVALID_PROPOSAL_ID" in out, (
        f"La sortie doit contenir INVALID_PROPOSAL_ID.\nSortie: {out[:400]}"
    )
    assert result.returncode == 0, (
        f"Exit code doit etre 0 (pas de crash).\nStderr: {result.stderr[:200]}"
    )


# =============================================================================
# TEST 11 — smoke CLI : proposal diff avec ID invalide
# =============================================================================

def test_11_cli_proposal_diff_invalid_id_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "proposal", "diff", "../bad"],
        capture_output=True, text=True, timeout=30,
    )
    out = result.stdout
    assert "INVALID_PROPOSAL_ID" in out or "READONLY" in out, (
        f"La sortie doit contenir INVALID_PROPOSAL_ID ou READONLY.\nSortie: {out[:400]}"
    )
    assert result.returncode == 0, (
        f"Exit code doit etre 0 (pas de crash).\nStderr: {result.stderr[:200]}"
    )


# =============================================================================
# TEST 12 — smoke CLI : mode answer router sur "obsidure proposal reader"
# =============================================================================

def test_12_cli_obsidure_runtime_smoke() -> None:
    result = subprocess.run(
        [sys.executable, str(_CLI), "obsidure proposal reader"],
        capture_output=True, text=True, timeout=30,
    )
    out = result.stdout + result.stderr
    assert result.returncode == 0, f"Pas de crash attendu.\nSortie: {out[:400]}"
    assert len(result.stdout.strip()) > 0, "La sortie doit etre non vide"


# =============================================================================
# TEST 13 — aucun subprocess dans le CLI source (guard statique regex)
# =============================================================================

def test_13_static_no_subprocess_or_process_spawn() -> None:
    import re
    src = _CLI.read_text(encoding="utf-8")
    assert "import subprocess" not in src, "import subprocess interdit dans le CLI"
    assert re.search(r'os\.system\s*\(', src) is None, "os.system() interdit dans le CLI"
    assert re.search(r'shell\s*=\s*True', src) is None, "shell=True interdit dans le CLI"
    assert re.search(r'Start-Process\b', src) is None, "Start-Process interdit dans le CLI"


# =============================================================================
# TEST 14 — aucune émission souveraine ALLOW/BLOCK/HOLD/ACT
# =============================================================================

def test_14_no_authority_emission() -> None:
    import obsidia_cli as _cli
    registry = _cli.load_registry(_cli.REGISTRY_PATH)
    for raw in ("proposal list", "proposal read nonexistent_xyz", "proposal diff nonexistent_xyz"):
        resp = _cli.build_obsidure_proposal_reader_response_v2(raw, registry)
        text = resp.get("reponse", "")
        for forbidden_token in ("X108Gate.ALLOW", "X108Gate.BLOCK", "X108Gate.HOLD",
                                "X108Gate.ACT", "EMIT_ALLOW", "EMIT_BLOCK", "EMIT_HOLD",
                                "EMIT_ACT"):
            assert forbidden_token not in text, (
                f"'{forbidden_token}' ne doit pas apparaitre dans la reponse proposal reader.\n"
                f"raw='{raw}'\nTexte: {text[:300]}"
            )


# =============================================================================
# TEST 15 — list positif si _PATCH_PROPOSALS/ existe
# =============================================================================

def test_15_proposal_reader_list_positive_if_dir_exists() -> None:
    import obsidia_cli as _cli
    root = _cli._obsidure_proposals_root_v2()
    result = _cli.list_obsidure_proposals_v2(limit=5)
    if root.exists():
        assert result.get("status") == "OK", (
            f"Si le dossier existe, status doit etre OK. Obtenu: {result.get('status')}"
        )
        assert isinstance(result.get("count"), int)
        assert isinstance(result.get("items"), list)
    else:
        assert result.get("status") in ("NO_PROPOSALS_DIR", "READ_ERROR"), (
            f"Si le dossier n'existe pas, status doit etre NO_PROPOSALS_DIR. "
            f"Obtenu: {result.get('status')}"
        )
        assert result.get("count") == 0
        assert result.get("items") == []
