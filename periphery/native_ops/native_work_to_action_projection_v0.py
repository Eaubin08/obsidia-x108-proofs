"""NATIVE_WORK_TO_ACTION_PROJECTION_V0.

Deterministic, non-sovereign projection from canonical native CRM/TASK work
state to the existing periphery.common.ActionCandidate contract.

This layer can also bind an ActionCandidate into the already-canonical
UNIVERSAL_WORLD_ACTION_REQUEST_V0 shape when an explicit infrastructure target
binding is supplied. It never approves, decides, executes, or emits ACT.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional

from periphery.common import ActionCandidate
from periphery.validators import validate_action_candidate

from .common_v0 import DECISION_AUTHORITY, NativeEntityStoreV0, canonical_hash
from .crm_native_v0 import DOMAIN_ID as CRM_DOMAIN, KIND_FOLLOWUP, KIND_RECORD
from .tasks_native_v0 import (
    DOMAIN_ID as TASK_DOMAIN,
    ENTITY_KIND as TASK_KIND,
    TERMINAL_STATUSES,
)

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_world_action_pre_execution_context_v0 as CTX  # noqa: E402

STATUS_ACTION_CANDIDATE = "ACTION_CANDIDATE"
STATUS_NO_ACTION = "NO_ACTION"

REASON_CALENDAR_DEADLINE_PROJECTION = "CALENDAR_DEADLINE_PROJECTION"
REASON_EXTERNAL_SURFACE_NOT_PROVEN = "EXTERNAL_ACTION_SURFACE_NOT_PROVEN"
REASON_TASK_TERMINAL = "TASK_TERMINAL"
REASON_WORK_NOT_ACTIONABLE = "WORK_NOT_ACTIONABLE"

ACTION_TYPE_CALENDAR_CREATE_EVENT = "CALENDAR_CREATE_EVENT"

CALENDAR_CASE_TYPES = {
    "ACTION_WITH_DEADLINE",
    "CONTRACT_DEADLINE",
}


@dataclass(frozen=True)
class NativeWorkActionProjectionV0:
    schema: str
    projection_id: str
    case_id: str
    task_id: str
    followup_id: str
    case_state_hash: str
    task_state_hash: str
    followup_state_hash: str
    status: str
    reason_code: str
    action_candidate: ActionCandidate | None
    evidence_refs: tuple[str, ...]
    projection_hash: str
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "projection_id": self.projection_id,
            "case_id": self.case_id,
            "task_id": self.task_id,
            "followup_id": self.followup_id,
            "case_state_hash": self.case_state_hash,
            "task_state_hash": self.task_state_hash,
            "followup_state_hash": self.followup_state_hash,
            "status": self.status,
            "reason_code": self.reason_code,
            "action_candidate": (
                asdict(self.action_candidate)
                if self.action_candidate is not None
                else None
            ),
            "evidence_refs": list(self.evidence_refs),
            "projection_hash": self.projection_hash,
            "allowed_to_decide": self.allowed_to_decide,
            "allowed_to_act": self.allowed_to_act,
            "emits_act": self.emits_act,
            "decision_authority": self.decision_authority,
        }


def _projection_payload(
    *,
    case_id: str,
    task_id: str,
    followup_id: str,
    case_state_hash: str,
    task_state_hash: str,
    followup_state_hash: str,
    status: str,
    reason_code: str,
    action_candidate: ActionCandidate | None,
    evidence_refs: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "schema": "OBSIDIA_NATIVE_WORK_ACTION_PROJECTION_V0",
        "case_id": case_id,
        "task_id": task_id,
        "followup_id": followup_id,
        "case_state_hash": case_state_hash,
        "task_state_hash": task_state_hash,
        "followup_state_hash": followup_state_hash,
        "status": status,
        "reason_code": reason_code,
        "action_candidate": (
            asdict(action_candidate)
            if action_candidate is not None
            else None
        ),
        "evidence_refs": list(evidence_refs),
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "decision_authority": DECISION_AUTHORITY,
    }


def _load_bound_work(
    *,
    store: NativeEntityStoreV0,
    case_id: str,
    task_id: str,
    followup_id: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    case = store.load_state(CRM_DOMAIN, KIND_RECORD, case_id)
    task = store.load_state(TASK_DOMAIN, TASK_KIND, task_id)
    followup = store.load_state(CRM_DOMAIN, KIND_FOLLOWUP, followup_id)
    if case is None:
        raise ValueError("WORK_ACTION_CASE_NOT_FOUND")
    if task is None:
        raise ValueError("WORK_ACTION_TASK_NOT_FOUND")
    if followup is None:
        raise ValueError("WORK_ACTION_FOLLOWUP_NOT_FOUND")
    if case.get("record_type") != "CASE":
        raise ValueError("WORK_ACTION_RECORD_NOT_CASE")
    if followup.get("record_id") != case_id:
        raise ValueError("WORK_ACTION_FOLLOWUP_CASE_BINDING_MISMATCH")
    if followup.get("task_ref") != task_id:
        raise ValueError("WORK_ACTION_FOLLOWUP_TASK_BINDING_MISMATCH")
    if followup.get("due_at") != task.get("due_at"):
        raise ValueError("WORK_ACTION_DUE_BINDING_MISMATCH")
    return case, task, followup


def _build_projection(
    *,
    case_id: str,
    task_id: str,
    followup_id: str,
    case_state_hash: str,
    task_state_hash: str,
    followup_state_hash: str,
    status: str,
    reason_code: str,
    action_candidate: ActionCandidate | None,
) -> NativeWorkActionProjectionV0:
    evidence_refs = tuple(sorted({
        f"native-case-state:{case_state_hash}",
        f"native-task-state:{task_state_hash}",
        f"native-followup-state:{followup_state_hash}",
    }))
    payload = _projection_payload(
        case_id=case_id,
        task_id=task_id,
        followup_id=followup_id,
        case_state_hash=case_state_hash,
        task_state_hash=task_state_hash,
        followup_state_hash=followup_state_hash,
        status=status,
        reason_code=reason_code,
        action_candidate=action_candidate,
        evidence_refs=evidence_refs,
    )
    projection_hash = canonical_hash(payload)
    return NativeWorkActionProjectionV0(
        schema=payload["schema"],
        projection_id=f"work-action-{projection_hash[:32]}",
        case_id=case_id,
        task_id=task_id,
        followup_id=followup_id,
        case_state_hash=case_state_hash,
        task_state_hash=task_state_hash,
        followup_state_hash=followup_state_hash,
        status=status,
        reason_code=reason_code,
        action_candidate=action_candidate,
        evidence_refs=evidence_refs,
        projection_hash=projection_hash,
    )


def project_native_work_to_action_v0(
    *,
    store: NativeEntityStoreV0,
    case_id: str,
    task_id: str,
    followup_id: str,
) -> NativeWorkActionProjectionV0:
    case, task, followup = _load_bound_work(
        store=store,
        case_id=case_id,
        task_id=task_id,
        followup_id=followup_id,
    )
    case_hash = canonical_hash(case)
    task_hash = canonical_hash(task)
    followup_hash = canonical_hash(followup)

    if task.get("status") in TERMINAL_STATUSES or followup.get("status") != "OPEN":
        return _build_projection(
            case_id=case_id,
            task_id=task_id,
            followup_id=followup_id,
            case_state_hash=case_hash,
            task_state_hash=task_hash,
            followup_state_hash=followup_hash,
            status=STATUS_NO_ACTION,
            reason_code=REASON_TASK_TERMINAL,
            action_candidate=None,
        )

    case_type = str(case.get("fields", {}).get("case_type") or "")
    if case_type not in CALENDAR_CASE_TYPES:
        reason = (
            REASON_EXTERNAL_SURFACE_NOT_PROVEN
            if case_type == "INCIDENT"
            else REASON_WORK_NOT_ACTIONABLE
        )
        return _build_projection(
            case_id=case_id,
            task_id=task_id,
            followup_id=followup_id,
            case_state_hash=case_hash,
            task_state_hash=task_hash,
            followup_state_hash=followup_hash,
            status=STATUS_NO_ACTION,
            reason_code=reason,
            action_candidate=None,
        )

    due_at = task.get("due_at")
    if not due_at:
        return _build_projection(
            case_id=case_id,
            task_id=task_id,
            followup_id=followup_id,
            case_state_hash=case_hash,
            task_state_hash=task_hash,
            followup_state_hash=followup_hash,
            status=STATUS_NO_ACTION,
            reason_code=REASON_WORK_NOT_ACTIONABLE,
            action_candidate=None,
        )

    action_seed = {
        "schema": "NATIVE_WORK_ACTION_CANDIDATE_SEED_V0",
        "case_id": case_id,
        "task_id": task_id,
        "followup_id": followup_id,
        "case_state_hash": case_hash,
        "task_state_hash": task_hash,
        "followup_state_hash": followup_hash,
        "action_type": ACTION_TYPE_CALENDAR_CREATE_EVENT,
    }
    action_id = f"native-work-action:{canonical_hash(action_seed)[:32]}"
    candidate = ActionCandidate(
        action_id=action_id,
        domain="native_operations",
        actor_id="OBSIDIA_NATIVE_WORK_PROJECTION_V0",
        intent="SCHEDULE_WORK_DEADLINE_CONTEXT",
        action_type=ACTION_TYPE_CALENDAR_CREATE_EVENT,
        irreversible=False,
        timestamp_plan=str(task["created_at"]),
        timestamp_exec=None,
        payload={
            "surface_id": "CALENDAR",
            "operation_id": "CREATE_EVENT",
            "case_id": case_id,
            "task_id": task_id,
            "followup_id": followup_id,
            "title": str(task["title"]),
            "due_at": str(due_at),
            "assignee_ref": task.get("assignee_ref"),
            "source_case_type": case_type,
            "case_state_hash": case_hash,
            "task_state_hash": task_hash,
            "followup_state_hash": followup_hash,
        },
    )
    validate_action_candidate(candidate)
    return _build_projection(
        case_id=case_id,
        task_id=task_id,
        followup_id=followup_id,
        case_state_hash=case_hash,
        task_state_hash=task_hash,
        followup_state_hash=followup_hash,
        status=STATUS_ACTION_CANDIDATE,
        reason_code=REASON_CALENDAR_DEADLINE_PROJECTION,
        action_candidate=candidate,
    )


def verify_native_work_action_projection_v0(
    projection: NativeWorkActionProjectionV0,
) -> tuple[bool, Optional[str]]:
    if projection.schema != "OBSIDIA_NATIVE_WORK_ACTION_PROJECTION_V0":
        return False, "WORK_ACTION_PROJECTION_SCHEMA_INVALID"
    if projection.allowed_to_decide or projection.allowed_to_act or projection.emits_act:
        return False, "WORK_ACTION_PROJECTION_AUTHORITY_FORBIDDEN"
    if projection.decision_authority != DECISION_AUTHORITY:
        return False, "WORK_ACTION_PROJECTION_DECISION_AUTHORITY_INVALID"
    if projection.status == STATUS_ACTION_CANDIDATE:
        if projection.action_candidate is None:
            return False, "WORK_ACTION_PROJECTION_CANDIDATE_MISSING"
        try:
            validate_action_candidate(projection.action_candidate)
        except ValueError as exc:
            return False, str(exc)
    elif projection.status == STATUS_NO_ACTION:
        if projection.action_candidate is not None:
            return False, "WORK_ACTION_PROJECTION_NO_ACTION_HAS_CANDIDATE"
    else:
        return False, "WORK_ACTION_PROJECTION_STATUS_INVALID"

    payload = _projection_payload(
        case_id=projection.case_id,
        task_id=projection.task_id,
        followup_id=projection.followup_id,
        case_state_hash=projection.case_state_hash,
        task_state_hash=projection.task_state_hash,
        followup_state_hash=projection.followup_state_hash,
        status=projection.status,
        reason_code=projection.reason_code,
        action_candidate=projection.action_candidate,
        evidence_refs=projection.evidence_refs,
    )
    expected_hash = canonical_hash(payload)
    if projection.projection_hash != expected_hash:
        return False, "WORK_ACTION_PROJECTION_HASH_MISMATCH"
    if projection.projection_id != f"work-action-{expected_hash[:32]}":
        return False, "WORK_ACTION_PROJECTION_ID_MISMATCH"
    return True, None


def build_world_action_request_from_action_candidate_v0(
    candidate: ActionCandidate,
    *,
    connector_id: str,
    connector_action: str,
    connector_args: Mapping[str, Any],
    target_ref: str,
    target_prestate_hash: str,
    required_scope: str,
    effect_class: str,
    world_call_class: str,
    action_risk_class: str = "ACTION_PLAN",
    autonomy_level: int = 3,
) -> dict[str, Any]:
    """Bind an existing ActionCandidate to canonical WORLD_ACTION request shape.

    All provider/target-specific authority remains explicit caller input. This
    adapter does not infer credentials, provider identity, target state, or
    execution permission.
    """
    validate_action_candidate(candidate)
    if not all((
        connector_id,
        connector_action,
        target_ref,
        target_prestate_hash,
        required_scope,
        effect_class,
        world_call_class,
    )):
        raise ValueError("WORK_ACTION_TARGET_BINDING_REQUIRED")
    if len(target_prestate_hash) != 64:
        raise ValueError("WORK_ACTION_TARGET_PRESTATE_HASH_INVALID")

    candidate_payload = asdict(candidate)
    proposal_hash = canonical_hash({
        "schema": "NATIVE_WORK_ACTION_PROPOSAL_V0",
        "action_candidate": candidate_payload,
    })
    connector_args_dict = dict(connector_args)
    connector_call_hash = canonical_hash({
        "connector_id": connector_id,
        "connector_action": connector_action,
        "connector_args": connector_args_dict,
    })
    idempotency_key = canonical_hash({
        "schema": "UNIVERSAL_WORLD_ACTION_IDEMPOTENCY_V0",
        "proposal_hash": proposal_hash,
        "connector_call_hash": connector_call_hash,
        "target_prestate_hash": target_prestate_hash,
        "required_scope": required_scope,
    })
    request = {
        "request_id": f"world:{candidate.action_id}",
        "proposal_id": f"proposal:{candidate.action_id}",
        "proposal_hash": proposal_hash,
        "domain_id": candidate.domain,
        "surface_id": str(candidate.payload.get("surface_id") or ""),
        "operation_id": str(candidate.payload.get("operation_id") or ""),
        "effect_class": effect_class,
        "connector_id": connector_id,
        "connector_action": connector_action,
        "connector_args": connector_args_dict,
        "connector_call_hash": connector_call_hash,
        "target_ref": target_ref,
        "target_prestate_hash": target_prestate_hash,
        "required_scope": required_scope,
        "world_call_class": world_call_class,
        "action_risk_class": action_risk_class,
        "autonomy_level": autonomy_level,
        "irreversible": bool(candidate.irreversible),
        "retry_policy": "NEVER_AUTORETRY_ON_UNKNOWN",
        "idempotency_key": idempotency_key,
        "decision_authority": DECISION_AUTHORITY,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
    }
    request["request_hash"] = canonical_hash({
        "schema": "UNIVERSAL_WORLD_ACTION_REQUEST_V0",
        "request_id": request["request_id"],
        "proposal_id": request["proposal_id"],
        "proposal_hash": request["proposal_hash"],
        "domain_id": request["domain_id"],
        "surface_id": request["surface_id"],
        "operation_id": request["operation_id"],
        "effect_class": request["effect_class"],
        "connector_id": request["connector_id"],
        "connector_action": request["connector_action"],
        "connector_args": request["connector_args"],
        "connector_call_hash": request["connector_call_hash"],
        "target_ref": request["target_ref"],
        "target_prestate_hash": request["target_prestate_hash"],
        "required_scope": request["required_scope"],
        "world_call_class": request["world_call_class"],
        "action_risk_class": request["action_risk_class"],
        "autonomy_level": request["autonomy_level"],
        "irreversible": request["irreversible"],
        "retry_policy": request["retry_policy"],
        "idempotency_key": request["idempotency_key"],
        "decision_authority": request["decision_authority"],
    })
    ok, reason = CTX.verify_world_action_request_mapping(request)
    if not ok:
        raise ValueError(f"WORK_ACTION_WORLD_ACTION_REQUEST_INVALID:{reason}")
    return request
