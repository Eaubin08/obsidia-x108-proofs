from __future__ import annotations

import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from jarjar_governed_contract_v0 import (
    CONTRACT_VERSION,
    PHASE_EXECUTE,
    PHASE_PREPARE,
    PHASE_ROLLBACK_EXECUTE,
    PHASE_ROLLBACK_PREPARE,
    canonical_governed_result,
    self_check_contract_v0,
    validate_governed_contract,
)


def _ok(result, *, operation_type=None, phase=None):
    c = canonical_governed_result(
        result,
        operation_type=operation_type,
        phase=phase,
    )
    ok, reason = validate_governed_contract(c)
    assert ok, reason
    return c


def test_prepare_contract_normalizes_create_file_shape():
    c = _ok(
        {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "j5_phase": "PREPARE",
            "operation_type": "V2_CREATE_FILE",
            "decision_authority": "KX108_ONLY",
            "jarvis_authority": "NONE",
            "execution_authority_hash": "a" * 64,
            "target_path": "a.txt",
            "receipt": {"session_id": "g7-create"},
        }
    )
    assert c["contract_version"] == CONTRACT_VERSION
    assert c["phase"] == PHASE_PREPARE
    assert c["session_id"] == "g7-create"
    assert c["human_approval_required"] is True
    assert c["human_authorization_consumed"] is False


def test_execute_contract_normalizes_single_sre_to_list():
    c = _ok(
        {
            "status": "EXECUTED_OK",
            "j5_phase": "EXECUTE",
            "operation_type": "V2_CREATE_FILE",
            "decision_authority": "KX108_ONLY",
            "jarvis_authority": "NONE",
            "human_authorization_consumed": True,
            "sealed_rollback_evidence_id": "sre-one",
            "sealed_apply_receipt_id": "sar-one",
            "target_path": "a.txt",
            "executor_provider": "JARJAR",
            "executor_backend": "NativeFilesystemBackend",
        }
    )
    assert c["phase"] == PHASE_EXECUTE
    assert c["sealed_rollback_evidence_ids"] == ["sre-one"]
    assert c["sealed_apply_receipt_ids"] == ["sar-one"]


def test_execute_contract_preserves_multi_sre_shape():
    c = _ok(
        {
            "status": "EXECUTED_OK",
            "j5_phase": "EXECUTE",
            "operation_type": "V2_APPLY_PATCH",
            "decision_authority": "KX108_ONLY",
            "jarvis_authority": "NONE",
            "human_authorization_consumed": True,
            "sealed_rollback_evidence_ids": ["sre-a", "sre-b"],
            "sealed_apply_receipt_id": "sar-a",
            "target_paths": ["a.txt", "b.txt"],
        }
    )
    assert c["sealed_rollback_evidence_ids"] == ["sre-a", "sre-b"]
    assert c["target_paths"] == ["a.txt", "b.txt"]


def test_move_rollback_prepare_infers_canonical_phase():
    c = _ok(
        {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "sealed_rollback_evidence_id": "sre-move",
            "source_path": "a.txt",
            "dest_path": "b.txt",
            "rollback_authority_hash": "b" * 64,
            "rollback_authority": "SEALED_EVIDENCE_BOUND_RECOVERY",
            "decision_authority": "KX108_ONLY",
            "kx108_invocations_during_rollback": 0,
        },
        operation_type="V2_MOVE_FILE",
    )
    assert c["phase"] == PHASE_ROLLBACK_PREPARE
    assert c["sealed_rollback_evidence_ids"] == ["sre-move"]


def test_patch_rollback_execute_normalizes_and_validates():
    c = _ok(
        {
            "status": "ROLLBACK_EXECUTED_OK",
            "session_id": "g7-rb",
            "sealed_rollback_evidence_id": "sre-patch",
            "sealed_apply_receipt_id": "sar-patch",
            "target_path": "a.txt",
            "restored_sha256": "c" * 64,
            "human_authorization_consumed": True,
            "decision_authority": "KX108_ONLY",
            "rollback_authority": "SEALED_EVIDENCE_BOUND_RECOVERY",
            "kx108_invocations_during_rollback": 0,
            "executor_provider": "JARJAR",
            "executor_backend": "NativeFilesystemBackend",
        },
        operation_type="V2_APPLY_PATCH",
    )
    assert c["phase"] == PHASE_ROLLBACK_EXECUTE
    assert c["restored_sha256"] == "c" * 64


def test_contract_rejects_parallel_decision_authority():
    try:
        canonical_governed_result(
            {
                "status": "EXECUTED_OK",
                "j5_phase": "EXECUTE",
                "operation_type": "V2_MOVE_FILE",
                "decision_authority": "SOMETHING_ELSE",
            }
        )
    except ValueError as exc:
        assert str(exc) == "DECISION_AUTHORITY_NOT_KX108_ONLY"
    else:
        raise AssertionError("parallel authority must fail closed")


def test_contract_rejects_rollback_kx108_reinvocation():
    c = canonical_governed_result(
        {
            "status": "ROLLBACK_EXECUTED_OK",
            "decision_authority": "KX108_ONLY",
            "human_authorization_consumed": True,
            "kx108_invocations_during_rollback": 1,
        },
        operation_type="V2_APPLY_PATCH",
        phase=PHASE_ROLLBACK_EXECUTE,
    )
    ok, reason = validate_governed_contract(c)
    assert ok is False
    assert reason == "ROLLBACK_KX108_REINVOCATION_FORBIDDEN"


def test_self_check_is_adapter_only():
    s = self_check_contract_v0()
    assert s["adapter_only"] is True
    assert s["mutates_filesystem"] is False
    assert s["makes_authorization_decisions"] is False
    assert s["decision_authority"] == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Integration: canonicalize real governed runtime outputs, not synthetic dicts
# ---------------------------------------------------------------------------

import hashlib
import subprocess
from unittest.mock import MagicMock

import obsidia_pc_capabilities_v2 as PC2
from jarjar_governed_patch_rollback_bridge_v0 import (
    governed_rollback_patch_execute,
    governed_rollback_patch_prepare,
)


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def test_g7_integration_real_create_move_patch_and_patch_rollback(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    (main / "a.txt").write_bytes(b"a\n")
    (main / "p.txt").write_bytes(b"before\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "g7@test.local")
    _git(main, "config", "user.name", "G7")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec"
    _git(main, "worktree", "add", str(exec_wt), "-b", "g7-int", base_sha)
    stores = tmp_path / "stores"

    common = dict(
        execution_worktree_path=exec_wt,
        main_worktree_path=main,
        branch_name="g7-int",
        base_sha=base_sha,
        stores_base_dir=stores,
    )

    # CREATE_FILE real output
    cp = PC2.pc_v2_create_file_prepare("new.txt", b"new\n", **common, session_id="g7-create")
    cpc = canonical_governed_result(cp)
    assert validate_governed_contract(cpc) == (True, None)

    ce = PC2.pc_v2_create_file_execute(
        cp,
        cp["execution_authority_hash"],
        "HUMAN_G7_CREATE",
        stores_base_dir=stores,
        repo_root=exec_wt,
        session_id="g7-create",
    )
    cec = canonical_governed_result(ce)
    assert validate_governed_contract(cec) == (True, None)
    assert cec["sealed_rollback_evidence_ids"]
    assert cec["sealed_apply_receipt_ids"]

    # Reset to a clean committed worktree so the next governed PREPARE can pass isolation.
    _git(exec_wt, "add", ".")
    _git(exec_wt, "commit", "-q", "-m", "g7 create")
    base_sha2 = _git(exec_wt, "rev-parse", "HEAD")

    # MOVE_FILE real output
    move_common = dict(common)
    move_common["base_sha"] = base_sha2
    mp = PC2.pc_v2_move_file_prepare(
        "a.txt", "moved.txt", **move_common, session_id="g7-move"
    )
    mpc = canonical_governed_result(mp)
    assert validate_governed_contract(mpc) == (True, None)

    me = PC2.pc_v2_move_file_execute(
        mp,
        mp["execution_authority_hash"],
        "HUMAN_G7_MOVE",
        stores_base_dir=stores,
        repo_root=exec_wt,
        session_id="g7-move",
    )
    mec = canonical_governed_result(me)
    assert validate_governed_contract(mec) == (True, None)

    _git(exec_wt, "add", ".")
    _git(exec_wt, "commit", "-q", "-m", "g7 move")
    base_sha3 = _git(exec_wt, "rev-parse", "HEAD")

    # APPLY_PATCH real governed output using the same executor contract as G5 tests.
    patch = (
        "--- a/p.txt\n"
        "+++ b/p.txt\n"
        "@@ -1 +1 @@\n"
        "-before\n"
        "+after\n"
    )
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _apply(repo_root, patch_content, target_paths):
        assert target_paths == ["p.txt"]
        (Path(repo_root) / "p.txt").write_bytes(b"after\n")
        return {"ok": True, "error": None}

    ex.apply_patch.side_effect = _apply
    patch_common = dict(common)
    patch_common["base_sha"] = base_sha3
    pp = PC2.pc_v2_apply_patch_prepare(
        patch, **patch_common, session_id="g7-patch"
    )
    ppc = canonical_governed_result(pp)
    assert validate_governed_contract(ppc) == (True, None)

    pe = PC2.pc_v2_apply_patch_execute(
        pp,
        pp["execution_authority_hash"],
        "HUMAN_G7_PATCH",
        stores_base_dir=stores,
        repo_root=exec_wt,
        session_id="g7-patch",
        executor=ex,
    )
    pec = canonical_governed_result(pe)
    assert validate_governed_contract(pec) == (True, None)
    assert pec["sealed_rollback_evidence_ids"]
    assert pec["sealed_apply_receipt_ids"]

    # Governed PATCH rollback real output.
    rbp = governed_rollback_patch_prepare(
        pe["sealed_rollback_evidence_ids"][0],
        pe["sealed_apply_receipt_id"],
        sre_dir=stores / "sre",
        sar_dir=stores / "sar",
        v2exec_dir=stores / "v2exec",
        repo_root=exec_wt,
        session_id="g7-rb",
    )
    rbpc = canonical_governed_result(rbp, operation_type="V2_APPLY_PATCH")
    assert validate_governed_contract(rbpc) == (True, None)
    assert rbpc["phase"] == PHASE_ROLLBACK_PREPARE

    rex = MagicMock()
    rex.EXECUTOR_PROVIDER = "JARJAR"
    rex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _restore(target, restore_content, expected_current_sha256):
        current = target.read_bytes()
        if hashlib.sha256(current).hexdigest() != expected_current_sha256:
            return {"ok": False, "error": "rollback target drifted"}
        target.write_bytes(restore_content)
        return {
            "ok": True,
            "error": None,
            "executor": "NativeFilesystemBackend",
            "data": {"restored_sha256": hashlib.sha256(restore_content).hexdigest()},
        }

    rex.restore_file_bytes_guarded.side_effect = _restore
    rbe = governed_rollback_patch_execute(
        rbp,
        rbp["rollback_authority_hash"],
        "HUMAN_G7_ROLLBACK",
        sre_dir=stores / "sre",
        sar_dir=stores / "sar",
        v2exec_dir=stores / "v2exec",
        executor=rex,
        repo_root=exec_wt,
        session_id="g7-rb",
    )
    rbec = canonical_governed_result(rbe, operation_type="V2_APPLY_PATCH")
    assert validate_governed_contract(rbec) == (True, None)
    assert rbec["phase"] == PHASE_ROLLBACK_EXECUTE
    assert rbec["human_authorization_consumed"] is True
    assert rbec["kx108_invocations_during_rollback"] == 0
