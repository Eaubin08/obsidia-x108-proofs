from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
for p in (WORKTREE, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_supervised_mission_state_v1 import project_supervised_mission_state  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import (  # noqa: E402
    REQUESTED_OPERATION,
    STATUS_HELD,
    STATUS_PROPOSED,
    STATUS_REJECTED,
    propose_supervised_mission_step,
)

BASE_SHA = "e" * 40


def _mission(**overrides):
    data = {
        "mission_id": "mission-r12-f3a",
        "human_mandate_reference": "mandate-r12-f3a",
        "mandate_status": "ACTIVE",
        "mission_authority": "KX108_ONLY",
        "repository_identity": "repo://obsidia-x108-proofs",
        "local_root": "C:/repo/main",
        "worktree": "C:/repo/worktree",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": BASE_SHA,
        "original_goal": "Supervise one prepare-only developer mission step.",
        "acceptance_criteria": ["a step proposal is produced", "no execution occurs"],
        "bounded_authorized_scope": {
            "authorized_paths": ["scripts/f3a.py", "tests/test_f3a.py"],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
        },
        "global_budget": {"remaining_actions": 3, "remaining_attempts": 2, "remaining_tickets": 2},
        "timebox": {"expired": False},
        "evidence_refs": ["model-evidence-r12-f3a", "mission-candidate-r12-f3a"],
        "explicit_unknowns": ["human review still required"],
        "source_ids": ["r12-f2"],
        "tickets": [
            {
                "ticket_id": "ticket-a",
                "objective": "Prepare source change",
                "status": "COMPLETED",
                "authorized_paths": ["scripts/f3a.py"],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["source prepared"],
                "evidence_refs": ["aev-ticket-a"],
            },
            {
                "ticket_id": "ticket-b",
                "objective": "Prepare regression test",
                "status": "PENDING",
                "dependency_ids": ["ticket-a"],
                "authorized_paths": ["tests/test_f3a.py"],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["test prepared"],
                "unknowns": ["test name not final"],
            },
        ],
    }
    data.update(overrides)
    return data


def _projection(**overrides):
    return project_supervised_mission_state(_mission(**overrides))


def test_two_ticket_progression_proposes_prepare_only_step():
    projection = _projection()

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_PROPOSED
    assert out["selected_ticket_id"] == "ticket-b"
    proposal = out["step_proposal"]
    assert proposal["mission_id"] == "mission-r12-f3a"
    assert proposal["selected_ticket_id"] == "ticket-b"
    assert proposal["project"]["base_sha"] == BASE_SHA
    assert proposal["dependency_references"] == [
        {"dependency_id": "ticket-a", "status": "COMPLETED", "evidence_refs": ["aev-ticket-a"]}
    ]
    assert proposal["mandate_reference"] == "mandate-r12-f3a"
    assert proposal["requested_operation"] == REQUESTED_OPERATION
    assert proposal["budget_available"]["remaining_actions"] == 3
    assert "human review still required" in proposal["semantic_unknowns"]
    assert "test name not final" in proposal["semantic_unknowns"]
    assert proposal["expected_next_state"]["to_status"] == "PREPARED_AWAITING_VALIDATED_FEEDBACK"
    assert proposal["proposal_does_not_complete_ticket"] is True
    assert proposal["ticket_completed"] is False


def test_deterministic_next_and_duplicate_proposal_are_idempotent():
    projection = _projection(
        tickets=[
            {"ticket_id": "ticket-z", "objective": "Z", "status": "PENDING"},
            {"ticket_id": "ticket-a", "objective": "A", "status": "PENDING"},
        ]
    )

    first = propose_supervised_mission_step(projection)
    second = propose_supervised_mission_step(json.loads(json.dumps(projection)), prior_step_proposal=first["step_proposal"])

    assert first["status"] == STATUS_PROPOSED
    assert first["selected_ticket_id"] == "ticket-z"
    assert first["step_proposal"]["proposal_id"] == second["step_proposal"]["proposal_id"]
    assert second["duplicate_of_prior_proposal"] is True
    assert first["canonical_state_json_before"] == second["canonical_state_json_before"]


def test_blocked_ticket_preserves_independent_eligible_ticket():
    projection = _projection(
        tickets=[
            {"ticket_id": "ticket-a", "objective": "A", "status": "BLOCKED", "blocked_reason": "UPSTREAM_HOLD"},
            {"ticket_id": "ticket-b", "objective": "B", "status": "PENDING", "dependency_ids": ["ticket-a"]},
            {"ticket_id": "ticket-c", "objective": "C", "status": "PENDING"},
        ]
    )

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_PROPOSED
    assert out["selected_ticket_id"] == "ticket-c"
    assert out["step_proposal"]["dependency_references"] == []
    assert out["ticket_completed"] is False


def test_exhausted_budget_holds_closed():
    projection = _projection(global_budget={"remaining_actions": 0})

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_BUDGET_EXHAUSTED"
    assert out["executor_invoked"] is False


def test_revoked_mandate_holds_closed():
    projection = _projection(mandate_revoked=True)

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "HUMAN_MANDATE_REVOKED"
    assert out["approval_created"] is False


def test_stale_head_holds_closed():
    projection = _projection()

    out = propose_supervised_mission_step(projection, observed_project_head="f" * 40)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "PROJECT_HEAD_STALE"
    assert out["projection"]["expected_head"] == BASE_SHA


def test_missing_required_evidence_holds_before_step():
    projection = _projection(evidence_refs=[])

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_EVIDENCE_REQUIRED"
    assert out["step_proposal"] is None


def test_malformed_feedback_holds_and_does_not_update_state():
    projection = _projection()

    out = propose_supervised_mission_step(projection, feedback={"status": "PASS"})

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MALFORMED_FEEDBACK"
    assert out["ticket_completed"] is False


def test_ambiguous_or_missing_next_ticket_holds_closed():
    projection = _projection()
    projection = dict(projection)
    projection["unique_next_ticket_id"] = None

    out = propose_supervised_mission_step(projection)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "NO_UNIQUE_NEXT_TICKET"


def test_missing_dependency_and_conflicting_state_are_rejected_by_f1():
    missing = _projection(tickets=[{"ticket_id": "ticket-a", "status": "PENDING", "dependency_ids": ["missing"]}])
    conflict = _projection(
        tickets=[
            {
                "ticket_id": "ticket-a",
                "status": "COMPLETED",
                "blocked_reason": "also blocked",
                "evidence_refs": ["aev-a"],
            }
        ]
    )

    missing_out = propose_supervised_mission_step(missing)
    conflict_out = propose_supervised_mission_step(conflict)

    assert missing_out["status"] == STATUS_REJECTED
    assert missing_out["reason"] == "MISSING_DEPENDENCY"
    assert conflict_out["status"] == STATUS_HELD
    assert conflict_out["reason"] == "CONTRADICTORY_TERMINAL_STATES"


def test_projection_immutability_no_completion_or_side_effects():
    projection = _projection()
    before = copy.deepcopy(projection)

    out = propose_supervised_mission_step(projection)

    assert projection == before
    assert out["state_immutable"] is True
    assert out["canonical_state_json_before"] == out["canonical_state_json_after"]
    for key in (
        "approval_created",
        "kx108_called",
        "binder_mutation",
        "executor_invoked",
        "repair_loop_invoked",
        "filesystem_execution",
        "network_or_model_call",
        "memory_write",
        "native_memory_write",
        "ticket_completed",
        "commit_created",
        "push_performed",
        "merge_performed",
        "autonomous_loop",
    ):
        assert out[key] is False
        assert out["step_proposal"][key] is False
