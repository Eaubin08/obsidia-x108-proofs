from __future__ import annotations
"""tests/test_jarjar_bridge_v0.py -- JarJar executor bridge V0 test suite."""
import hashlib, subprocess, sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS  = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
import obsidia_governed_execution_driver_v0 as DRV

_CONTENT_SRC = b"bridge-source-content\n"

def _sha256(b):
    return hashlib.sha256(b).hexdigest()

def _git(repo, *args):
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {args}: {proc.stderr}"
    return proc.stdout.strip()

@pytest.fixture
def bridge_world(tmp_path):
    main = tmp_path / "main"
    (main / "subdir").mkdir(parents=True)
    (main / "subdir" / "source.txt").write_bytes(_CONTENT_SRC)
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "bridge@test.com")
    _git(main, "config", "user.name", "bridgetest")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", "subdir/source.txt")
    _git(main, "commit", "-q", "-m", "bridge seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "bridge-test-br", base_sha)
    stores_base = tmp_path / "stores"
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha,
            "stores_base": stores_base,
            "src_abs": exec_wt / "subdir" / "source.txt",
            "dst_rel": "subdir/moved.txt",
            "src_rel": "subdir/source.txt"}

def _do_move_prepare(w, *, session_id=""):
    return PC2.pc_v2_move_file_prepare(
        source_path=w["src_rel"], dest_path=w["dst_rel"],
        execution_worktree_path=w["exec_wt"], main_worktree_path=w["main"],
        branch_name="bridge-test-br", base_sha=w["base_sha"],
        stores_base_dir=w["stores_base"], session_id=session_id)

def _do_cdir_prepare(w, *, dir_rel="subdir/newdir", session_id=""):
    return PC2.pc_v2_create_dir_prepare(
        dir_path=dir_rel,
        execution_worktree_path=w["exec_wt"], main_worktree_path=w["main"],
        branch_name="bridge-test-br", base_sha=w["base_sha"],
        stores_base_dir=w["stores_base"], session_id=session_id)

def _make_ok_move_executor():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"
    def _move(sa, da):
        da.parent.mkdir(parents=True, exist_ok=True)
        sa.rename(da)
        return {"ok": True, "error": None}
    ex.move_file.side_effect = _move
    return ex

def _make_ok_cdir_executor():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"
    def _mkdir(da):
        da.mkdir(parents=False, exist_ok=False)
        return {"ok": True, "error": None}
    ex.create_dir.side_effect = _mkdir
    return ex

def _make_fail_executor(error="SIMULATED_BACKEND_FAILURE"):
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"
    ex.move_file.return_value = {"ok": False, "error": error}
    ex.create_dir.return_value = {"ok": False, "error": error}
    return ex

# ---- T01 self_check invariants -----------------------------------------------
def test_self_check_invariants():
    from jarjar_executor_bridge_v0 import self_check_bridge_v0
    sc = self_check_bridge_v0()
    assert sc["openjarvis_authority"] == "NONE"
    assert sc["jarjar_authority"] == "NONE"
    assert sc["kx108_only"] is True
    assert sc["human_approval_required"] is True
    assert sc["generic_shell_enabled"] is False
    assert sc["makes_authorization_decisions"] is False
    assert sc["is_execution_authority"] is False
    assert sc["is_kx_authority"] is False
    assert sc["new_parallel_mutation_engine"] is False

# ---- T02 PREPARE ne declenche pas executor -----------------------------------
def test_prepare_does_not_invoke_executor(bridge_world):
    w = bridge_world
    before = w["src_abs"].read_bytes()
    out = _do_move_prepare(w)
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert w["src_abs"].read_bytes() == before

# ---- T03 mauvais EAH bloque avant executor -----------------------------------
def test_wrong_eah_blocks_before_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    out = _do_move_prepare(w)
    result = PC2.pc_v2_move_file_execute(
        out, "a" * 64, "HUMAN_REF",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result.get("reason") == "EAH_MISMATCH" or result["status"] == "EAH_MISMATCH"
    assert w["src_abs"].exists()
    ex.move_file.assert_not_called()

# ---- T04 ref humaine manquante bloque avant executor -------------------------
def test_missing_human_ref_blocks_before_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        out, eah, "",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result.get("reason") == "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED" or result["status"] == "HUMAN_AUTHORIZATION_REFERENCE_REQUIRED"
    ex.move_file.assert_not_called()

# ---- T05 phase incorrecte bloque avant executor ------------------------------
def test_wrong_phase_blocks_before_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    fake = {"j5_phase": "EXECUTE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
            "execution_authority_hash": "b" * 64}
    result = PC2.pc_v2_move_file_execute(
        fake, "b" * 64, "HUMAN_REF",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] not in (PC2.EXECUTED_OK,)
    ex.move_file.assert_not_called()

# ---- T06 statut incorrect bloque avant executor ------------------------------
def test_wrong_status_blocks_before_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    fake = {"j5_phase": "PREPARE", "status": "PREPARE_REJECTED",
            "execution_authority_hash": "b" * 64}
    result = PC2.pc_v2_move_file_execute(
        fake, "b" * 64, "HUMAN_REF",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] not in (PC2.EXECUTED_OK,)
    ex.move_file.assert_not_called()

# ---- A. MOVE_FILE avec executor injecte -------------------------------------
def test_move_file_with_jarjar_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        out, eah, "HUMAN_BRIDGE_TEST_MOVE",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] == PC2.EXECUTED_OK, result
    ex.move_file.assert_called_once()
    dst_abs = w["exec_wt"] / w["dst_rel"]
    assert dst_abs.exists() and not w["src_abs"].exists()
    assert _sha256(dst_abs.read_bytes()) == _sha256(_CONTENT_SRC)
    assert result["j5_phase"] == "EXECUTE"
    assert result["human_authorization_consumed"] is True
    assert result["kx108_pre_gate"] == "ALLOW"
    assert result.get("executor_provider") == "JARJAR"
    assert result.get("executor_backend") == "NativeFilesystemBackend"

# ---- B. CREATE_DIR avec executor injecte ------------------------------------
def test_create_dir_with_jarjar_executor(bridge_world):
    w = bridge_world
    ex = _make_ok_cdir_executor()
    out = _do_cdir_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        out, eah, "HUMAN_BRIDGE_TEST_CDIR",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] == PC2.EXECUTED_OK, result
    ex.create_dir.assert_called_once()
    dir_abs = w["exec_wt"] / "subdir" / "newdir"
    assert dir_abs.exists() and dir_abs.is_dir()
    assert result["j5_phase"] == "EXECUTE"
    assert result.get("executor_provider") == "JARJAR"
    assert result.get("executor_backend") == "NativeFilesystemBackend"

# ---- C. executor=None fallback historique inchange --------------------------
def test_move_file_executor_none_fallback(bridge_world):
    w = bridge_world
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        out, eah, "HUMAN_FALLBACK_MOVE",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    dst_abs = w["exec_wt"] / w["dst_rel"]
    assert dst_abs.exists() and not w["src_abs"].exists()
    assert result.get("executor_provider") == "OS_NATIVE"
    assert result.get("executor_backend") == "os.replace"

def test_create_dir_executor_none_fallback(bridge_world):
    w = bridge_world
    out = _do_cdir_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        out, eah, "HUMAN_FALLBACK_CDIR",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"])
    assert result["status"] == PC2.EXECUTED_OK, result
    dir_abs = w["exec_wt"] / "subdir" / "newdir"
    assert dir_abs.exists() and dir_abs.is_dir()

# ---- D. backend failure MOVE_FILE fail closed --------------------------------
def test_move_file_backend_failure_fail_closed(bridge_world):
    w = bridge_world
    ex = _make_fail_executor()
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        out, eah, "HUMAN_FAIL_MOVE",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] != PC2.EXECUTED_OK
    assert "JARJAR_EXECUTOR_FAILED" in result.get("reason", "")
    assert w["src_abs"].exists()
    assert not (w["exec_wt"] / w["dst_rel"]).exists()

# ---- E. backend failure CREATE_DIR fail closed --------------------------------
def test_create_dir_backend_failure_fail_closed(bridge_world):
    w = bridge_world
    ex = _make_fail_executor()
    out = _do_cdir_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_create_dir_execute(
        out, eah, "HUMAN_FAIL_CDIR",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] != PC2.EXECUTED_OK
    assert "JARJAR_EXECUTOR_FAILED" in result.get("reason", "")
    assert not (w["exec_wt"] / "subdir" / "newdir").exists()

# ---- F. gouvernance : executor_backend dans le receipt / no bypass -----------
def test_executor_metadata_in_receipt(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    result = PC2.pc_v2_move_file_execute(
        out, eah, "HUMAN_META_CHECK",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] == PC2.EXECUTED_OK
    assert result.get("executor_provider") == "JARJAR"
    assert result.get("executor_backend") == "NativeFilesystemBackend"
    assert "sealed_apply_receipt_id" in result
    assert result["jarvis_authority"] == "NONE"
    assert result["decision_authority"] == "KX108_ONLY"

def test_no_kx108_bypass(bridge_world):
    w = bridge_world
    ex = _make_ok_move_executor()
    # tamper v2_exec_id -> DESCRIPTOR_EAH_MISMATCH before KX108/executor
    out = _do_move_prepare(w)
    eah = out["execution_authority_hash"]
    tampered = dict(out)
    tampered["v2_exec_id"] = "00000000000000000000000000000000"
    result = PC2.pc_v2_move_file_execute(
        tampered, eah, "HUMAN_REF",
        stores_base_dir=w["stores_base"], repo_root=w["exec_wt"], executor=ex)
    assert result["status"] not in (PC2.EXECUTED_OK,)
    assert result["status"] == PC2.EXECUTE_REJECTED
    ex.move_file.assert_not_called()
