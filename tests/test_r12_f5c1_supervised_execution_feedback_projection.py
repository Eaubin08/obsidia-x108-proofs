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

import obsidia_realized_state_reconciliation_v1 as R8_REC  # noqa: E402
from obsidure_supervised_execution_feedback_projection_v1 import (  # noqa: E402
    STATUS_HELD,
    STATUS_PROJECTED,
    project_supervised_execution_feedback,
)
from obsidure_supervised_execution_outcome_bridge_v1 import (  # noqa: E402
    PHASE_EXECUTED_OBSERVED,
    PHASE_EXECUTION_FAILED,
    PHASE_OUTCOME_UNCERTAIN,
    execute_supervised_governed_ticket,
)
from obsidure_supervised_mission_checkpoint_v1 import (  # noqa: E402
    STATUS_RESTORED,
    resume_supervised_mission_checkpoint,
)
from test_r12_f3b_governed_prepare_handoff import TARGET, _handoff, _projection, _step, _world  # noqa: E402
from test_r12_f5b_supervised_execution_outcome_bridge import _prepared_update  # noqa: E402


def _execute(world, handoff, update, **kwargs):
    action = handoff["r9_prepare_result"]["prepared_action"]
    return execute_supervised_governed_ticket(
        mission_update=update,
        prepare_handoff_result=handoff,
        human_authorized_execution_authority_hash=kwargs.pop("eah", action["execution_authority_hash"]),
        human_authorization_reference=kwargs.pop("auth_ref", "human-r12-f5c1-authorization"),
        stores_base_dir=world["stores"],
        repo_root=world["exec_wt"],
        session_id="r12-f5c1",
        **kwargs,
    )


def _feedback(world, **kwargs):
    projection, step, handoff, update = _prepared_update(world)
    outcome = kwargs.pop("outcome", None) or _execute(world, handoff, update, **kwargs)
    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        **kwargs.pop("project_kwargs", {}),
    )
    return projection, step, handoff, update, outcome, projected


def _plain(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def test_valid_observed_execution_feedback_records_phase_without_verification_or_closure(tmp_path):
    world = _world(tmp_path)

    *_unused, outcome, projected = _feedback(world)

    assert outcome["execution_phase"] == PHASE_EXECUTED_OBSERVED
    assert projected["status"] == STATUS_PROJECTED
    assert projected["execution_phase"] == "AWAITING_INDEPENDENT_VERIFICATION"
    ticket = projected["accepted_state"]["tickets"][0]
    assert ticket["status"] == "HELD"
    assert ticket["hold_reason"] == "AWAITING_INDEPENDENT_VERIFICATION"
    assert ticket["verified"] is False
    assert ticket["closed"] is False
    assert projected["ticket_verified"] is False
    assert projected["ticket_closed"] is False
    assert projected["mission_done"] is False
    assert projected["r8_evidence_bound"] is True


def test_execution_failure_preserves_failure_and_r10_advice_without_retry(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    (world["exec_wt"] / TARGET).write_text("dirty\n", encoding="utf-8", newline="\n")
    outcome = _execute(world, handoff, update)

    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )

    assert outcome["execution_phase"] == PHASE_EXECUTION_FAILED
    assert projected["status"] == STATUS_PROJECTED
    ticket = projected["accepted_state"]["tickets"][0]
    assert ticket["status"] == "EXECUTION_FAILED"
    assert ticket["r10_repair_classification"]["repair_feedback_mode"] == "R10_CLASSIFICATION_ONLY"
    assert ticket["r10_repair_classification"]["repair_launch_allowed"] is False
    assert projected["automatic_retry"] is False


def test_uncertain_outcome_and_missing_r8_receipt_hold_without_state_corruption(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)

    uncertain = _execute(world, handoff, update, executor=lambda *args, **kwargs: {"status": "EXECUTED_OK"})
    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=uncertain,
    )

    assert uncertain["execution_phase"] == PHASE_OUTCOME_UNCERTAIN
    assert projected["status"] == STATUS_HELD
    assert projected["reason"] == "ACTION_EVIDENCE_ID_REQUIRED"
    assert projected["accepted_state"] == update["accepted_state"]


def test_forged_or_mismatched_evidence_fails_closed(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)

    forged = _plain(outcome)
    forged["mission_id"] = "mission-other"
    assert project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=forged,
    )["reason"] == "EXECUTION_MISSION_MISMATCH"

    mismatched = _plain(outcome)
    mismatched["r8_replay"]["action_evidence_id"] = "aev-" + "0" * 32
    assert project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=mismatched,
    )["reason"] == "R8_REPLAY_ACTION_EVIDENCE_MISMATCH"


def test_duplicate_identical_feedback_is_idempotent_and_conflict_holds(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)

    first = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )
    duplicate = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        prior_execution_feedback=outcome,
    )
    conflicting = _plain(outcome)
    conflicting["prepared_patch_hash"] = "f" * 64
    conflict = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=conflicting,
        prior_execution_feedback=outcome,
    )

    assert duplicate["status"] == STATUS_PROJECTED
    assert duplicate["duplicate_idempotent"] is True
    assert duplicate["budget_consumed"] == 0
    assert duplicate["accepted_state_hash"] == first["accepted_state_hash"]
    assert conflict["status"] == STATUS_HELD
    assert conflict["reason"] == "DUPLICATE_EXECUTION_FEEDBACK_CONFLICT"


def test_revoked_mandate_holds_without_corrupting_state(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)
    revoked = deepcopy(update)
    revoked["accepted_state"]["mandate_revoked"] = True

    projected = project_supervised_execution_feedback(
        mission_update=revoked,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )

    assert projected["status"] == STATUS_HELD
    assert projected["reason"] == "HUMAN_MANDATE_REVOKED"
    assert projected["accepted_state"] == revoked["accepted_state"]


def test_changed_project_head_after_valid_action_is_recorded_not_rewritten(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)

    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        observed_post_action_head="b" * 40,
    )

    assert projected["status"] == STATUS_PROJECTED
    assert projected["accepted_state"]["base_sha"] == update["accepted_state"]["base_sha"]
    assert projected["git_base_evolution"]["observed_post_action_head"] == "b" * 40
    assert projected["git_base_evolution"]["base_revalidation_required"] is True
    assert projected["accepted_state"]["observed_project_state"]["base_revalidation_required"] is True


def test_downstream_remains_blocked_before_verification_and_independent_ticket_continues(tmp_path):
    world = _world(tmp_path)
    mission = _projection(
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
            {"ticket_id": "dependent", "objective": "Depends", "status": "PENDING", "dependency_ids": ["ticket-f3b"]},
            {
                "ticket_id": "independent",
                "objective": "Independent",
                "status": "PENDING",
                "authorized_paths": [TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["independent remains available"],
            },
        ],
    )
    step = _step(world, mission)
    handoff = _handoff(world, mission_projection=mission, supervisor_step=step)
    update = __import__("obsidure_supervised_dependency_state_integration_v1").integrate_supervised_dependency_state(
        mission_projection=mission,
        supervisor_step=step,
        prepare_feedback=handoff["handoff_feedback"],
    )
    outcome = _execute(world, handoff, update)

    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
    )

    assert projected["unique_next_ticket_id"] == "independent"
    assert projected["independent_continuation"] is True
    assert any(block["ticket_id"] == "dependent" for block in projected["transitive_dependency_blocks"])


def test_checkpoint_resume_with_execution_feedback_preserves_budget_and_pending_verification(tmp_path):
    world = _world(tmp_path)
    projection, step, handoff, update = _prepared_update(world)
    outcome = _execute(world, handoff, update)

    projected = project_supervised_execution_feedback(
        mission_update=update,
        prepare_handoff_result=handoff,
        execution_outcome=outcome,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    checkpoint = projected["checkpoint"]
    restored = resume_supervised_mission_checkpoint(checkpoint["checkpoint_id"], checkpoint_store_dir=tmp_path / "checkpoints")

    assert checkpoint["checkpoint_saved"] is True
    assert restored["status"] == STATUS_RESTORED
    assert restored["budget"]["consumed_actions"] == 1
    assert restored["pending_approvals"] == []
    assert restored["restored_state"]["tickets"][0]["hold_reason"] == "AWAITING_INDEPENDENT_VERIFICATION"


def test_no_authority_no_executor_regression_in_reducer(tmp_path):
    world = _world(tmp_path)
    *_unused, projected = _feedback(world)

    assert projected["executor_invoked"] is False
    assert projected["approval_created"] is False
    assert projected["kx108_called_by_supervisor"] is False
    assert projected["binder_mutation"] is False
    assert projected["native_memory_write"] is False
    assert projected["ticket_verified"] is False
    assert projected["ticket_closed"] is False
    assert projected["mission_done"] is False
