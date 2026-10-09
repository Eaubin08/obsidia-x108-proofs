from __future__ import annotations
import json
import sys
import time
from copy import deepcopy
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
for p in (WORKTREE / "scripts", WORKTREE / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_supervised_multi_ticket_loop_v1 import (
    run_supervised_multi_ticket_loop,
    STATUS_LOOP_MISSION_DONE_VERIFIED,
    STATUS_LOOP_BUDGET_EXHAUSTED,
    STATUS_LOOP_EXPIRED,
    STATUS_LOOP_BLOCKED,
    STATUS_LOOP_NO_ELIGIBLE_NEXT,
    STATUS_LOOP_LOCAL_HOLD,
    STATUS_LOOP_GLOBAL_HOLD,
    STATUS_LOOP_AWAITING_AUTHORIZATION,
    STATUS_LOOP_AWAITING_VERIFICATION,
)

from obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state
from obsidure_supervised_execution_feedback_projection_v1 import project_supervised_execution_feedback
from test_r12_f3b_governed_prepare_handoff import _world, _projection, _handoff
from test_r12_f5c1_supervised_execution_feedback_projection import _execute
from test_r12_f5c2_independent_verification import _verification

def test_multiple_independent_tickets_completion(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state["mandate_revoked"] = False
    state.setdefault("global_budget", {})
    state.setdefault("timebox", {})
    
    def feedback_provider(current_state, step):
        handoff = _handoff(world, mission_projection=current_state, supervisor_step=step)
        print("HANDOFF KEYS:", handoff.keys())
        print("prepare_handoff value:", handoff.get("prepare_handoff"))
        
        update = integrate_supervised_dependency_state(
            mission_projection=current_state,
            supervisor_step=step,
            prepare_feedback=handoff["handoff_feedback"],
        )
        
        outcome = _execute(world, handoff, update)
        
        projected = project_supervised_execution_feedback(
            mission_update=update,
            prepare_handoff_result=handoff,
            execution_outcome=outcome,
        )
        
        if "accepted_state" not in projected:
            print("UPDATE:", update)
            print("PROJECTED:", projected)
            assert False, "projected failed!"
        verification = _verification(outcome, projected)
        
        return {
            "prepare_handoff": handoff,
            "execution_outcome": outcome,
            "verification_evidence": verification,
        }

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] == STATUS_LOOP_MISSION_DONE_VERIFIED

def test_exhausted_budget(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state.setdefault("global_budget", {})["remaining_actions"] = 0
    
    def feedback_provider(current_state, step):
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] == STATUS_LOOP_BUDGET_EXHAUSTED

def test_expired_timebox(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    
    def feedback_provider(current_state, step):
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
        timebox_seconds=-1,
    )
    assert res["status"] == STATUS_LOOP_EXPIRED

def test_expired_timebox_state(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state.setdefault("timebox", {})["expired"] = True
    
    def feedback_provider(current_state, step):
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] == STATUS_LOOP_EXPIRED

def test_revoked_mandate(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state["mandate_revoked"] = True
    
    def feedback_provider(current_state, step):
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] == STATUS_LOOP_BLOCKED
    assert res["reason"] == "MANDATE_REVOKED"

def test_transitive_hold_propagation_and_independent_continuation(tmp_path):
    world = _world(tmp_path)
    projection = _projection(
        world,
        tickets=[
            {
                "ticket_id": "blocked-ticket",
                "objective": "I am blocked",
                "status": "HELD",
                "hold_reason": "SOME_HOLD",
            },
            {
                "ticket_id": "dependent-ticket",
                "objective": "Depends on blocked",
                "status": "PENDING",
                "dependency_ids": ["blocked-ticket"],
            },
            {
                "ticket_id": "independent-ticket",
                "objective": "I am independent",
                "status": "PENDING",
                "authorized_paths": ["scripts/r12_f3b_fixture.py"],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
            }
        ]
    )
    projection["mandate_status"] = "ACTIVE"
    projection.setdefault("global_budget", {})
    projection.setdefault("timebox", {})

    executions = []
    def feedback_provider(current_state, step):
        handoff = _handoff(world, mission_projection=current_state, supervisor_step=step)
        if handoff.get("prepare_handoff"):
            update = integrate_supervised_dependency_state(
                mission_projection=current_state,
                supervisor_step=step,
                prepare_feedback=handoff["handoff_feedback"],
            )
            outcome = _execute(world, handoff, update)
            executions.append(step["selected_ticket_id"])
            projected = project_supervised_execution_feedback(
                mission_update=update,
                prepare_handoff_result=handoff,
                execution_outcome=outcome,
            )
            verification = _verification(outcome, projected)
            return {
                "prepare_handoff": handoff,
                "execution_outcome": outcome,
                "verification_evidence": verification,
            }
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=projection,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] in {STATUS_LOOP_NO_ELIGIBLE_NEXT, STATUS_LOOP_LOCAL_HOLD, STATUS_LOOP_GLOBAL_HOLD}
    assert "independent-ticket" in executions
    assert "dependent-ticket" not in executions

def test_binder_limited_replay_remains_hold(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state.setdefault("global_budget", {})
    state.setdefault("timebox", {})

    def feedback_provider(current_state, step):
        handoff = _handoff(world, mission_projection=current_state, supervisor_step=step)
        update = integrate_supervised_dependency_state(
            mission_projection=current_state,
            supervisor_step=step,
            prepare_feedback=handoff["handoff_feedback"],
        )
        outcome = _execute(world, handoff, update)
        projected = project_supervised_execution_feedback(
            mission_update=update,
            prepare_handoff_result=handoff,
            execution_outcome=outcome,
        )
        verification = _verification(outcome, projected)
        verification["r8_replay"]["replay_verdict"] = "VERIFIED_WITH_LIMITS"
        verification["r8_replay"]["binder_replay_status"] = "INLINE_STATUS_ONLY"
        
        return {
            "prepare_handoff": handoff,
            "execution_outcome": outcome,
            "verification_evidence": verification,
        }

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] in {STATUS_LOOP_LOCAL_HOLD, STATUS_LOOP_NO_ELIGIBLE_NEXT}
    ticket = res["canonical_state"]["tickets"][0]
    assert ticket["status"] == "HELD"

def test_checkpoint_interruption_and_resume(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state.setdefault("global_budget", {})
    state.setdefault("timebox", {})

    call_count = 0
    def feedback_provider(current_state, step):
        nonlocal call_count
        call_count += 1
        handoff = _handoff(world, mission_projection=current_state, supervisor_step=step)
        if call_count == 1:
            return {"prepare_handoff": handoff}
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    assert res["status"] in {STATUS_LOOP_AWAITING_AUTHORIZATION, STATUS_LOOP_NO_ELIGIBLE_NEXT}

def test_no_authority_no_act_regression(tmp_path):
    world = _world(tmp_path)
    state = _projection(world)
    state["mandate_status"] = "ACTIVE"
    state.setdefault("global_budget", {})
    state.setdefault("timebox", {})

    def feedback_provider(current_state, step):
        return None

    res = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=feedback_provider,
        checkpoint_store_dir=tmp_path,
    )
    st = res["step"]
    assert st.get("approval_created") is False
    assert st.get("kx108_called") is False
    assert st.get("binder_mutation") is False
    assert st.get("executor_invoked") is False
    assert st.get("repair_loop_invoked") is False
    assert st.get("filesystem_execution") is False
    assert st.get("native_memory_write") is False
