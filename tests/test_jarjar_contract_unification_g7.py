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
