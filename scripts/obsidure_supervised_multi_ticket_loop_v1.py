from __future__ import annotations

import time
import sys
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_stepper_v1 import (
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_supervised_mission_state_v1 import project_supervised_mission_state
from obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state
from obsidure_supervised_execution_feedback_projection_v1 import project_supervised_execution_feedback
from obsidure_supervised_independent_verification_v1 import verify_supervised_ticket_and_mission_closure
from obsidure_supervised_execution_outcome_bridge_v1 import STATUS_EXECUTION_OUTCOME as F5B_STATUS_EXECUTION_OUTCOME
from obsidure_supervised_mission_checkpoint_v1 import (
    STATUS_RESTORED as F5A_STATUS_RESTORED,
    resume_supervised_mission_checkpoint,
    save_supervised_mission_checkpoint,
)

STATUS_LOOP_BLOCKED = "BLOCKED"
STATUS_LOOP_LOCAL_HOLD = "LOCAL_HOLD"
STATUS_LOOP_GLOBAL_HOLD = "GLOBAL_HOLD"
STATUS_LOOP_BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
STATUS_LOOP_AWAITING_AUTHORIZATION = "AWAITING_AUTHORIZATION"
STATUS_LOOP_AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
STATUS_LOOP_MISSION_DONE_VERIFIED = "MISSION_DONE_VERIFIED"
STATUS_LOOP_EXPIRED = "TIMEBOX_EXPIRED"
STATUS_LOOP_NO_ELIGIBLE_NEXT = "NO_ELIGIBLE_NEXT"
STATUS_LOOP_EXECUTION_HOLD = "EXECUTION_HOLD"
STATUS_LOOP_VERIFICATION_HOLD = "VERIFICATION_HOLD"
STATUS_LOOP_RECOVERY_HOLD = "RECOVERY_HOLD"


def _tickets(state: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [ticket for ticket in state.get("tickets") or [] if isinstance(ticket, Mapping)]


def _ticket_by_id(state: Mapping[str, Any], ticket_id: str) -> Mapping[str, Any] | None:
    for ticket in _tickets(state):
        if str(ticket.get("ticket_id") or "") == ticket_id:
            return ticket
    return None


def _has_pending_verification(state: Mapping[str, Any]) -> bool:
    return any(
        ticket.get("status") == "HELD"
        and (
            ticket.get("hold_reason") == "AWAITING_INDEPENDENT_VERIFICATION"
            or ticket.get("execution_phase") == "AWAITING_INDEPENDENT_VERIFICATION"
        )
        for ticket in _tickets(state)
    )


def _all_tickets_closed(state: Mapping[str, Any]) -> bool:
    tickets = _tickets(state)
    return bool(tickets) and all(
        str(ticket.get("status") or "").upper() in {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"}
        and ticket.get("closed") is True
        for ticket in tickets
    )


def _preserve_closed_ticket_metadata(previous_state: Mapping[str, Any], next_state: Mapping[str, Any]) -> dict[str, Any]:
    updated = deepcopy(dict(next_state))
    previous_by_id = {
        str(ticket.get("ticket_id") or ""): ticket
        for ticket in _tickets(previous_state)
        if ticket.get("closed") is True
    }
    if not previous_by_id:
        return updated
    tickets = []
    for ticket in _tickets(updated):
        copied = deepcopy(dict(ticket))
        previous = previous_by_id.get(str(copied.get("ticket_id") or ""))
        if previous and str(copied.get("status") or "").upper() in {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"}:
            for key in (
                "closed",
                "verified",
                "verification_level",
                "independent_verification_status",
                "independent_verification_id",
            ):
                if previous.get(key) is not None and copied.get(key) is None:
                    copied[key] = previous.get(key)
        tickets.append(copied)
    updated["tickets"] = tickets
    return updated


def _authority_ref(outcome: Mapping[str, Any]) -> str:
    authority = outcome.get("authority_reference") if isinstance(outcome.get("authority_reference"), Mapping) else {}
    return str(authority.get("human_authorization_reference") or authority.get("execution_authority_hash") or "")


def _append_trace(trace: dict[str, Any], key: str, value: Any) -> None:
    trace.setdefault(key, []).append(_json_safe(value))


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _with_trace(result: dict[str, Any], trace: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(result)
    out.setdefault("controller_trace", _json_safe(dict(trace)))
    out.setdefault("real_multi_ticket_executions", len(trace.get("execution_outcomes", [])))
    out.setdefault("r8_receipts", [item.get("action_evidence_id") for item in trace.get("execution_outcomes", []) if isinstance(item, Mapping) and item.get("action_evidence_id")])
    out.setdefault("f5_c1_feedback_count", len(trace.get("f5c1_feedbacks", [])))
    out.setdefault("f5_c2_verification_count", len(trace.get("verification_results", [])))
    out.setdefault("separate_authorizations", len(set(trace.get("authorization_refs", []))) == len(trace.get("authorization_refs", [])))
    out.setdefault("mission_completion_proof", None)
    out.setdefault("duplicate_mutation_prevented", bool(trace.get("duplicate_mutation_prevented", False)))
    out.setdefault("decision_authority", "KX108_ONLY")
    out.setdefault("supervisor_authority", "NONE")
    out.setdefault("approval_created", False)
    out.setdefault("kx108_called", False)
    out.setdefault("binder_mutation", False)
    out.setdefault("executor_invoked", False)
    out.setdefault("memory_write", False)
    out.setdefault("native_memory_write", False)
    out.setdefault("push_performed", False)
    out.setdefault("merge_performed", False)
    return out


def _canonical_state(source: Mapping[str, Any]) -> dict[str, Any]:
    state = source.get("canonical_state") if isinstance(source.get("canonical_state"), Mapping) else source
    out = dict(state)
    if state is not source:
        for key in (
            "mandate_status",
            "mandate_revoked",
            "global_budget",
            "timebox",
            "tickets",
            "evidence_refs",
            "explicit_unknowns",
        ):
            if key in source:
                out[key] = deepcopy(source[key])
    return out


def _resume_state_if_requested(
    mission_state: Mapping[str, Any],
    checkpoint_store_dir: str | Path,
    checkpoint_id: str | None,
    observed_project_head: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not checkpoint_id:
        return _canonical_state(mission_state), None
    restored = resume_supervised_mission_checkpoint(
        checkpoint_id,
        checkpoint_store_dir=checkpoint_store_dir,
        observed_project_head=observed_project_head,
    )
    if restored.get("status") != F5A_STATUS_RESTORED:
        return None, restored
    return dict(restored.get("restored_state") or mission_state), restored

def run_supervised_multi_ticket_loop(
    mission_state: Mapping[str, Any],
    feedback_provider: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any] | None],
    checkpoint_store_dir: str | Path,
    timebox_seconds: int = 3600,
    observed_project_head: str | None = None,
    resume_checkpoint_id: str | None = None,
) -> dict[str, Any]:
    start_time = time.time()
    current_state, resume_result = _resume_state_if_requested(
        mission_state,
        checkpoint_store_dir,
        resume_checkpoint_id,
        observed_project_head,
    )
    trace: dict[str, Any] = {
        "prepare_results": [],
        "execution_outcomes": [],
        "f5c1_feedbacks": [],
        "verification_results": [],
        "checkpoints": [],
        "authorization_refs": [],
    }
    if current_state is None:
        return _with_trace(
            {"status": STATUS_LOOP_RECOVERY_HOLD, "reason": "CHECKPOINT_RESUME_FAILED", "resume_result": resume_result},
            trace,
        )
    if resume_result is not None:
        trace["resume_result"] = resume_result
    
    while True:
        if time.time() - start_time > timebox_seconds:
            return _with_trace({"status": STATUS_LOOP_EXPIRED, "canonical_state": current_state}, trace)
            
        if current_state.get("mandate_revoked") is True or current_state.get("mandate_status") != "ACTIVE":
            return _with_trace({"status": STATUS_LOOP_BLOCKED, "reason": "MANDATE_REVOKED", "canonical_state": current_state}, trace)
            
        budget = current_state.get("global_budget") or {}
        if any(isinstance(budget.get(k), int) and budget.get(k) <= 0 for k in ("remaining_actions", "remaining_attempts", "remaining_tickets")):
            return _with_trace({"status": STATUS_LOOP_BUDGET_EXHAUSTED, "canonical_state": current_state}, trace)
            
        tb = current_state.get("timebox") or {}
        if tb.get("expired") is True:
            return _with_trace({"status": STATUS_LOOP_EXPIRED, "canonical_state": current_state}, trace)
            
        if _all_tickets_closed(current_state):
            if current_state.get("status") == "R12_F5_C2_MISSION_DONE_VERIFIED" or current_state.get("mission_done") is True:
                return _with_trace({"status": STATUS_LOOP_MISSION_DONE_VERIFIED, "canonical_state": current_state}, trace)
            else:
                return _with_trace({"status": STATUS_LOOP_AWAITING_VERIFICATION, "canonical_state": current_state}, trace)
        if _has_pending_verification(current_state):
            trace["duplicate_mutation_prevented"] = True
            return _with_trace(
                {"status": STATUS_LOOP_AWAITING_VERIFICATION, "reason": "PENDING_VERIFICATION_REQUIRES_RECONCILIATION", "canonical_state": current_state},
                trace,
            )

        step = propose_supervised_mission_step(current_state, observed_project_head=observed_project_head)
        
        if step["status"] != F3A_STATUS_PROPOSED:
            reason = step.get("reason")
            if reason == "GLOBAL_DEPENDENCY_BLOCKER":
                return _with_trace({"status": STATUS_LOOP_GLOBAL_HOLD, "canonical_state": current_state, "step": step}, trace)
            elif reason == "LOCAL_DEPENDENCY_HOLD":
                return _with_trace({"status": STATUS_LOOP_LOCAL_HOLD, "canonical_state": current_state, "step": step}, trace)
            else:
                return _with_trace({"status": STATUS_LOOP_NO_ELIGIBLE_NEXT, "canonical_state": current_state, "step": step}, trace)
                
        mission_projection = project_supervised_mission_state(current_state, observed_project_head=observed_project_head)
        feedback = feedback_provider(mission_projection, step)
        if not feedback:
            return _with_trace({"status": STATUS_LOOP_AWAITING_AUTHORIZATION, "canonical_state": current_state, "step": step}, trace)
            
        handoff = feedback.get("prepare_handoff")
        if not handoff:
            return _with_trace({"status": STATUS_LOOP_AWAITING_AUTHORIZATION, "canonical_state": current_state, "step": step}, trace)
        _append_trace(trace, "prepare_results", handoff)
            
        update = integrate_supervised_dependency_state(
            mission_projection=mission_projection,
            supervisor_step=step,
            prepare_feedback=handoff.get("handoff_feedback", handoff),
            observed_project_head=observed_project_head,
        )
        checkpoint = save_supervised_mission_checkpoint(update, checkpoint_store_dir=checkpoint_store_dir)
        _append_trace(trace, "checkpoints", checkpoint)
        if update.get("mission_update_accepted") is not True:
            return _with_trace(
                {"status": STATUS_LOOP_LOCAL_HOLD, "reason": update.get("reason") or "PREPARE_FEEDBACK_HELD", "canonical_state": current_state, "update": update},
                trace,
            )
        if isinstance(update.get("accepted_state"), Mapping):
            update = dict(update)
            update["accepted_state"] = _preserve_closed_ticket_metadata(current_state, update["accepted_state"])
        
        outcome = feedback.get("execution_outcome")
        if not outcome:
            current_state = update.get("accepted_state") or current_state
            continue
        if not isinstance(outcome, Mapping):
            return _with_trace({"status": STATUS_LOOP_EXECUTION_HOLD, "reason": "EXECUTION_OUTCOME_MALFORMED", "canonical_state": current_state}, trace)
        authority_ref = _authority_ref(outcome)
        if authority_ref and authority_ref in trace["authorization_refs"]:
            return _with_trace(
                {"status": STATUS_LOOP_EXECUTION_HOLD, "reason": "AUTHORIZATION_REUSED", "canonical_state": current_state, "execution_outcome": outcome},
                trace,
            )
        if authority_ref:
            trace["authorization_refs"].append(authority_ref)
        _append_trace(trace, "execution_outcomes", outcome)
        if outcome.get("status") != F5B_STATUS_EXECUTION_OUTCOME:
            reason = outcome.get("reason") or "EXECUTION_OUTCOME_HELD"
            return _with_trace(
                {"status": STATUS_LOOP_EXECUTION_HOLD, "reason": reason, "canonical_state": update.get("accepted_state") or current_state, "execution_outcome": outcome},
                trace,
            )
        if outcome.get("reason"):
            return _with_trace(
                {"status": STATUS_LOOP_EXECUTION_HOLD, "reason": outcome.get("reason"), "canonical_state": update.get("accepted_state") or current_state, "execution_outcome": outcome},
                trace,
            )
            
        projected = project_supervised_execution_feedback(
            mission_update=update,
            prepare_handoff_result=handoff,
            execution_outcome=outcome,
            checkpoint_store_dir=checkpoint_store_dir,
            observed_post_action_head=observed_project_head,
        )
        if isinstance(projected.get("accepted_state"), Mapping):
            projected = dict(projected)
            projected["accepted_state"] = _preserve_closed_ticket_metadata(update.get("accepted_state") or current_state, projected["accepted_state"])
        _append_trace(trace, "f5c1_feedbacks", projected)
        if projected.get("execution_feedback_projected") is not True:
            reason = projected.get("reason") or "EXECUTION_FEEDBACK_HELD"
            status = STATUS_LOOP_RECOVERY_HOLD if "R8" in str(reason) or "UNCERTAIN" in str(reason) else STATUS_LOOP_EXECUTION_HOLD
            return _with_trace(
                {"status": status, "reason": reason, "canonical_state": projected.get("accepted_state") or update.get("accepted_state") or current_state, "f5c1_feedback": projected},
                trace,
            )
        
        verification = feedback.get("verification_evidence")
        if not verification:
            current_state = projected.get("accepted_state") or current_state
            continue
            
        final = verify_supervised_ticket_and_mission_closure(
            execution_feedback_projection=projected,
            verification_evidence=verification,
            checkpoint_store_dir=checkpoint_store_dir,
            observed_project_head=observed_project_head,
        )
        _append_trace(trace, "verification_results", final)
        if final.get("ticket_closed") is not True:
            return _with_trace(
                {"status": STATUS_LOOP_VERIFICATION_HOLD, "reason": final.get("reason") or "VERIFICATION_HELD", "canonical_state": final.get("accepted_state") or projected.get("accepted_state") or current_state, "verification_result": final},
                trace,
            )
        if isinstance(final.get("accepted_state"), Mapping):
            final = dict(final)
            final["accepted_state"] = _preserve_closed_ticket_metadata(projected.get("accepted_state") or current_state, final["accepted_state"])
        
        if final.get("mission_done") is True:
            state = dict(final.get("accepted_state") or current_state)
            state["mission_done"] = True
            state["status"] = "R12_F5_C2_MISSION_DONE_VERIFIED"
            state["mission_completion_proof"] = final.get("mission_completion_proof")
            return _with_trace({"status": STATUS_LOOP_MISSION_DONE_VERIFIED, "canonical_state": state, "mission_completion_proof": final.get("mission_completion_proof")}, trace)
            
        current_state = final.get("accepted_state") or current_state
