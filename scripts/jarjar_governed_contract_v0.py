from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "G7_V0"
DECISION_AUTHORITY = "KX108_ONLY"
JARVIS_AUTHORITY = "NONE"

PHASE_PREPARE = "PREPARE"
PHASE_EXECUTE = "EXECUTE"
PHASE_ROLLBACK_PREPARE = "ROLLBACK_PREPARE"
PHASE_ROLLBACK_EXECUTE = "ROLLBACK_EXECUTE"

_PREPARED = "PREPARED_AWAITING_HUMAN_APPROVAL"
_EXECUTED = "EXECUTED_OK"
_RB_EXECUTED = "ROLLBACK_EXECUTED_OK"
_PREPARE_REJECTED = "PREPARE_REJECTED"
_EXECUTE_REJECTED = "EXECUTE_REJECTED"


def _evidence_ids(result: dict[str, Any]) -> dict[str, Any]:
    sre_ids = result.get("sealed_rollback_evidence_ids")
    if sre_ids is None:
        one = result.get("sealed_rollback_evidence_id")
        sre_ids = [one] if one else []
    sar_ids = []
    sar = result.get("sealed_apply_receipt_id")
    if sar:
        sar_ids.append(sar)
    return {
        "sealed_rollback_evidence_ids": list(sre_ids or []),
        "sealed_apply_receipt_ids": sar_ids,
    }


def _infer_phase(result: dict[str, Any], explicit_phase: str | None) -> str:
    if explicit_phase:
        return explicit_phase
    j5 = str(result.get("j5_phase", "")).upper()
    if j5 in (PHASE_PREPARE, PHASE_EXECUTE):
        return j5
    status = str(result.get("status", ""))
    if status == _RB_EXECUTED:
        return PHASE_ROLLBACK_EXECUTE
    if status == _PREPARED and result.get("rollback_authority"):
        return PHASE_ROLLBACK_PREPARE
    return "UNKNOWN"


def _infer_human_approval_required(phase: str) -> bool:
    return phase in {
        PHASE_PREPARE,
        PHASE_EXECUTE,
        PHASE_ROLLBACK_PREPARE,
        PHASE_ROLLBACK_EXECUTE,
    }


def canonical_governed_result(
    result: dict[str, Any],
    *,
    operation_type: str | None = None,
    phase: str | None = None,
) -> dict[str, Any]:
    """Return a read-only canonical view over an existing governed result.

    This adapter does not authorize, decide, mutate, execute, or persist anything.
    It exists only to unify result shape for higher layers.
    """
    p = _infer_phase(result, phase)
    op = operation_type or result.get("operation_type") or "UNKNOWN"

    decision_authority = result.get("decision_authority", DECISION_AUTHORITY)
    if decision_authority != DECISION_AUTHORITY:
        raise ValueError("DECISION_AUTHORITY_NOT_KX108_ONLY")

    jarvis_authority = result.get("jarvis_authority", JARVIS_AUTHORITY)
    if jarvis_authority not in (None, "", JARVIS_AUTHORITY):
        raise ValueError("JARVIS_AUTHORITY_MUST_BE_NONE")

    evidence = _evidence_ids(result)

    contract = {
        "contract_version": CONTRACT_VERSION,
        "operation_type": op,
        "phase": p,
        "status": result.get("status"),
        "reason": result.get("reason"),
        "session_id": result.get("session_id")
        or (result.get("receipt") or {}).get("session_id", ""),
        "decision_authority": DECISION_AUTHORITY,
        "jarvis_authority": JARVIS_AUTHORITY,
        "human_approval_required": _infer_human_approval_required(p),
        "human_authorization_consumed": bool(
            result.get("human_authorization_consumed", False)
        ),
        "execution_authority_hash": result.get("execution_authority_hash"),
        "rollback_authority_hash": result.get("rollback_authority_hash"),
        "rollback_authority": result.get("rollback_authority"),
        "kx108_pre_gate": result.get("kx108_pre_gate"),
        "kx108_invocations_during_rollback": result.get(
            "kx108_invocations_during_rollback"
        ),
        "executor_provider": result.get("executor_provider"),
        "executor_backend": result.get("executor_backend"),
        "target_path": result.get("target_path"),
        "target_paths": list(result.get("target_paths") or []),
        "source_path": result.get("source_path"),
        "dest_path": result.get("dest_path"),
        "restored_sha256": result.get("restored_sha256"),
        **evidence,
    }
    return contract


def validate_governed_contract(contract: dict[str, Any]) -> tuple[bool, str | None]:
    if contract.get("contract_version") != CONTRACT_VERSION:
        return False, "CONTRACT_VERSION_MISMATCH"
    if contract.get("decision_authority") != DECISION_AUTHORITY:
        return False, "DECISION_AUTHORITY_NOT_KX108_ONLY"
    if contract.get("jarvis_authority") != JARVIS_AUTHORITY:
        return False, "JARVIS_AUTHORITY_MUST_BE_NONE"
    if contract.get("phase") not in {
        PHASE_PREPARE,
        PHASE_EXECUTE,
        PHASE_ROLLBACK_PREPARE,
        PHASE_ROLLBACK_EXECUTE,
    }:
        return False, "PHASE_INVALID"
    if not contract.get("operation_type") or contract.get("operation_type") == "UNKNOWN":
        return False, "OPERATION_TYPE_REQUIRED"
    if contract.get("status") is None:
        return False, "STATUS_REQUIRED"

    phase = contract["phase"]
    status = contract["status"]

    if phase in {PHASE_PREPARE, PHASE_ROLLBACK_PREPARE}:
        if status not in {_PREPARED, _PREPARE_REJECTED}:
            return False, "PREPARE_STATUS_INVALID"

    if phase == PHASE_EXECUTE:
        if status not in {_EXECUTED, _EXECUTE_REJECTED}:
            return False, "EXECUTE_STATUS_INVALID"

    if phase == PHASE_ROLLBACK_EXECUTE:
        if status not in {_RB_EXECUTED, _EXECUTE_REJECTED}:
            return False, "ROLLBACK_EXECUTE_STATUS_INVALID"

    if phase == PHASE_ROLLBACK_EXECUTE and status == _RB_EXECUTED:
        if contract.get("kx108_invocations_during_rollback") != 0:
            return False, "ROLLBACK_KX108_REINVOCATION_FORBIDDEN"
        if contract.get("human_authorization_consumed") is not True:
            return False, "ROLLBACK_HUMAN_AUTHORIZATION_REQUIRED"

    return True, None


def self_check_contract_v0() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "decision_authority": DECISION_AUTHORITY,
        "jarvis_authority": JARVIS_AUTHORITY,
        "phases": [
            PHASE_PREPARE,
            PHASE_EXECUTE,
            PHASE_ROLLBACK_PREPARE,
            PHASE_ROLLBACK_EXECUTE,
        ],
        "adapter_only": True,
        "mutates_filesystem": False,
        "makes_authorization_decisions": False,
        "is_execution_authority": False,
        "is_kx_authority": False,
    }
