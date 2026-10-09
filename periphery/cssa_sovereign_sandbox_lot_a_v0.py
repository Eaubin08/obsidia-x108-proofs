"""CSSA LOT A: actual CSSA synthetic action through Universal sandbox rail.

Uses an explicitly simulated operator approval, isolated temporary native store,
and pre-existing immutable Universal KX108 / ticket / receipt / replay path.
No real operator authorization and no external effect.
"""
from __future__ import annotations

from pathlib import Path

from periphery.cssa_native_lot_a_bridge_v0 import run_cssa_native_lot_a
from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.native_work_to_action_projection_v0 import (
    STATUS_ACTION_CANDIDATE,
    project_native_work_to_action_v0,
    verify_native_work_action_projection_v0,
)
from periphery.native_sources.enterprise_office_full_loop_e2e_v0 import (
    _execute_projection,
)


def run_cssa_sovereign_sandbox_lot_a(
    events: list[dict], *, root: Path,
    simulate_operator_approval: bool = False,
) -> dict:
    root = Path(root)
    intake = run_cssa_native_lot_a(
        events, root=root,
        simulate_operator_approval=simulate_operator_approval,
    )
    if intake["status"] != "SANDBOX_NATIVE_WORK_COMMITTED_ACTION_NOT_EXECUTED":
        return {
            "status": intake["status"], "intake": intake,
            "cssa_action_executed": False, "external_actions": [],
            "decision_authority": "KX108_ONLY",
            "real_external_effect": False,
        }
    if not simulate_operator_approval:
        raise ValueError("CSSA_LOT_A_EXPLICIT_SANDBOX_APPROVAL_REQUIRED")
    work = intake["native_result"]
    projection = project_native_work_to_action_v0(
        store=NativeEntityStoreV0(root / "native"),
        case_id=work["case_id"],
        task_id=work["task_id"],
        followup_id=work["followup_id"],
    )
    if (verify_native_work_action_projection_v0(projection) != (True, None)
            or projection.status != STATUS_ACTION_CANDIDATE):
        raise ValueError("CSSA_LOT_A_ACTION_PROJECTION_INVALID")
    result = _execute_projection(
        projection=projection,
        governance_root=root / "cssa-world-action",
        execution_root=root / "cssa-sandbox-execution",
    )
    if (result["kx108_gate"] != "ALLOW"
            or result["execution_replay_ok"] is not True
            or result["duplicate_adapter_called"] is not False
            or result["network_call_performed"] is not False
            or result["real_external_effect"] is not False):
        raise ValueError("CSSA_LOT_A_SOVEREIGN_SANDBOX_RESULT_INVALID")
    return {
        "status": "CSSA_LOT_A_SANDBOX_E2E_PROVEN",
        "cssa_action_executed": True,
        "cssa_source_case_id": work["case_id"],
        "cssa_source_task_id": work["task_id"],
        "cssa_source_followup_id": work["followup_id"],
        "cssa_projection_hash": projection.projection_hash,
        "intake_mutations": work["canonical_mutation_count"],
        "execution": result,
        "sandbox_operator_approval_simulated": True,
        "real_operator_approval": False,
        "external_actions": [],
        "network_call_performed": False,
        "real_external_effect": False,
        "decision_authority": "KX108_ONLY",
    }
