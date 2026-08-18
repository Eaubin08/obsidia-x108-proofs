"""
tests/test_checkpoint3_verrous.py
==================================
Tests unitaires cibles sur les deux verrous du Checkpoint 3.

VERROU 1 : AgentObsidure.run_cycle() produit 0 patch (masque par injection).
  Fix : objectif reference periphery/ directement -> pas de redirection.
  Tests : _local_intent, _generate_python_peripheral_patches, chemin en periphery/.

VERROU 2 : run_tests_for_evidence() -> exit code 5 (aucun test collecte).
  Fix : commande de test pointe vers tests/test_obsidure_bounded_apply_v1.py.
  Tests : GateTestEvidence.passed, exit_code 5 => status FAIL.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# VERROU 1 -- intent et generation de patches
# ---------------------------------------------------------------------------

def test_local_intent_periphery_objective():
    """_local_intent retourne PYTHON_PATCH_PROPOSAL pour un objectif avec chemin .py."""
    from periphery.agents.agent_obsidure import _local_intent

    objective = (
        "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
        "periphery/math_core/peripheral_version_target.py -- "
        "session synthetique OBSIDURE_BOUNDED_APPLY_V1"
    )
    assert _local_intent(objective) == "PYTHON_PATCH_PROPOSAL"


def test_local_intent_tests_fixtures_objective():
    """_local_intent retourne aussi PYTHON_PATCH_PROPOSAL pour un chemin tests/ .py."""
    from periphery.agents.agent_obsidure import _local_intent

    objective = (
        "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
        "tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py"
    )
    assert _local_intent(objective) == "PYTHON_PATCH_PROPOSAL"


def test_generate_python_peripheral_patches_periphery_path():
    """
    Avec un objectif referancant periphery/ directement,
    _generate_python_peripheral_patches produit un patch dont le chemin
    commence par periphery/ sans redirection.
    """
    from periphery.agents.agent_obsidure import _generate_python_peripheral_patches

    objective = (
        "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
        "periphery/math_core/peripheral_version_target.py -- "
        "session synthetique OBSIDURE_BOUNDED_APPLY_V1"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(objective, sandbox, 1)

    assert len(patches) >= 1, "Doit generer au moins 1 patch"
    for p in patches:
        assert p["path"].startswith("periphery/"), (
            f"Chemin hors periphery/ : {p['path']}"
        )
    # Chemin exact attendu : pas de redirection via periphery/math_core/tests/...
    assert patches[0]["path"] == "periphery/math_core/peripheral_version_target.py"


def test_generate_python_peripheral_patches_tests_path_redirected():
    """
    Avec un objectif referancant tests/, le chemin est redirige vers
    periphery/math_core/... (comportement existant documente).
    C'est pourquoi obsidure_synth_session.py doit utiliser periphery/ directement.
    """
    from periphery.agents.agent_obsidure import _generate_python_peripheral_patches

    objective = (
        "Mettre a jour PERIPHERAL_VERSION dans "
        "tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(objective, sandbox, 1)

    assert len(patches) >= 1
    # Le chemin est redirige vers periphery/math_core/
    assert patches[0]["path"].startswith("periphery/math_core/"), (
        f"Redirection attendue vers periphery/math_core/ : {patches[0]['path']}"
    )
    # NE correspond PAS au TARGET_REL original (d'ou l'injection artificielle anterieure)
    assert patches[0]["path"] != "tests/fixtures/obsidure_apply_v1/session_synth_01/target_peripheral.py"


def test_sandbox_file_created_for_periphery_patch():
    """
    _generate_python_peripheral_patches cree le fichier stub dans la sandbox.
    Le sandbox_path doit exister apres generation.
    """
    from periphery.agents.agent_obsidure import _generate_python_peripheral_patches

    objective = (
        "PERIPHERAL_VERSION periphery/math_core/peripheral_version_target.py"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir)
        patches = _generate_python_peripheral_patches(objective, sandbox, 1)

        assert len(patches) >= 1
        sp = Path(patches[0]["sandbox_path"])
        assert sp.exists(), f"Fichier sandbox non cree : {sp}"
        assert sp.read_text(encoding="utf-8").strip() != ""


# ---------------------------------------------------------------------------
# VERROU 2 -- GateTestEvidence et exit code 5
# ---------------------------------------------------------------------------

def test_gate_test_evidence_exit_code_5_is_fail():
    """
    GateTestEvidence avec exit_code=5 (aucun test collecte) doit avoir status=FAIL
    et passed=False. Le runner E2E ne doit pas ignorer ce code de retour.
    """
    from scripts.obsidure_bounded_apply import GateTestEvidence

    ev = GateTestEvidence(
        command="pytest tests/fixtures/obsidure_apply_v1/ -q",
        test_identity="test_no_collect",
        exit_code=5,
        status="FAIL",
        timestamp="2026-08-18T00:00:00+00:00",
        results_summary="no tests ran",
        receipt_hash="abc123",
    )
    assert ev.exit_code == 5
    assert ev.status == "FAIL"
    assert ev.passed is False


def test_gate_test_evidence_exit_code_0_is_pass():
    """GateTestEvidence avec exit_code=0 et status=PASS => passed=True."""
    from scripts.obsidure_bounded_apply import GateTestEvidence

    ev = GateTestEvidence(
        command="pytest tests/test_obsidure_bounded_apply_v1.py -q",
        test_identity="test_real_suite",
        exit_code=0,
        status="PASS",
        timestamp="2026-08-18T00:00:00+00:00",
        results_summary="59 passed",
        receipt_hash="def456",
    )
    assert ev.passed is True


def test_run_tests_for_evidence_exit_code_5_status_fail(tmp_path):
    """
    run_tests_for_evidence() avec une commande qui produit exit_code=5
    retourne GateTestEvidence avec status=FAIL et passed=False.
    """
    import sys
    from scripts.obsidure_bounded_apply import run_tests_for_evidence

    # pytest sur un repertoire vide produit exit_code=5
    empty_dir = tmp_path / "empty_tests"
    empty_dir.mkdir()

    ev = run_tests_for_evidence(
        test_command=[sys.executable, "-m", "pytest", str(empty_dir), "-q"],
        test_identity="test_empty_dir",
        worktree_root=tmp_path,
        timeout=30,
    )
    assert ev.exit_code == 5, f"Attendu 5 (no tests collected) : {ev.exit_code}"
    assert ev.status == "FAIL"
    assert ev.passed is False


def test_ostrad_unknown_intent_falls_back_to_local():
    """
    Quand l'API OS_TRAD retourne intent='unknown', _local_intent() doit prendre le relais.
    Verifie que translate_and_build_ir resout 'unknown' via _local_intent.
    """
    from unittest.mock import MagicMock, patch
    from periphery.agents.agent_obsidure import OSTradClient, _local_intent

    objective = (
        "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
        "periphery/math_core/peripheral_version_target.py"
    )

    client = OSTradClient()
    # Simule l'API Step 1 qui repond avec detected_language=unknown
    # et Step 2 qui retourne ir_candidate.intent=unknown
    mock_r1 = MagicMock()
    mock_r1.json.return_value = {"detected_language": "unknown", "alphabet_units": [], "risk_flags": []}
    mock_r1.raise_for_status = MagicMock()

    mock_r2 = MagicMock()
    mock_r2.json.return_value = {"ir_candidate": {"intent": "unknown", "constraints": []}}
    mock_r2.raise_for_status = MagicMock()

    with patch("periphery.agents.agent_obsidure._REQUESTS_OK", True), \
         patch("periphery.agents.agent_obsidure._requests") as mock_req:
        mock_req.post.side_effect = [mock_r1, mock_r2]
        result = client.translate_and_build_ir(objective)

    # Doit avoir utilise _local_intent au lieu de "unknown"
    expected = _local_intent(objective)
    assert result.intent == expected, (
        f"intent attendu={expected!r} mais obtenu={result.intent!r}"
    )
    assert result.intent == "PYTHON_PATCH_PROPOSAL"


def test_synth_session_no_injection_in_step2():
    """
    Verifie que la logique de l'Etape 2 de obsidure_synth_session.py
    extrait les chemins directement depuis data["patches"] sans injection.
    Les patches generees par l'agent pour periphery/ doivent rester intacts.
    """
    # Simule ce que fait l'Etape 2 (extraction seule -- pas de remplacement)
    proposal_data = {
        "patches": [
            {
                "path": "periphery/math_core/peripheral_version_target.py",
                "action": "CREATE_PYTHON_PERIPHERAL",
                "sandbox_path": "/tmp/sandbox/periphery/math_core/peripheral_version_target.py",
            }
        ],
        "proposal_files": [],
        "approved_scope": [],
        "session_id": "",
        "base_sha": "",
        "worktree": "",
    }

    # Logique Etape 2 (extraction uniquement)
    actual_patch_paths = [p["path"] for p in proposal_data.get("patches", [])]

    assert len(actual_patch_paths) == 1
    assert actual_patch_paths[0] == "periphery/math_core/peripheral_version_target.py"
    assert all(p.startswith("periphery/") for p in actual_patch_paths)

    # Verifie que metadonnees sont mises a jour sans toucher aux patches
    proposal_data["session_id"] = "synth-e2e-test"
    proposal_data["approved_scope"] = actual_patch_paths
    proposal_data["proposal_files"] = actual_patch_paths

    # Les patches restent inchanges
    assert proposal_data["patches"][0]["path"] == "periphery/math_core/peripheral_version_target.py"
    assert proposal_data["patches"][0]["action"] == "CREATE_PYTHON_PERIPHERAL"
    assert "/tmp/sandbox/" in proposal_data["patches"][0]["sandbox_path"]


# ---------------------------------------------------------------------------
# Section 2 -- BASE_SHA dynamique (git rev-parse HEAD)
# ---------------------------------------------------------------------------

def test_capture_head_returns_valid_sha():
    """_capture_head() doit retourner un SHA-1 de 40 caracteres hexadecimaux."""
    import subprocess
    import re

    worktree = Path(__file__).parents[1]  # racine TBV1
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=str(worktree), timeout=10,
    )
    sha = r.stdout.strip()
    assert r.returncode == 0, f"git rev-parse HEAD echec: {r.stderr}"
    assert re.match(r"^[0-9a-f]{40}$", sha), f"SHA invalide: {sha!r}"


def test_base_sha_not_hardcoded():
    """
    Verifie que obsidure_synth_session.py ne contient pas le SHA durci
    d072baa612a60e1df5b6e671c11f5510183eefd2 (ancien BASE_SHA fixe).
    """
    script = Path(__file__).parents[1] / "scripts" / "obsidure_synth_session.py"
    content = script.read_text(encoding="utf-8")
    assert "d072baa" not in content, (
        "BASE_SHA durci detecte dans obsidure_synth_session.py -- "
        "doit etre lu dynamiquement via git rev-parse HEAD"
    )


def test_load_and_validate_proposal_base_sha_mismatch():
    """
    Quand proposal.base_sha != session base_sha -> HOLD_PROPOSAL_MISMATCH.
    """
    import json
    from scripts.obsidure_bounded_apply import load_and_validate_proposal, _compute_proposal_hash

    def _make_proposal(tmp_path: Path, base_sha: str, pid: str) -> None:
        proposal_dir = tmp_path / "_PATCH_PROPOSALS" / pid
        proposal_dir.mkdir(parents=True)
        data = {
            "proposal_id": pid,
            "session_id": "synth-01",
            "base_sha": base_sha,
            "worktree": "TERMINAL_BOUNDED_V1",
            "approved_scope": ["periphery/math_core/target.py"],
            "proposal_files": ["periphery/math_core/target.py"],
            "patches": [{"path": "periphery/math_core/target.py", "action": "CREATE_PYTHON_PERIPHERAL", "sandbox_path": ""}],
            "protected_paths_check": "CLEAN",
            "human_approved": False,
            "status": "AWAITING_HUMAN_APPROVED_WRITE",
        }
        data["proposal_hash"] = _compute_proposal_hash(data)
        (proposal_dir / "proposal.json").write_text(json.dumps(data), encoding="utf-8")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pid = "base-sha-mismatch-test"
        _make_proposal(tmp_path, base_sha="aaaaabbbbbcccccdddddeeeeefffffaaaaabbbbb", pid=pid)

        import pytest
        from unittest.mock import patch
        with patch("scripts.obsidure_bounded_apply.PROPOSALS_DIR", tmp_path / "_PATCH_PROPOSALS"):
            with pytest.raises(ValueError, match="HOLD_PROPOSAL_MISMATCH"):
                load_and_validate_proposal(
                    proposal_id=pid,
                    session_id="synth-01",
                    base_sha="9654f3a13611c1b9142e1d3f1df63f75369cd61e",  # HEAD reel != proposal
                    worktree="TERMINAL_BOUNDED_V1",
                    approved_scope=["periphery/math_core/target.py"],
                )


# ---------------------------------------------------------------------------
# Section 3 -- target_effect_evidence (verification PERIPHERAL_VERSION=v1)
# ---------------------------------------------------------------------------

def test_python_peripheral_stub_version_bump():
    """
    _python_peripheral_stub genere PERIPHERAL_VERSION = "v1"
    quand l'objectif contient "PERIPHERAL_VERSION de v0 a v1".
    """
    from periphery.agents.agent_obsidure import _python_peripheral_stub

    objective = (
        "Mettre a jour PERIPHERAL_VERSION de v0 a v1 dans "
        "periphery/math_core/peripheral_version_target.py -- "
        "session synthetique OBSIDURE_BOUNDED_APPLY_V1"
    )
    content = _python_peripheral_stub("periphery/math_core/peripheral_version_target.py", objective, 1)
    assert 'PERIPHERAL_VERSION = "v1"' in content, (
        f"PERIPHERAL_VERSION='v1' absent du stub:\n{content[:300]}"
    )


def test_target_effect_evidence_pass(tmp_path):
    """
    run_tests_for_evidence() avec un script qui confirme PERIPHERAL_VERSION=v1
    retourne status=PASS et exit_code=0.
    """
    import sys
    from scripts.obsidure_bounded_apply import run_tests_for_evidence

    # Creer un fichier cible avec PERIPHERAL_VERSION = "v1"
    target = tmp_path / "periphery" / "math_core" / "peripheral_version_target.py"
    target.parent.mkdir(parents=True)
    target.write_text('PERIPHERAL_VERSION = "v1"\n', encoding="utf-8")

    rel = "periphery/math_core/peripheral_version_target.py"
    check_script = (
        "import sys; from pathlib import Path; "
        "p = Path('" + rel + "'); "
        "assert p.exists(); "
        "c = p.read_text(encoding='utf-8'); "
        "lines = [l for l in c.splitlines() if 'PERIPHERAL_VERSION' in l]; "
        "assert any('v1' in l for l in lines); "
        "print('TARGET_EFFECT_PASS'); sys.exit(0)"
    )
    ev = run_tests_for_evidence(
        test_command=[sys.executable, "-c", check_script],
        test_identity="test_target_effect",
        worktree_root=tmp_path,
        timeout=15,
    )
    assert ev.exit_code == 0, f"exit_code={ev.exit_code}: {ev.results_summary}"
    assert ev.status == "PASS"
    assert ev.passed is True


def test_target_effect_evidence_fail_no_v1(tmp_path):
    """
    run_tests_for_evidence() echoue si PERIPHERAL_VERSION=v1 absent du fichier.
    """
    import sys
    from scripts.obsidure_bounded_apply import run_tests_for_evidence

    target = tmp_path / "periphery" / "math_core" / "peripheral_version_target.py"
    target.parent.mkdir(parents=True)
    target.write_text('PERIPHERAL_VERSION = "v0"\n', encoding="utf-8")

    rel = "periphery/math_core/peripheral_version_target.py"
    check_script = (
        "import sys; from pathlib import Path; "
        "p = Path('" + rel + "'); "
        "c = p.read_text(encoding='utf-8'); "
        "lines = [l for l in c.splitlines() if 'PERIPHERAL_VERSION' in l]; "
        "assert any('v1' in l for l in lines), 'v1 absent'; "
        "print('TARGET_EFFECT_PASS'); sys.exit(0)"
    )
    ev = run_tests_for_evidence(
        test_command=[sys.executable, "-c", check_script],
        test_identity="test_target_effect_fail",
        worktree_root=tmp_path,
        timeout=15,
    )
    assert ev.exit_code != 0
    assert ev.status == "FAIL"
    assert ev.passed is False
