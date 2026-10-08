from __future__ import annotations

from copy import deepcopy

from scripts.obsidure_supervised_mission_state_v1 import (
    canonical_json,
    project_supervised_mission_state,
)
from scripts.obsidure_supervised_mission_stepper_v1 import propose_supervised_mission_step
from scripts.obsidure_supervised_prepare_feedback_projection_v1 import (
    HOLD,
    PREPARED_AWAITING_APPROVAL,
    STATUS_HELD,
    STATUS_PROJECTED,
    STATUS_REJECTED,
    project_supervised_prepare_feedback,
)

BASE_SHA = "a" * 40


def _hash(value):
    import hashlib

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _mission(*, tickets=None, mandate_revoked=False, remaining_actions=3, current_head=BASE_SHA):
    return {
        "mission_id": "mission-r12-f3c",
        "human_mandate_reference": "mandate-r12-f3c",
        "repository_identity": "repo://obsidia/f3c",
        "local_root": "C:/work/repo",
        "worktree": "C:/work/repo",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": current_head,
        "original_goal": "Prepare a governed supervised mission ticket.",
        "acceptance_criteria": ["prepare feedback is projected"],
        "bounded_authorized_scope": {
            "authorized_paths": ["scripts/example.py"],
            "authorized_operations": ["MODIFY"],
        },
        "tickets": tickets
        or [
            {
                "ticket_id": "ticket-one",
                "objective": "Prepare ticket one.",
                "status": "PENDING",
                "authorized_paths": ["scripts/example.py"],
                "authorized_operations": ["MODIFY"],
                "acceptance_criteria": ["prepared only"],
                "evidence_refs": [],
                "unknowns": ["model-output-not-authority"],
            }
        ],
        "global_budget": {"remaining_actions": remaining_actions, "remaining_tickets": 2},
        "timebox": {"expired": False},
        "evidence_refs": ["mandate-evidence"],
        "explicit_unknowns": ["semantic-unknown-preserved"],
        "mission_authority": "KX108_ONLY",
        "mandate_status": "REVOKED" if mandate_revoked else "ACTIVE",
        "mandate_revoked": mandate_revoked,
        "source_ids": ["r12-f3c-test"],
    }


def _projection(mission=None, *, observed_project_head=None):
    return project_supervised_mission_state(mission or _mission(), observed_project_head=observed_project_head)


def _step(projection):
    return propose_supervised_mission_step(projection)


def _feedback(projection, step, *, outcome="R11_SELF_BUILD_PREPARED", reason="", ticket_id=None):
    proposal = step["step_proposal"]
    selected_ticket_id = ticket_id or proposal["selected_ticket_id"]
    return {
        "feedback_id": "feedback-f3c-1",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": _hash(proposal),
        "mission_id": proposal["mission_id"],
        "selected_ticket_id": selected_ticket_id,
        "mandate_reference": proposal["mandate_reference"],
        "project": dict(proposal["project"]),
        "preparation_outcome": outcome,
        "reason": reason,
        "r9_candidate_reference": {
            "r9_proposal_id": "r9-proposal-1",
            "r9_manifest_id": "r9-manifest-1",
            "r9_validation_id": "r9-validation-1",
            "r9_handoff_id": "r9-handoff-1",
            "candidate_patch_hash": "b" * 64,
        },
        "evidence_references": list(proposal["evidence_references"]) + ["inventory-1", "deficiency-1", "validation-1"],
        "prepared_action_reference": {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "execution_authority_hash": "eah-f3c-1",
            "v2_exec_id": "v2-exec-f3c-1",
            "handoff_to_governed_prepare": True,
            "executor_invoked": False,
            "physical_mutation": False,
        },
        "expected_next_state": "PREPARED_AWAITING_VALIDATED_FEEDBACK",
        "canonical_state_json": projection["canonical_state_json"],
        "preparation_is_execution": False,
        "prepared_not_verified": True,
        "prepared_not_closed": True,
        "approval_created": False,
        "kx108_called": False,
        "binder_mutation": False,
        "executor_invoked": False,
        "physical_mutation": False,
        "memory_write": False,
        "native_memory_write": False,
        "commit_created": False,
        "push_performed": False,
        "merge_performed": False,
    }


def test_valid_prepare_feedback_projects_pending_approval_without_completion():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert result["status"] == STATUS_PROJECTED
    assert result["prepare_phase_status"] == PREPARED_AWAITING_APPROVAL
    assert result["ticket_completed"] is False
    assert result["executor_invoked"] is False
    ticket = result["updated_mission_state"]["tickets"][0]
    assert ticket["status"] == "HELD"
    assert ticket["hold_reason"] == PREPARED_AWAITING_APPROVAL
    assert "r9-proposal-1" in ticket["evidence_refs"]
    assert result["reduced_projection"]["status"] == "SUPERVISED_MISSION_STATE_BLOCKED"


def test_hold_feedback_projects_ticket_hold_with_exact_reason():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step, outcome="R11_SELF_BUILD_HELD", reason="VALIDATION_EVIDENCE_REQUIRED")
    feedback["prepared_action_reference"] = {}
    feedback["r9_candidate_reference"] = {}

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert result["status"] == STATUS_PROJECTED
    assert result["prepare_phase_status"] == HOLD
    ticket = result["updated_mission_state"]["tickets"][0]
    assert ticket["status"] == "HELD"
    assert ticket["hold_reason"] == "VALIDATION_EVIDENCE_REQUIRED"


def test_forged_feedback_proposal_hash_is_rejected():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)
    feedback["proposal_hash"] = "0" * 64

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert result["status"] == STATUS_REJECTED
    assert result["reason"] == "FEEDBACK_PROPOSAL_HASH_MISMATCH"


def test_duplicate_identical_feedback_is_idempotent_and_budget_neutral():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)

    first = project_supervised_prepare_feedback(projection, step, feedback)
    second = project_supervised_prepare_feedback(projection, step, feedback, prior_prepare_feedback=feedback)

    assert first["status"] == STATUS_PROJECTED
    assert second["status"] == STATUS_PROJECTED
    assert second["duplicate_idempotent"] is True
    assert second["budget_consumed"] is False
    assert second["updated_mission_state"]["global_budget"] == first["updated_mission_state"]["global_budget"]


def test_duplicate_conflicting_feedback_is_rejected():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)
    conflicting = deepcopy(feedback)
    conflicting["r9_candidate_reference"]["candidate_patch_hash"] = "c" * 64

    result = project_supervised_prepare_feedback(projection, step, conflicting, prior_prepare_feedback=feedback)

    assert result["status"] == STATUS_REJECTED
    assert result["reason"] == "DUPLICATE_FEEDBACK_CONFLICT"


def test_revoked_mandate_is_held_before_feedback_projection():
    projection = _projection(_mission(mandate_revoked=True))
    assert projection["reason"] == "HUMAN_MANDATE_REVOKED"

    result = project_supervised_prepare_feedback(projection, {}, {})

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "HUMAN_MANDATE_REVOKED"


def test_stale_head_is_held_during_replay_validation():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = project_supervised_prepare_feedback(projection, step, feedback, observed_project_head="d" * 40)

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "PROJECT_HEAD_STALE"


def test_prepared_feedback_requires_bound_evidence_and_hashes():
    projection = _projection()
    step = _step(projection)
    feedback = _feedback(projection, step)
    feedback["evidence_references"] = ["validation-1"]

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "FEEDBACK_EVIDENCE_BINDING_MISMATCH"


def test_independent_ticket_remains_eligible_after_first_ticket_pending_approval():
    tickets = [
        {
            "ticket_id": "ticket-one",
            "objective": "Prepare ticket one.",
            "status": "PENDING",
            "authorized_paths": ["scripts/example.py"],
            "authorized_operations": ["MODIFY"],
            "acceptance_criteria": ["prepared only"],
        },
        {
            "ticket_id": "ticket-two",
            "objective": "Prepare independent ticket two.",
            "status": "PENDING",
            "authorized_paths": ["scripts/example.py"],
            "authorized_operations": ["MODIFY"],
            "acceptance_criteria": ["prepared only"],
        },
    ]
    projection = _projection(_mission(tickets=tickets))
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert result["updated_mission_state"]["tickets"][0]["status"] == "HELD"
    assert result["reduced_projection"]["status"] == "SUPERVISED_MISSION_STATE_PROJECTED"
    assert result["reduced_projection"]["unique_next_ticket_id"] == "ticket-two"


def test_source_projection_is_not_mutated_and_no_authority_side_effects():
    projection = _projection()
    original = deepcopy(projection)
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = project_supervised_prepare_feedback(projection, step, feedback)

    assert projection == original
    assert result["approval_created"] is False
    assert result["kx108_called"] is False
    assert result["binder_mutation"] is False
    assert result["native_memory_write"] is False
    assert result["prepared_promoted_to_executed"] is False
    assert result["prepared_promoted_to_verified"] is False
    assert result["prepared_promoted_to_closed"] is False
