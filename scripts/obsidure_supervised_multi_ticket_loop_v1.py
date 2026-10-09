from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_stepper_v1 import (
    STATUS_PROPOSED as F3A_STATUS_PROPOSED,
    propose_supervised_mission_step,
)
from obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state
from obsidure_supervised_execution_feedback_projection_v1 import project_supervised_execution_feedback
from obsidure_supervised_independent_verification_v1 import verify_supervised_ticket_and_mission_closure
from obsidure_supervised_mission_checkpoint_v1 import save_supervised_mission_checkpoint

STATUS_LOOP_BLOCKED = "BLOCKED"
STATUS_LOOP_LOCAL_HOLD = "LOCAL_HOLD"
STATUS_LOOP_GLOBAL_HOLD = "GLOBAL_HOLD"
STATUS_LOOP_BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
STATUS_LOOP_AWAITING_AUTHORIZATION = "AWAITING_AUTHORIZATION"
STATUS_LOOP_AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
STATUS_LOOP_MISSION_DONE_VERIFIED = "MISSION_DONE_VERIFIED"
STATUS_LOOP_EXPIRED = "TIMEBOX_EXPIRED"
STATUS_LOOP_NO_ELIGIBLE_NEXT = "NO_ELIGIBLE_NEXT"

def run_supervised_multi_ticket_loop(
    mission_state: Mapping[str, Any],
    feedback_provider: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any] | None],
    checkpoint_store_dir: str | Path,
    timebox_seconds: int = 3600,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    start_time = time.time()
    current_state = dict(mission_state)
    
    while True:
        if time.time() - start_time > timebox_seconds:
            return {"status": STATUS_LOOP_EXPIRED, "canonical_state": current_state}
            
        if current_state.get("mandate_revoked") is True or current_state.get("mandate_status") != "ACTIVE":
            return {"status": STATUS_LOOP_BLOCKED, "reason": "MANDATE_REVOKED", "canonical_state": current_state}
            
        budget = current_state.get("global_budget") or {}
        if any(isinstance(budget.get(k), int) and budget.get(k) <= 0 for k in ("remaining_actions", "remaining_attempts", "remaining_tickets")):
            return {"status": STATUS_LOOP_BUDGET_EXHAUSTED, "canonical_state": current_state}
            
        tb = current_state.get("timebox") or {}
        if tb.get("expired") is True:
            return {"status": STATUS_LOOP_EXPIRED, "canonical_state": current_state}
            
        tickets = current_state.get("tickets") or []
        if tickets and all(t.get("status") in {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"} for t in tickets):
            if current_state.get("status") == "R12_F5_C2_MISSION_DONE_VERIFIED" or current_state.get("mission_done") is True:
                return {"status": STATUS_LOOP_MISSION_DONE_VERIFIED, "canonical_state": current_state}
            else:
                return {"status": STATUS_LOOP_AWAITING_VERIFICATION, "canonical_state": current_state}

        step = propose_supervised_mission_step(current_state, observed_project_head=observed_project_head)
        
        if step["status"] != F3A_STATUS_PROPOSED:
            reason = step.get("reason")
            if reason == "GLOBAL_DEPENDENCY_BLOCKER":
                return {"status": STATUS_LOOP_GLOBAL_HOLD, "canonical_state": current_state, "step": step}
            elif reason == "LOCAL_DEPENDENCY_HOLD":
                return {"status": STATUS_LOOP_LOCAL_HOLD, "canonical_state": current_state, "step": step}
            else:
                return {"status": STATUS_LOOP_NO_ELIGIBLE_NEXT, "canonical_state": current_state, "step": step}
                
        feedback = feedback_provider(current_state, step)
        if not feedback:
            return {"status": STATUS_LOOP_AWAITING_AUTHORIZATION, "canonical_state": current_state, "step": step}
            
        handoff = feedback.get("prepare_handoff")
        if not handoff:
            return {"status": STATUS_LOOP_AWAITING_AUTHORIZATION, "canonical_state": current_state, "step": step}
            
        update = integrate_supervised_dependency_state(
            mission_projection=current_state,
            supervisor_step=step,
            prepare_feedback=handoff.get("handoff_feedback", handoff),
            observed_project_head=observed_project_head,
        )
        save_supervised_mission_checkpoint(update, checkpoint_store_dir=checkpoint_store_dir)
        
        outcome = feedback.get("execution_outcome")
        if not outcome:
            current_state = update.get("accepted_state") or current_state
            continue
            
        projected = project_supervised_execution_feedback(
            mission_update=update,
            prepare_handoff_result=handoff,
            execution_outcome=outcome,
            checkpoint_store_dir=checkpoint_store_dir,
            observed_post_action_head=observed_project_head,
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
        
        if final.get("mission_done") is True:
            return {"status": STATUS_LOOP_MISSION_DONE_VERIFIED, "canonical_state": final.get("accepted_state") or current_state}
            
        current_state = final.get("accepted_state") or current_state
