from __future__ import annotations

from copy import deepcopy
import hashlib

from scripts.obsidure_supervised_dependency_state_integration_v1 import (
    STATUS_HELD,
    STATUS_UPDATED,
    integrate_supervised_dependency_state,
)
from scripts.obsidure_supervised_mission_state_v1 import canonical_json, project_supervised_mission_state
from scripts.obsidure_supervised_mission_stepper_v1 import propose_supervised_mission_step
from scripts.obsidure_transitive_hold_projection_v1 import project_transitive_dependency_blocks

BASE_SHA = "a" * 40


def _hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _ticket(ticket_id, *, deps=(), status="PENDING", evidence=(), hold_reason="", blocked_reason=""):
    return {
        "ticket_id": ticket_id,
        "objective": f"Prepare {ticket_id}",
        "dependency_ids": list(deps),
        "status": status,
        "authorized_paths": ["scripts/example.py"],
        "authorized_operations": ["MODIFY"],
        "acceptance_criteria": ["prepared only"],
        "evidence_refs": list(evidence),
        "unknowns": ["unknown-preserved"],
        "hold_reason": hold_reason,
        "blocked_reason": blocked_reason,
    }


def _mission(tickets, *, revoked=False, remaining_actions=5, current_head=BASE_SHA):
    return {
        "mission_id": "mission-r12-f4b",
        "human_mandate_reference": "mandate-r12-f4b",
        "repository_identity": "repo://obsidia/f4b",
        "local_root": "C:/work/repo",
        "worktree": "C:/work/repo",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": current_head,
        "original_goal": "Integrate supervised dependency state.",
        "acceptance_criteria": ["dependency state is refreshed"],
        "bounded_authorized_scope": {"authorized_paths": ["scripts/example.py"], "authorized_operations": ["MODIFY"]},
        "tickets": tickets,
        "global_budget": {"remaining_actions": remaining_actions, "remaining_tickets": 5},
        "timebox": {"expired": False},
        "evidence_refs": ["mandate-evidence"],
        "explicit_unknowns": ["semantic-unknown-preserved"],
        "mission_authority": "KX108_ONLY",
        "mandate_status": "REVOKED" if revoked else "ACTIVE",
        "mandate_revoked": revoked,
        "source_ids": ["r12-f4b-test"],
    }


def _projection(mission):
    return project_supervised_mission_state(mission)


def _step(projection):
    return propose_supervised_mission_step(projection)


def _feedback(projection, step, *, suffix="1"):
    proposal = step["step_proposal"]
    return {
        "feedback_id": f"feedback-f4b-{suffix}",
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": _hash(proposal),
        "mission_id": proposal["mission_id"],
        "selected_ticket_id": proposal["selected_ticket_id"],
        "mandate_reference": proposal["mandate_reference"],
        "project": dict(proposal["project"]),
        "preparation_outcome": "R11_SELF_BUILD_PREPARED",
        "r9_candidate_reference": {
            "r9_proposal_id": f"r9-proposal-{suffix}",
            "r9_manifest_id": f"r9-manifest-{suffix}",
            "r9_validation_id": f"r9-validation-{suffix}",
            "r9_handoff_id": f"r9-handoff-{suffix}",
            "candidate_patch_hash": "b" * 64,
        },
        "evidence_references": list(proposal["evidence_references"]) + [f"validation-{suffix}"],
        "prepared_action_reference": {
            "status": "PREPARED_AWAITING_HUMAN_APPROVAL",
            "execution_authority_hash": f"eah-f4b-{suffix}",
            "v2_exec_id": f"v2-exec-f4b-{suffix}",
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


def test_valid_feedback_refreshes_dependencies_and_independent_next():
    mission = _mission([_ticket("a"), _ticket("b", deps=["a"]), _ticket("c", deps=["b"]), _ticket("d")])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step=step, prepare_feedback=feedback)

    assert result["status"] == STATUS_UPDATED
    assert result["mission_update_accepted"] is True
    assert result["dependency_projection_refreshed"] is True
    assert result["unique_next_ticket_id"] == "d"
    assert result["independent_continuation"] is True
    blocks = result["transitive_dependency_blocks"]
    assert any(block["ticket_id"] == "b" and block["reason"] == "BLOCKED_BY_HOLD(a)" for block in blocks)
    assert any(block["ticket_id"] == "c" and block["reason"] == "BLOCKED_BY_DEPENDENCY(b <- a)" for block in blocks)


def test_unresolved_hold_keeps_descendants_blocked():
    mission = _mission([_ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"), _ticket("b", deps=["a"]), _ticket("d")])
    dependency_projection = project_transitive_dependency_blocks(mission)

    assert dependency_projection["unique_next_ticket_id"] == "d"
    assert dependency_projection["transitive_dependency_blocks"][0]["reason"] == "BLOCKED_BY_HOLD(a)"


def test_resolved_hold_with_fresh_valid_evidence_unblocks_dependent_ticket():
    mission = _mission([_ticket("a", status="PASS", evidence=["fresh-receipt-a"]), _ticket("b", deps=["a"])])
    dependency_projection = project_transitive_dependency_blocks(mission)

    assert dependency_projection["unique_next_ticket_id"] == "b"
    assert dependency_projection["transitive_dependency_blocks"] == []


def test_missing_upstream_evidence_does_not_unblock_dependency():
    mission = _mission([_ticket("a", status="PASS"), _ticket("b", deps=["a"])])
    dependency_projection = project_transitive_dependency_blocks(mission)

    assert dependency_projection["status"].endswith("HELD")
    assert dependency_projection["reason"] == "TICKET_EVIDENCE_REQUIRED"


def test_revoked_mandate_holds_without_corrupting_state():
    mission = _mission([_ticket("a"), _ticket("d")], revoked=True)
    projection = _projection(mission)

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step={}, prepare_feedback={})

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "HUMAN_MANDATE_REVOKED"
    assert result["mission_update_accepted"] is False


def test_exhausted_budget_holds_without_update():
    mission = _mission([_ticket("a")], remaining_actions=0)
    projection = _projection(mission)

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step={}, prepare_feedback={})

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_stale_base_sha_holds_and_preserves_original_state():
    mission = _mission([_ticket("a"), _ticket("d")])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=feedback,
        observed_project_head="c" * 40,
    )

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "PROJECT_HEAD_STALE"
    assert result["accepted_state"] == projection["canonical_state"]


def test_duplicate_feedback_is_idempotent():
    mission = _mission([_ticket("a"), _ticket("d")])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)

    first = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step=step, prepare_feedback=feedback)
    second = integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=feedback,
        prior_prepare_feedback=feedback,
    )

    assert first["status"] == STATUS_UPDATED
    assert second["status"] == STATUS_UPDATED
    assert second["duplicate_idempotent"] is True
    assert second["accepted_state_hash"] == first["accepted_state_hash"]


def test_conflicting_feedback_holds_without_corrupting_accepted_state():
    mission = _mission([_ticket("a"), _ticket("d")])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)
    conflicting = deepcopy(feedback)
    conflicting["r9_candidate_reference"]["candidate_patch_hash"] = "c" * 64

    result = integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=conflicting,
        prior_prepare_feedback=feedback,
    )

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "DUPLICATE_FEEDBACK_CONFLICT"
    assert result["accepted_state"] == projection["canonical_state"]


def test_forged_feedback_holds_without_update():
    mission = _mission([_ticket("a"), _ticket("d")])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)
    feedback["proposal_hash"] = "0" * 64

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step=step, prepare_feedback=feedback)

    assert result["status"] == STATUS_HELD
    assert result["reason"] == "FEEDBACK_PROPOSAL_HASH_MISMATCH"
    assert result["mission_update_accepted"] is False


def test_blocked_ticket_never_enters_prepare():
    mission = _mission([_ticket("a"), _ticket("b", deps=["a"]), _ticket("c", deps=["b"])])
    projection = _projection(mission)
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step=step, prepare_feedback=feedback)

    assert result["unique_next_ticket_id"] is None
    assert result["prepare_available"] is False
    assert result["next_step"]["status"] != "R12_F3_A_SUPERVISOR_STEP_PROPOSED"
    assert result["blocked_descendant_prepared"] is False


def test_canonical_state_is_immutable_and_no_authority_created():
    mission = _mission([_ticket("a"), _ticket("d")])
    projection = _projection(mission)
    original = deepcopy(projection)
    step = _step(projection)
    feedback = _feedback(projection, step)

    result = integrate_supervised_dependency_state(mission_projection=projection, supervisor_step=step, prepare_feedback=feedback)

    assert projection == original
    assert result["original_mandate_preserved"] is True
    assert result["acceptance_criteria_preserved"] is True
    assert result["semantic_unknowns_preserved"] is True
    assert result["approval_created"] is False
    assert result["kx108_called"] is False
    assert result["binder_mutation"] is False
    assert result["executor_invoked"] is False
    assert result["native_memory_write"] is False
    assert result["push_performed"] is False
    assert result["merge_performed"] is False
