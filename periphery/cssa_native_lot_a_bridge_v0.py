"""CSSA Lot A → actual native CRM/TASK/FOLLOW-UP via existing KX108 gate.

Only synthetic fixtures; writes ONLY to explicitly isolated local sandbox dirs.
Caller must opt in to an explicitly simulated HUMAN:SANDBOX_OPERATOR approval.
No real CSSA operator approval, external connector, or live delivery implied.
"""
from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import json

from periphery.cssa_season_campaign_lot_a_v0 import (
    run_cssa_season_campaign, verify_cssa_season_campaign,
)
from periphery.native_ops.common_v0 import NativeEntityStoreV0
from periphery.native_ops.intake_bundle_v0 import (
    build_native_case_task_intake_plan_v0,
    execute_native_case_task_intake_v0,
)
from periphery.native_ops.native_work_to_action_projection_v0 import (
    project_native_work_to_action_v0, verify_native_work_action_projection_v0,
)


def _digest(x):
    return sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def run_cssa_native_lot_a(events: list[dict], *, root: Path,
                          simulate_operator_approval: bool = False) -> dict:
    root = Path(root)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError("CSSA_LOT_A_SANDBOX_ROOT_NOT_EMPTY")
    campaign = run_cssa_season_campaign(events)
    if not verify_cssa_season_campaign(campaign):
        raise ValueError("CSSA_LOT_A_CAMPAIGN_INVALID")
    if not simulate_operator_approval:
        return {"status": "HOLD", "reason": "NO_SANDBOX_OPERATOR_APPROVAL",
                "cases": [], "decision_authority": "KX108_ONLY",
                "external_actions": [], "native_writes": False}
    if len(events) != 1 or len(campaign["report"]["cases"]) != 1:
        raise ValueError("CSSA_LOT_A_NATIVE_SINGLE_CASE_ONLY")
    inspected = campaign["report"]["cases"][0]
    event = events[0]
    if inspected["status"] != "HOLD":
        return {"status": "BLOCK", "reason": "CSSA_DOMAIN_CONFLICT",
                "issues": inspected["issues"], "cases": [],
                "decision_authority": "KX108_ONLY",
                "external_actions": [], "native_writes": False}
    if (event["kind"] != "DEADLINE"
            or event.get("regulatory_basis_proven") is not True
            or not isinstance(event.get("due_at"), str)
            or not event["due_at"].endswith("+00:00")):
        return {"status": "HOLD", "reason": "CSSA_DEADLINE_CANONICALIZATION_UNPROVEN",
                "cases": [], "decision_authority": "KX108_ONLY",
                "external_actions": [], "native_writes": False}
    root.mkdir(parents=True, exist_ok=True)
    seed = _digest(event)[:24]
    plan = build_native_case_task_intake_plan_v0(
        intake_id="cssa-lot-a-" + seed,
        case_id="cssa-case-" + seed,
        task_id="cssa-task-" + seed,
        interaction_id="cssa-interaction-" + seed,
        followup_id="cssa-followup-" + seed,
        case_type="ACTION_WITH_DEADLINE",
        title="CSSA synthetic dossier deadline",
        summary="Synthetic CSSA deadline review; not a real club instruction",
        owner_ref=None,
        priority="NORMAL",
        occurred_at="2026-10-09T00:00:00+00:00",
        due_at=event["due_at"],
        source_refs=(event["source_ref"],),
        evidence_refs=("cssa:synthetic:" + inspected["source_hash"],),
        tags=("CSSA", "SYNTHETIC", "LOT_A"),
    )
    store = NativeEntityStoreV0(root / "native")
    outcome = execute_native_case_task_intake_v0(
        plan=plan, store=store, governance_root=root / "governance",
        approved_by="HUMAN:SANDBOX_OPERATOR",
        approval_reference="CSSA_SYNTHETIC_SANDBOX_ONLY",
    )
    if outcome["status"] != "NATIVE_INTAKE_COMMITTED":
        return {"status": "HOLD", "reason": "NATIVE_GATE_NOT_COMMITTED",
                "native_result": outcome, "cases": [],
                "decision_authority": "KX108_ONLY",
                "external_actions": [], "native_writes": False}
    projection = project_native_work_to_action_v0(
        store=store, case_id=outcome["case_id"],
        task_id=outcome["task_id"], followup_id=outcome["followup_id"],
    )
    if verify_native_work_action_projection_v0(projection) != (True, None):
        raise ValueError("CSSA_NATIVE_PROJECTION_VERIFICATION_FAILED")
    return {
        "status": "SANDBOX_NATIVE_WORK_COMMITTED_ACTION_NOT_EXECUTED",
        "native_result": outcome,
        "cases": [{"case_id": outcome["case_id"],
                   "task_id": outcome["task_id"],
                   "followup_id": outcome["followup_id"],
                   "projection_status": projection.status,
                   "projection_hash": projection.projection_hash,
                   "action_candidate": projection.action_candidate is not None}],
        "decision_authority": "KX108_ONLY",
        "external_actions": [],
        "native_writes": True,
        "native_writes_scope": "ISOLATED_TEST_ROOT_ONLY",
        "real_external_effect": False,
    }
