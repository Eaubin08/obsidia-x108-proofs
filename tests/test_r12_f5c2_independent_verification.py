from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
TESTS = WORKTREE / "tests"
for p in (SCRIPTS, TESTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_supervised_independent_verification_v1 import (  # noqa: E402
    STATUS_HELD,
    STATUS_REJECTED,
    STATUS_VERIFIED,
    verify_supervised_ticket_and_mission_closure,
)
from obsidure_supervised_mission_checkpoint_v1 import (  # noqa: E402
    STATUS_RESTORED,
    resume_supervised_mission_checkpoint,
)
from test_r12_f3b_governed_prepare_handoff import TARGET, _handoff, _projection, _step, _world  # noqa: E402
from test_r12_f5b_supervised_execution_outcome_bridge import _prepared_update  # noqa: E402
from test_r12_f5c1_supervised_execution_feedback_projection import _execute  # noqa: E402
from obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state  # noqa: E402
from obsidure_supervised_execution_feedback_projection_v1 import project_supervised_execution_feedback  # noqa: E402


def _plain(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _project(state):
    return {
        "repository_identity": state["repository_identity"],
        "local_root": state["local_root"],
        "worktree": state["worktree"],
        "branch": state["branch"],
        "base_sha": state["base_sha"],
    }


def _executed_projection(world, **kwargs):
    projection, step, handoff, update = _prepared_update(world)
    project_kwargs = kwargs.pop("project_kwargs", {})
    outcome = kwargs.pop("outcome", None)
    if outcome is None:
        outcome = _execute(world, handoff, update, **kwargs)
    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        **project_kwargs,
    )
    assert projected["status"] == "R12_F5_C1_EXECUTION_FEEDBACK_PROJECTED"
    return projection, step, handoff, update, outcome, projected


def _verification(outcome, projected, *, ticket_id=None, mission_results=True):
    state = projected["accepted_state"]
    ticket_id = ticket_id or projected["selected_ticket_id"]
    ticket = next(t for t in state["tickets"] if t["ticket_id"] == ticket_id)
    ticket_criteria = ticket.get("acceptance_criteria") or ["R9 prepare result exists"]
    mission_criteria = state.get("acceptance_criteria") or []
    data = {
        "verification_id": "ver-r12-f5c2-" + ticket_id,
        "mission_id": state["mission_id"],
        "ticket_id": ticket_id,
        "mandate_reference": state["human_mandate_reference"],
        "project": _project(state),
        "action_evidence_id": outcome["action_evidence_id"],
        "execution_attempt_id": outcome["execution_attempt_id"],
        "prepared_proposal_id": outcome["prepared_proposal_id"],
        "prepared_patch_hash": outcome["prepared_patch_hash"],
        "authority_reference": outcome["authority_reference"],
        "r8_replay": {**outcome["r8_replay"], "replay_verdict": "VERIFIED", "binder_replay_status": None},
        "realized_state_reconciliation": outcome["realized_state_reconciliation"],
        "reviewer_verdict": "PASS",
        "reviewer_independent": True,
        "reviewer_reference": "review-r12-f5c2",
        "test_evidence": [
            {
                "test_id": "pytest-r12-f5c2-disposable",
                "status": "PASS",
                "independently_checked": True,
                "real_input_tested": True,
                "evidence_ref": "test-ref-r12-f5c2",
            }
        ],
        "acceptance_criteria_results": [
            {"criterion": criterion, "status": "PASS", "evidence_ref": "accept-" + str(index)}
            for index, criterion in enumerate(ticket_criteria)
        ],
        "mission_acceptance_criteria_results": [
            {"criterion": criterion, "status": "PASS", "evidence_ref": "mission-accept-" + str(index)}
            for index, criterion in enumerate(mission_criteria)
        ]
        if mission_results
        else [],
        "observed_project": {
            "original_base_sha": state["base_sha"],
            "current_head": state["base_sha"],
            "authorized_state_evolution": False,
        },
        "unknowns": [],
        "contradictions": [],
    }
    return data


def test_valid_verified_ticket_closes_but_does_not_falsely_complete_mission(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    evidence = _verification(outcome, projected)

    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=evidence,
    )

    assert out["status"] == STATUS_VERIFIED
    assert out["ticket_verified"] is True
    assert out["ticket_closed"] is True
    assert out["accepted_state"]["tickets"][0]["status"] == "COMPLETED"
    assert out["accepted_state"]["tickets"][0]["closed"] is True
    assert out["mission_done"] is True
    assert out["mission_completion_proof"]["completion_proof_digest"]
    assert out["executor_invoked"] is False
    assert out["memory_write"] is False


def test_execution_success_but_failing_tests_defect_open(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    evidence = _verification(outcome, projected)
    evidence["test_evidence"][0]["status"] = "FAIL"

    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=evidence,
    )

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "INDEPENDENT_TEST_FAILED"
    assert out["defect_open"] is True
    assert out["ticket_closed"] is False


def test_successful_tests_but_unmet_acceptance_holds(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    evidence = _verification(outcome, projected)
    evidence["acceptance_criteria_results"][0]["status"] = "FAIL"

    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=evidence,
    )

    assert out["status"] == STATUS_HELD
    assert out["reason"].startswith("ACCEPTANCE_CRITERION_NOT_MET")
    assert out["mission_done"] is False


def test_missing_r8_receipt_and_forged_reviewer_pass_fail_closed(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    missing_r8 = _verification(outcome, projected)
    del missing_r8["r8_replay"]
    forged_reviewer = _verification(outcome, projected)
    forged_reviewer["reviewer_independent"] = False

    assert verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=missing_r8,
    )["reason"] == "R8_REPLAY_REQUIRED"
    assert verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=forged_reviewer,
    )["reason"] == "INDEPENDENT_REVIEWER_PASS_REQUIRED"


def test_contradictory_evidence_and_upstream_hold_prevent_closure(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    contradictory = _verification(outcome, projected)
    contradictory["contradictions"] = ["review says pass but realized state says mismatch"]
    assert verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=contradictory,
    )["reason"] == "CONTRADICTORY_CRITICAL_EVIDENCE"

    blocked = deepcopy(projected)
    blocked["accepted_state"]["tickets"].append(
        {
            "ticket_id": "dependent",
            "objective": "Blocked dependent ticket",
            "dependency_ids": ["ticket-f3b"],
            "status": "HELD",
            "hold_reason": "AWAITING_INDEPENDENT_VERIFICATION",
            "acceptance_criteria": ["dependent verified"],
            "authorized_paths": [TARGET],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "evidence_refs": [outcome["action_evidence_id"]],
            "execution_phase": "AWAITING_INDEPENDENT_VERIFICATION",
            "action_evidence_id": outcome["action_evidence_id"],
            "execution_attempt_id": outcome["execution_attempt_id"],
        }
    )
    blocked["selected_ticket_id"] = "dependent"
    blocked["transitive_dependency_blocks"] = [{"ticket_id": "dependent", "reason": "DEPENDENCY_NOT_VERIFIED", "root_ticket_id": "other"}]
    evidence = _verification(outcome, blocked, ticket_id="dependent")
    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=blocked,
        verification_evidence=evidence,
    )
    assert out["status"] == STATUS_HELD
    assert out["reason"].startswith("TICKET_BLOCKED_BY_DEPENDENCY")


def test_multi_ticket_completed_mission_and_partial_mission(tmp_path):
    world = _world(tmp_path)
    projection = _projection(
        world,
        tickets=[
            {
                "ticket_id": "ticket-f3b",
                "objective": "Prepare governed patch handoff",
                "status": "PENDING",
                "authorized_paths": [TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
            },
            {
                "ticket_id": "second",
                "objective": "Already verified second ticket",
                "status": "COMPLETED",
                "dependency_classification": "PASS",
                "acceptance_criteria": ["second closed"],
                "evidence_refs": ["second-proof"],
            },
        ],
    )
    projection["canonical_state"]["tickets"][1]["verified"] = True
    projection["canonical_state"]["tickets"][1]["closed"] = True
    step = _step(world, projection)
    handoff = _handoff(world, mission_projection=projection, supervisor_step=step)
    update = integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=handoff["handoff_feedback"],
    )
    outcome = _execute(world, handoff, update)
    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )

    complete = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=_verification(outcome, projected),
    )
    assert complete["mission_done"] is True, f"Failed with reason: {complete.get('reason')} - Tickets: {complete['accepted_state']['tickets']}"
    assert complete["mission_completion_proof"]["dependency_graph_resolved"] is True

    (tmp_path / "partial").mkdir()
    partial_world = _world(tmp_path / "partial")
    partial_projection = _projection(
        partial_world,
        global_budget={"remaining_actions": 4, "remaining_attempts": 4, "remaining_tickets": 2},
        tickets=[
            {
                "ticket_id": "ticket-f3b",
                "objective": "Prepare governed patch handoff",
                "status": "PENDING",
                "authorized_paths": [TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
            },
            {"ticket_id": "second", "objective": "Later independent ticket", "status": "PENDING", "acceptance_criteria": ["later"]},
        ],
    )
    step = _step(partial_world, partial_projection)
    handoff = _handoff(partial_world, mission_projection=partial_projection, supervisor_step=step)
    update = integrate_supervised_dependency_state(
        mission_projection=partial_projection,
        supervisor_step=step,
        prepare_feedback=handoff["handoff_feedback"],
    )
    outcome = _execute(partial_world, handoff, update)
    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )
    partial = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=_verification(outcome, projected),
    )
    assert partial["ticket_closed"] is True
    assert partial["mission_done"] is False
    assert partial["unique_next_ticket_id"] == "second"


def test_all_tickets_closed_but_global_criteria_unmet_and_unresolved_defect_prevent_done(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    unmet = _verification(outcome, projected, mission_results=False)
    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=unmet,
    )
    assert out["ticket_closed"] is True
    assert out["mission_done"] is False
    assert "ACCEPTANCE_CRITERION" in out["reason"]

    defect = deepcopy(projected)
    defect["accepted_state"]["tickets"].append(
        {"ticket_id": "defect", "objective": "Open defect", "status": "EXECUTION_FAILED", "blocked_reason": "DEFECT_OPEN", "evidence_refs": ["defect-ref"]}
    )
    evidence = _verification(outcome, defect)
    blocked = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=defect,
        verification_evidence=evidence,
    )
    assert blocked["mission_done"] is False
    assert blocked["root_dependency_blocks"]


def test_unauthorized_project_drift_and_legitimate_state_evolution(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world, project_kwargs={"observed_post_action_head": "b" * 40})
    bad = _verification(outcome, projected)
    bad["observed_project"]["current_head"] = "c" * 40
    bad["observed_project"]["authorized_state_evolution"] = False
    assert verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=bad,
        observed_project_head="c" * 40,
    )["reason"] == "UNAUTHORIZED_PROJECT_DRIFT"

    good = _verification(outcome, projected)
    good["observed_project"]["current_head"] = "b" * 40
    good["observed_project"]["authorized_state_evolution"] = True
    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=good,
        observed_project_head="b" * 40,
    )
    assert out["status"] == STATUS_VERIFIED
    assert out["git_state_revalidated"] is True


def test_checkpoint_resume_before_and_after_verification_and_idempotence(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)
    c1 = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    restored = resume_supervised_mission_checkpoint(c1["checkpoint"]["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")
    resumed_projection = dict(c1)
    resumed_projection["accepted_state"] = restored["restored_state"]

    evidence = _verification(outcome, resumed_projection)
    first = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=resumed_projection,
        verification_evidence=evidence,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    duplicate = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=resumed_projection,
        verification_evidence=evidence,
        prior_verification_evidence=evidence,
    )
    conflict = _plain(evidence)
    conflict["test_evidence"][0]["evidence_ref"] = "other-test-ref"
    conflict_out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=resumed_projection,
        verification_evidence=conflict,
        prior_verification_evidence=evidence,
    )

    assert restored["status"] == STATUS_RESTORED
    assert first["checkpoint"]["checkpoint_saved"] is True
    assert duplicate["duplicate_idempotent"] is True
    assert duplicate["accepted_state_hash"] == first["accepted_state_hash"]
    assert conflict_out["status"] == STATUS_HELD
    assert conflict_out["reason"] == "DUPLICATE_VERIFICATION_EVIDENCE_CONFLICT"


def test_completion_proof_integrity_and_no_authority_side_effects(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=_verification(outcome, projected),
    )

    proof = out["mission_completion_proof"]
    assert proof["mission_id"] == projected["accepted_state"]["mission_id"]
    assert proof["human_mandate_reference"] == projected["accepted_state"]["human_mandate_reference"]
    assert proof["reviewer_verdict"] == "PASS"
    assert proof["completion_proof_digest"]
    assert out["approval_created"] is False
    assert out["kx108_called"] is False
    assert out["binder_mutation"] is False
    assert out["executor_invoked"] is False
    assert out["automatic_retry"] is False
    assert out["native_memory_write"] is False


def test_r8_verified_with_limits_holds_for_binder_reconstruction(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world)
    evidence = _verification(outcome, projected)
    evidence["r8_replay"]["replay_verdict"] = "VERIFIED_WITH_LIMITS"
    evidence["r8_replay"]["binder_replay_status"] = "INLINE_STATUS_ONLY"

    out = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=evidence,
    )

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "BINDER_DECISION_RECONSTRUCTION_REQUIRED"
    assert out["ticket_closed"] is False


def test_scope_drift_and_evolution_authority_rules(tmp_path):
    world = _world(tmp_path)
    *_unused, outcome, projected = _executed_projection(world, project_kwargs={"observed_post_action_head": "b" * 40})
    
    # Missing evolution authority evidence
    missing_evol_auth = _verification(outcome, projected)
    missing_evol_auth["observed_project"]["current_head"] = "b" * 40
    missing_evol_auth["observed_project"]["authorized_state_evolution"] = True
    missing_evol_auth["authority_reference"] = None
    
    out_missing = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=missing_evol_auth,
        observed_project_head="b" * 40,
    )
    assert out_missing["reason"] == "MISSING_EVOLUTION_AUTHORITY_EVIDENCE"

    # Unapproved scope drift
    unapproved_drift = _verification(outcome, projected)
    unapproved_drift["observed_project"]["scope_drift_observed"] = True
    unapproved_drift["observed_project"]["scope_drift_approved"] = False
    
    out_unapproved = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=unapproved_drift,
    )
    assert out_unapproved["reason"] == "UNAPPROVED_SCOPE_DRIFT"

    # Missing scope drift authority
    missing_drift_auth = _verification(outcome, projected)
    missing_drift_auth["observed_project"]["scope_drift_observed"] = True
    missing_drift_auth["observed_project"]["scope_drift_approved"] = True
    missing_drift_auth["authority_reference"] = None
    
    out_missing_drift = verify_supervised_ticket_and_mission_closure(
        execution_feedback_projection=projected,
        verification_evidence=missing_drift_auth,
    )
    assert out_missing_drift["reason"] == "MISSING_SCOPE_DRIFT_AUTHORITY_EVIDENCE"

