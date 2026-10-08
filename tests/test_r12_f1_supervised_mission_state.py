from __future__ import annotations

import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidure_supervised_mission_state_v1 import (  # noqa: E402
    STATUS_BLOCKED,
    STATUS_COMPLETE,
    STATUS_HELD,
    STATUS_PROJECTED,
    STATUS_REJECTED,
    canonicalize_supervised_mission_state,
    project_supervised_mission_state,
)

BASE_SHA = "a" * 40


def _mission(**overrides):
    data = {
        "mission_id": "mission-r12-f1",
        "human_mandate_reference": "mandate-r12-f1",
        "mandate_status": "ACTIVE",
        "mission_authority": "KX108_ONLY",
        "repository_identity": "repo://obsidia-x108-proofs",
        "local_root": "C:/repo/main",
        "worktree": "C:/repo/worktree",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": BASE_SHA,
        "original_goal": "Complete a supervised local development mission.",
        "acceptance_criteria": ["all tickets verified", "final state reconciled"],
        "bounded_authorized_scope": {
            "authorized_paths": ["scripts/example.py", "tests/test_example.py"],
            "authorized_operations": ["APPLY_PATCH"],
        },
        "global_budget": {"remaining_actions": 3, "remaining_attempts": 2, "remaining_tickets": 2},
        "timebox": {"expired": False},
        "evidence_refs": ["aev-r12-f1"],
        "explicit_unknowns": ["live execution not requested"],
        "source_ids": ["r12-b4"],
        "tickets": [
            {
                "ticket_id": "ticket-a",
                "objective": "Prepare fixture A",
                "status": "COMPLETED",
                "acceptance_criteria": ["A verified"],
                "authorized_paths": ["scripts/example.py"],
                "authorized_operations": ["APPLY_PATCH"],
                "evidence_refs": ["aev-ticket-a"],
                "source_ids": ["r11-b2"],
            },
            {
                "ticket_id": "ticket-b",
                "objective": "Prepare fixture B",
                "status": "PENDING",
                "dependency_ids": ["ticket-a"],
                "acceptance_criteria": ["B verified"],
                "authorized_paths": ["tests/test_example.py"],
                "authorized_operations": ["APPLY_PATCH"],
            },
        ],
    }
    data.update(overrides)
    return data


def test_valid_two_ticket_dag_projects_unique_next():
    out = project_supervised_mission_state(_mission())

    assert out["status"] == STATUS_PROJECTED
    assert out["unique_next_ticket_id"] == "ticket-b"
    assert out["eligible_ticket_ids"] == ["ticket-b"]
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["supervisor_authority"] == "NONE"
    assert out["executor_invoked"] is False
    assert out["repair_loop_invoked"] is False
    assert out["memory_write"] is False
    assert out["network_or_model_call"] is False


def test_missing_dependency_rejected():
    mission = _mission(tickets=[{"ticket_id": "ticket-a", "status": "PENDING", "dependency_ids": ["missing"]}])

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "MISSING_DEPENDENCY"
    assert out["dependency_id"] == "missing"


def test_cyclic_dependency_rejected():
    mission = _mission(
        tickets=[
            {"ticket_id": "ticket-a", "status": "PENDING", "dependency_ids": ["ticket-b"]},
            {"ticket_id": "ticket-b", "status": "PENDING", "dependency_ids": ["ticket-a"]},
        ]
    )

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "CYCLIC_DEPENDENCY"


def test_duplicate_ticket_id_rejected():
    mission = _mission(tickets=[{"ticket_id": "ticket-a"}, {"ticket_id": "ticket-a"}])

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "DUPLICATE_TICKET_ID"


def test_invalid_mandate_holds_closed():
    out = project_supervised_mission_state(_mission(human_mandate_reference="bad mandate with spaces"))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "INVALID_HUMAN_MANDATE_REFERENCE"
    assert out["approval_created"] is False


def test_revoked_mandate_holds_closed():
    out = project_supervised_mission_state(_mission(mandate_revoked=True))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "HUMAN_MANDATE_REVOKED"
    assert out["kx108_called"] is False


def test_exhausted_budget_holds_closed():
    out = project_supervised_mission_state(_mission(global_budget={"remaining_actions": 0}))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_blocked_dependency_blocks_only_dependent_ticket():
    mission = _mission(
        tickets=[
            {"ticket_id": "ticket-a", "status": "BLOCKED", "blocked_reason": "R8_REPLAY_INCOMPLETE"},
            {"ticket_id": "ticket-b", "status": "PENDING", "dependency_ids": ["ticket-a"]},
        ]
    )

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_BLOCKED
    assert out["reason"] == "UNRESOLVED_HOLD_OR_BLOCK"
    assert out["unique_next_ticket_id"] is None
    assert out["unresolved_states"][0]["reason"] == "R8_REPLAY_INCOMPLETE"


def test_independent_ticket_eligible_while_other_branch_blocked():
    mission = _mission(
        tickets=[
            {"ticket_id": "ticket-a", "status": "BLOCKED", "blocked_reason": "DEPENDENCY_FAILED"},
            {"ticket_id": "ticket-b", "status": "PENDING", "dependency_ids": ["ticket-a"]},
            {"ticket_id": "ticket-c", "status": "PENDING"},
        ]
    )

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_PROJECTED
    assert out["unique_next_ticket_id"] == "ticket-c"
    assert out["eligible_ticket_ids"] == ["ticket-c"]
    assert out["unresolved_states"][0]["ticket_id"] == "ticket-a"


def test_stale_project_head_holds():
    out = project_supervised_mission_state(_mission(current_head="b" * 40))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "PROJECT_HEAD_STALE"
    assert out["expected_head"] == BASE_SHA


def test_missing_evidence_for_completed_ticket_holds():
    mission = _mission(tickets=[{"ticket_id": "ticket-a", "status": "COMPLETED"}])

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TICKET_EVIDENCE_REQUIRED"


def test_inconsistent_terminal_status_rejected():
    mission = _mission(tickets=[{"ticket_id": "ticket-a", "status": "COMPLETED", "evidence_refs": ["aev-a"], "blocked_reason": "also blocked"}])

    out = project_supervised_mission_state(mission)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "CONTRADICTORY_TERMINAL_STATES"


def test_deterministic_next_uses_ticket_order_not_model_choice():
    mission = _mission(
        tickets=[
            {"ticket_id": "ticket-z", "status": "PENDING"},
            {"ticket_id": "ticket-a", "status": "PENDING"},
        ]
    )

    first = project_supervised_mission_state(mission)
    second = project_supervised_mission_state(json.loads(json.dumps(mission)))

    assert first["unique_next_ticket_id"] == "ticket-z"
    assert second["unique_next_ticket_id"] == "ticket-z"
    assert first["canonical_state_json"] == second["canonical_state_json"]


def test_serialization_projection_stability_and_complete_status():
    mission = _mission(
        tickets=[
            {"ticket_id": "ticket-a", "status": "COMPLETED", "evidence_refs": ["aev-a"]},
            {"ticket_id": "ticket-b", "status": "EXECUTED_VERIFIED", "dependency_ids": ["ticket-a"], "evidence_refs": ["aev-b"]},
        ]
    )

    out = project_supervised_mission_state(mission)
    canonical = canonicalize_supervised_mission_state(out["canonical_state"])

    assert out["status"] == STATUS_COMPLETE
    assert out["unique_next_ticket_id"] is None
    assert canonical == out["canonical_state_json"]


def test_no_authority_or_execution_side_effect_fields_are_ever_promoted():
    out = project_supervised_mission_state(_mission())

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
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        assert out[key] is False
