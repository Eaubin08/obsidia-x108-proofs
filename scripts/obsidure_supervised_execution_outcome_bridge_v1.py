from __future__ import annotations

"""R12-F5-B supervised governed execution outcome bridge.

This adapter connects an already prepared supervised ticket to the existing
R9-B6 apply-patch execution rail and R8 evidence replay/reconciliation. It does
not create an executor, approval, authority system, repair engine, automatic
retry, or completion claim.
"""

import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_canonical_receipt_replay_v1 as _R8_REPLAY  # noqa: E402
import obsidia_realized_state_reconciliation_v1 as _R8_RECONCILE  # noqa: E402
from obsidia_pc_capabilities_v2 import (  # noqa: E402
    EXECUTED_OK,
    EXECUTE_REJECTED,
    PREPARED_AWAITING_HUMAN_APPROVAL,
    pc_v2_apply_patch_execute,
)
from obsidure_supervised_dependency_state_integration_v1 import STATUS_UPDATED as F4B_STATUS_UPDATED  # noqa: E402
from obsidure_supervised_mission_state_v1 import DECISION_AUTHORITY, canonical_json  # noqa: E402

ADAPTER_SCHEMA_VERSION = "OBSIDURE_SUPERVISED_EXECUTION_OUTCOME_BRIDGE_V1"

STATUS_EXECUTION_OUTCOME = "R12_F5_B_EXECUTION_OUTCOME_RECORDED"
STATUS_HELD = "R12_F5_B_EXECUTION_OUTCOME_HELD"
STATUS_REJECTED = "R12_F5_B_EXECUTION_OUTCOME_REJECTED"

PHASE_PREPARED = "PREPARED"
PHASE_AUTHORIZED = "AUTHORIZED"
PHASE_EXECUTION_ATTEMPTED = "EXECUTION_ATTEMPTED"
PHASE_EXECUTED_OBSERVED = "EXECUTED_OBSERVED"
PHASE_EXECUTION_FAILED = "EXECUTION_FAILED"
PHASE_OUTCOME_UNCERTAIN = "OUTCOME_UNCERTAIN"
PHASE_AWAITING_VERIFICATION = "AWAITING_INDEPENDENT_VERIFICATION"

HOLD_AWAITING_VALID_AUTHORIZATION = "HOLD_AWAITING_VALID_AUTHORIZATION"

_NO_ESCALATION_FIELDS = {
    "approval_created_by_supervisor": False,
    "authorization_inferred": False,
    "binder_mutation": False,
    "memory_write": False,
    "native_memory_write": False,
    "automatic_retry": False,
    "repair_loop_invoked": False,
    "ticket_verified": False,
    "ticket_closed": False,
    "mission_done": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
}


def _sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "execution_phase": PHASE_PREPARED,
        "execution_attempted": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "budget_consumed": 0,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_ESCALATION_FIELDS,
        **extra,
    }


def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in state.get("tickets") or ():
        if isinstance(ticket, Mapping) and ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _handoff_feedback(prepare_handoff_result: Mapping[str, Any]) -> Mapping[str, Any] | None:
    feedback = prepare_handoff_result.get("handoff_feedback")
    return feedback if isinstance(feedback, Mapping) else None


def _prepared_action(prepare_handoff_result: Mapping[str, Any]) -> Mapping[str, Any] | None:
    prepared = prepare_handoff_result.get("r9_prepare_result")
    if isinstance(prepared, Mapping):
        action = prepared.get("prepared_action")
        if isinstance(action, Mapping):
            return action
    feedback = _handoff_feedback(prepare_handoff_result)
    if isinstance(feedback, Mapping):
        action_ref = feedback.get("prepared_action_reference")
        if isinstance(action_ref, Mapping):
            return action_ref
    return None


def _r9_patch_hash(prepare_handoff_result: Mapping[str, Any]) -> str:
    feedback = _handoff_feedback(prepare_handoff_result) or {}
    ref = feedback.get("r9_candidate_reference")
    if isinstance(ref, Mapping):
        return str(ref.get("candidate_patch_hash") or "")
    return ""


def _accepted_state(mission_update: Mapping[str, Any]) -> Mapping[str, Any] | None:
    state = mission_update.get("accepted_state")
    return state if isinstance(state, Mapping) else None


def _blocking_reason(mission_update: Mapping[str, Any], ticket_id: str) -> str | None:
    for block in list(mission_update.get("transitive_dependency_blocks") or []) + list(mission_update.get("root_dependency_blocks") or []):
        if isinstance(block, Mapping) and block.get("ticket_id") == ticket_id:
            if str(block.get("reason") or "") in {"PREPARED_AWAITING_APPROVAL", f"BLOCKED_BY_HOLD({ticket_id})"}:
                continue
            return str(block.get("reason") or "TICKET_BLOCKED_BY_DEPENDENCY")
    dep = mission_update.get("dependency_projection")
    if isinstance(dep, Mapping):
        for block in list(dep.get("transitive_dependency_blocks") or []) + list(dep.get("root_dependency_blocks") or []):
            if isinstance(block, Mapping) and block.get("ticket_id") == ticket_id:
                if str(block.get("reason") or "") in {"PREPARED_AWAITING_APPROVAL", f"BLOCKED_BY_HOLD({ticket_id})"}:
                    continue
                return str(block.get("reason") or "TICKET_BLOCKED_BY_DEPENDENCY")
    return None


def _budget_reason(state: Mapping[str, Any]) -> str | None:
    budget = state.get("global_budget") if isinstance(state.get("global_budget"), Mapping) else {}
    for key in ("remaining_actions", "remaining_attempts", "remaining_tickets"):
        value = budget.get(key)
        if isinstance(value, int) and value <= 0:
            return "MISSION_BUDGET_EXHAUSTED"
    timebox = state.get("timebox") if isinstance(state.get("timebox"), Mapping) else {}
    if timebox.get("expired") is True:
        return "MISSION_TIMEBOX_EXPIRED"
    return None


def _validate_bindings(
    mission_update: Mapping[str, Any],
    prepare_handoff_result: Mapping[str, Any],
    *,
    observed_project_head: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(mission_update, Mapping) or mission_update.get("status") != F4B_STATUS_UPDATED:
        return _fail(STATUS_REJECTED, "ACCEPTED_F4B_UPDATE_REQUIRED"), {}
    if not isinstance(prepare_handoff_result, Mapping) or prepare_handoff_result.get("prepare_handoff") is not True:
        return _fail(STATUS_REJECTED, "VALID_F3B_PREPARE_HANDOFF_REQUIRED"), {}
    state = _accepted_state(mission_update)
    feedback = _handoff_feedback(prepare_handoff_result)
    action = _prepared_action(prepare_handoff_result)
    if not isinstance(state, Mapping) or not isinstance(feedback, Mapping) or not isinstance(action, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_PREPARE_BINDING_REQUIRED"), {}

    ticket_id = str(feedback.get("selected_ticket_id") or "")
    ticket = _ticket_by_id(state, ticket_id)
    if not isinstance(ticket, Mapping):
        return _fail(STATUS_REJECTED, "PREPARED_TICKET_NOT_FOUND"), {}
    if state.get("mandate_revoked") is True or str(state.get("mandate_status") or "ACTIVE").upper() == "REVOKED":
        return _fail(STATUS_HELD, "HUMAN_MANDATE_REVOKED", mission_id=state.get("mission_id"), selected_ticket_id=ticket_id), {}
    if str(state.get("mandate_status") or "ACTIVE").upper() not in {"ACTIVE", "AUTHORIZED", "MANDATE_ACTIVE", "MISSION_ACTIVE"}:
        return _fail(STATUS_HELD, "HUMAN_MANDATE_NOT_ACTIVE", mission_id=state.get("mission_id"), selected_ticket_id=ticket_id), {}
    if observed_project_head is not None and str(observed_project_head).lower() != str(state.get("base_sha") or "").lower():
        return _fail(STATUS_HELD, "PROJECT_HEAD_STALE", mission_id=state.get("mission_id"), selected_ticket_id=ticket_id), {}
    budget_reason = _budget_reason(state)
    if budget_reason:
        return _fail(STATUS_HELD, budget_reason, mission_id=state.get("mission_id"), selected_ticket_id=ticket_id), {}
    block_reason = _blocking_reason(mission_update, ticket_id)
    if block_reason:
        return _fail(STATUS_HELD, "TICKET_BLOCKED_BY_DEPENDENCY", block_reason=block_reason, selected_ticket_id=ticket_id), {}
    if ticket.get("status") != "HELD" or ticket.get("hold_reason") != "PREPARED_AWAITING_APPROVAL":
        return _fail(STATUS_HELD, "TICKET_NOT_PREPARED_AWAITING_APPROVAL", selected_ticket_id=ticket_id), {}
    if feedback.get("mission_id") != state.get("mission_id"):
        return _fail(STATUS_REJECTED, "MISSION_BINDING_MISMATCH"), {}
    if feedback.get("mandate_reference") != state.get("human_mandate_reference"):
        return _fail(STATUS_REJECTED, "MANDATE_BINDING_MISMATCH"), {}
    project = feedback.get("project") if isinstance(feedback.get("project"), Mapping) else {}
    for key in ("repository_identity", "local_root", "worktree", "branch", "base_sha"):
        state_key = "repository_identity" if key == "repository_identity" else key
        if str(project.get(key) or "") != str(state.get(state_key) or ""):
            return _fail(STATUS_REJECTED, "PROJECT_BINDING_MISMATCH:" + key.upper()), {}
    if action.get("status") != PREPARED_AWAITING_HUMAN_APPROVAL:
        return _fail(STATUS_HELD, "PREPARED_ACTION_NOT_AWAITING_HUMAN_APPROVAL", selected_ticket_id=ticket_id), {}
    if action.get("executor_invoked") is True or action.get("physical_mutation") is True:
        return _fail(STATUS_REJECTED, "PREPARED_ACTION_ALREADY_CLAIMS_EXECUTION", selected_ticket_id=ticket_id), {}
    patch_hash = _r9_patch_hash(prepare_handoff_result)
    if patch_hash and action.get("patch_sha256") and patch_hash != action.get("patch_sha256"):
        return _fail(STATUS_HELD, "PREPARED_PATCH_HASH_MISMATCH", selected_ticket_id=ticket_id), {}
    if not action.get("execution_authority_hash"):
        return _fail(STATUS_HELD, "PREPARED_ACTION_AUTHORITY_HASH_REQUIRED", selected_ticket_id=ticket_id), {}
    return None, {"state": state, "ticket": ticket, "feedback": feedback, "prepared_action": action}


def _repair_advice(executor_result: Mapping[str, Any], reconciliation: Mapping[str, Any] | None) -> dict[str, Any]:
    failed = executor_result.get("status") != EXECUTED_OK
    uncertain = bool(reconciliation and reconciliation.get("reconciliation_status") in {
        _R8_RECONCILE.STATUS_UNCERTAIN,
        _R8_RECONCILE.STATUS_INCOMPLETE,
        _R8_RECONCILE.STATUS_TAMPERED,
        _R8_RECONCILE.STATUS_MISMATCH,
    })
    return {
        "repair_feedback_mode": "R10_CLASSIFICATION_ONLY",
        "repair_eligible": bool(failed and not uncertain),
        "repair_launch_allowed": False,
        "automatic_retry": False,
        "failure_status": executor_result.get("status"),
        "failure_reason": executor_result.get("reason") or "",
        "reconciliation_status": reconciliation.get("reconciliation_status") if isinstance(reconciliation, Mapping) else "UNAVAILABLE",
    }


def _phase_from_evidence(executor_result: Mapping[str, Any], replay: Mapping[str, Any] | None, reconciliation: Mapping[str, Any] | None) -> tuple[str, str | None]:
    if not isinstance(replay, Mapping) or replay.get("replay_verdict") in {
        _R8_REPLAY.VERDICT_NOT_FOUND,
        _R8_REPLAY.VERDICT_INCOMPLETE,
        _R8_REPLAY.VERDICT_TAMPERED,
        _R8_REPLAY.VERDICT_CONFLICTING,
    }:
        return PHASE_OUTCOME_UNCERTAIN, "R8_REPLAY_NOT_VERIFIED"
    if not isinstance(reconciliation, Mapping):
        return PHASE_OUTCOME_UNCERTAIN, "R8_RECONCILIATION_MISSING"
    rec_status = reconciliation.get("reconciliation_status")
    if rec_status in {_R8_RECONCILE.STATUS_MISMATCH, _R8_RECONCILE.STATUS_TAMPERED, _R8_RECONCILE.STATUS_INCOMPLETE, _R8_RECONCILE.STATUS_UNCERTAIN}:
        return PHASE_OUTCOME_UNCERTAIN, "R8_RECONCILIATION_NOT_CONFIRMED:" + str(rec_status)
    if executor_result.get("status") == EXECUTED_OK and rec_status in {_R8_RECONCILE.STATUS_MATCH, _R8_RECONCILE.STATUS_NOOP_CONFIRMED}:
        return PHASE_EXECUTED_OBSERVED, None
    if executor_result.get("status") == EXECUTE_REJECTED:
        return PHASE_EXECUTION_FAILED, executor_result.get("reason") or "EXECUTE_REJECTED"
    return PHASE_AWAITING_VERIFICATION, None


def _attempt_id(mission_id: str, ticket_id: str, action_evidence_id: str, eah: str) -> str:
    return "exec-" + hashlib.sha256(f"{mission_id}:{ticket_id}:{action_evidence_id}:{eah}".encode("utf-8")).hexdigest()[:24]


def reconcile_supervised_execution_outcome(
    *,
    mission_update: Mapping[str, Any],
    prepare_handoff_result: Mapping[str, Any],
    action_evidence_id: str,
    stores_base_dir: str | Path,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    binding_error, bound = _validate_bindings(mission_update, prepare_handoff_result, observed_project_head=observed_project_head)
    if binding_error is not None:
        return binding_error
    if not isinstance(action_evidence_id, str) or not action_evidence_id.startswith("aev-"):
        return _fail(STATUS_HELD, "ACTION_EVIDENCE_ID_REQUIRED", selected_ticket_id=bound["ticket"].get("ticket_id"))
    replay = _R8_REPLAY.replay_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    reconciliation = _R8_RECONCILE.reconcile_action_evidence(action_evidence_id, stores_base_dir=stores_base_dir)
    synthetic = {"status": "RECOVERED_EXISTING_OUTCOME", "action_evidence_id": action_evidence_id}
    phase, reason = _phase_from_evidence(synthetic, replay, reconciliation)
    if phase == PHASE_OUTCOME_UNCERTAIN:
        return _fail(
            STATUS_HELD,
            reason or "OUTCOME_UNCERTAIN",
            execution_phase=phase,
            action_evidence_id=action_evidence_id,
            r8_replay=replay,
            realized_state_reconciliation=reconciliation,
        )
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_EXECUTION_OUTCOME,
        "reason": None,
        "execution_phase": phase,
        "execution_attempted": True,
        "executor_invoked": False,
        "physical_mutation": bool(reconciliation.get("mutation_performed")),
        "execution_attempt_id": _attempt_id(str(bound["state"].get("mission_id")), str(bound["ticket"].get("ticket_id")), action_evidence_id, str(bound["prepared_action"].get("execution_authority_hash"))),
        "mission_id": bound["state"].get("mission_id"),
        "selected_ticket_id": bound["ticket"].get("ticket_id"),
        "mandate_reference": bound["state"].get("human_mandate_reference"),
        "action_evidence_id": action_evidence_id,
        "r8_replay": replay,
        "realized_state_reconciliation": reconciliation,
        "pending_verification_status": PHASE_AWAITING_VERIFICATION,
        "budget_consumed": 0,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_ESCALATION_FIELDS,
    }


def execute_supervised_governed_ticket(
    *,
    mission_update: Mapping[str, Any],
    prepare_handoff_result: Mapping[str, Any],
    human_authorized_execution_authority_hash: str | None = None,
    human_authorization_reference: str | None = None,
    stores_base_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    observed_project_head: str | None = None,
    prior_execution_outcome: Mapping[str, Any] | None = None,
    session_id: str = "r12-f5b",
    executor: Callable[..., Mapping[str, Any]] = pc_v2_apply_patch_execute,
) -> dict[str, Any]:
    """Attempt exactly one authorized governed execution, then replay R8 evidence."""

    binding_error, bound = _validate_bindings(mission_update, prepare_handoff_result, observed_project_head=observed_project_head)
    if binding_error is not None:
        return binding_error
    action = bound["prepared_action"]
    state = bound["state"]
    ticket = bound["ticket"]
    expected_eah = str(action.get("execution_authority_hash") or "")
    if isinstance(prior_execution_outcome, Mapping) and prior_execution_outcome.get("action_evidence_id"):
        return _fail(
            STATUS_HELD,
            "DUPLICATE_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION",
            selected_ticket_id=ticket.get("ticket_id"),
            action_evidence_id=prior_execution_outcome.get("action_evidence_id"),
            execution_phase=PHASE_OUTCOME_UNCERTAIN,
        )
    if not human_authorized_execution_authority_hash or not human_authorization_reference:
        return _fail(
            STATUS_HELD,
            HOLD_AWAITING_VALID_AUTHORIZATION,
            mission_id=state.get("mission_id"),
            selected_ticket_id=ticket.get("ticket_id"),
            prepared_execution_authority_hash=expected_eah,
        )
    if human_authorized_execution_authority_hash != expected_eah:
        return _fail(
            STATUS_HELD,
            HOLD_AWAITING_VALID_AUTHORIZATION,
            mission_id=state.get("mission_id"),
            selected_ticket_id=ticket.get("ticket_id"),
            authorization_binding="EAH_MISMATCH",
        )
    stores = stores_base_dir or action.get("_stores_base_dir")
    root = repo_root or state.get("worktree")
    if not stores or not root:
        return _fail(STATUS_HELD, "EXECUTION_STORE_OR_REPO_ROOT_REQUIRED", selected_ticket_id=ticket.get("ticket_id"))

    executor_result = dict(
        executor(
            action,
            human_authorized_execution_authority_hash,
            human_authorization_reference,
            stores_base_dir=stores,
            repo_root=root,
            session_id=session_id,
        )
    )
    action_evidence_id = executor_result.get("action_evidence_id")
    if not action_evidence_id:
        return _fail(
            STATUS_HELD,
            "MISSING_R8_RECEIPT",
            mission_id=state.get("mission_id"),
            selected_ticket_id=ticket.get("ticket_id"),
            mandate_reference=state.get("human_mandate_reference"),
            prepared_proposal_id=bound["feedback"].get("proposal_id"),
            prepared_patch_hash=action.get("patch_sha256") or _r9_patch_hash(prepare_handoff_result),
            authority_reference={
                "execution_authority_hash": expected_eah,
                "human_authorization_reference": human_authorization_reference,
            },
            execution_phase=PHASE_OUTCOME_UNCERTAIN,
            execution_attempted=True,
            executor_invoked=True,
            executor_result=executor_result,
            budget_consumed=1,
        )
    replay = _R8_REPLAY.replay_action_evidence(action_evidence_id, stores_base_dir=stores)
    reconciliation = _R8_RECONCILE.reconcile_action_evidence(action_evidence_id, stores_base_dir=stores)
    phase, reason = _phase_from_evidence(executor_result, replay, reconciliation)
    status = STATUS_EXECUTION_OUTCOME if phase != PHASE_OUTCOME_UNCERTAIN else STATUS_HELD
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "execution_phase": phase,
        "execution_attempted": True,
        "executor_invoked": True,
        "physical_mutation": bool(reconciliation.get("mutation_performed")),
        "execution_attempt_id": _attempt_id(str(state.get("mission_id")), str(ticket.get("ticket_id")), str(action_evidence_id), expected_eah),
        "mission_id": state.get("mission_id"),
        "selected_ticket_id": ticket.get("ticket_id"),
        "mandate_reference": state.get("human_mandate_reference"),
        "prepared_proposal_id": bound["feedback"].get("proposal_id"),
        "prepared_patch_hash": action.get("patch_sha256") or _r9_patch_hash(prepare_handoff_result),
        "authority_reference": {
            "execution_authority_hash": expected_eah,
            "human_authorization_reference": human_authorization_reference,
        },
        "executor_result": executor_result,
        "action_evidence_id": action_evidence_id,
        "r8_replay": replay,
        "realized_state_reconciliation": reconciliation,
        "r10_repair_classification": _repair_advice(executor_result, reconciliation),
        "pending_verification_status": PHASE_AWAITING_VERIFICATION,
        "budget_consumed": 1,
        "prepared_not_verified": True,
        "executed_not_closed": True,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_ESCALATION_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "HOLD_AWAITING_VALID_AUTHORIZATION",
    "PHASE_AUTHORIZED",
    "PHASE_AWAITING_VERIFICATION",
    "PHASE_EXECUTED_OBSERVED",
    "PHASE_EXECUTION_ATTEMPTED",
    "PHASE_EXECUTION_FAILED",
    "PHASE_OUTCOME_UNCERTAIN",
    "PHASE_PREPARED",
    "STATUS_EXECUTION_OUTCOME",
    "STATUS_HELD",
    "STATUS_REJECTED",
    "execute_supervised_governed_ticket",
    "reconcile_supervised_execution_outcome",
]
