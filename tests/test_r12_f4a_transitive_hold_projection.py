from __future__ import annotations

from scripts.obsidure_supervised_mission_stepper_v1 import STATUS_HELD as F3A_HELD
from scripts.obsidure_supervised_mission_stepper_v1 import STATUS_PROPOSED, propose_supervised_mission_step
from scripts.obsidure_transitive_hold_projection_v1 import (
    DEFECT_OPEN,
    STATUS_HELD,
    STATUS_PROJECTED,
    project_transitive_dependency_blocks,
)

BASE_SHA = "a" * 40


def _ticket(ticket_id, *, deps=(), status="PENDING", evidence=(), hold_reason="", blocked_reason="", exceptions=()):
    ticket = {
        "ticket_id": ticket_id,
        "objective": f"Do {ticket_id}",
        "dependency_ids": list(deps),
        "status": status,
        "authorized_paths": ["scripts/example.py"],
        "authorized_operations": ["MODIFY"],
        "acceptance_criteria": ["prepared only"],
        "evidence_refs": list(evidence),
        "hold_reason": hold_reason,
        "blocked_reason": blocked_reason,
    }
    if exceptions:
        ticket["dependency_exceptions"] = list(exceptions)
    return ticket


def _mission(tickets):
    return {
        "mission_id": "mission-r12-f4a",
        "human_mandate_reference": "mandate-r12-f4a",
        "repository_identity": "repo://obsidia/f4a",
        "local_root": "C:/work/repo",
        "worktree": "C:/work/repo",
        "branch": "build/openjarvis-full-install",
        "base_sha": BASE_SHA,
        "current_head": BASE_SHA,
        "original_goal": "Project supervised transitive dependency blocks.",
        "acceptance_criteria": ["transitive blockers are deterministic"],
        "bounded_authorized_scope": {
            "authorized_paths": ["scripts/example.py"],
            "authorized_operations": ["MODIFY"],
        },
        "tickets": tickets,
        "global_budget": {"remaining_actions": 5, "remaining_tickets": 5},
        "timebox": {"expired": False},
        "evidence_refs": ["mandate-evidence"],
        "explicit_unknowns": ["dependency-root-preserved"],
        "mission_authority": "KX108_ONLY",
        "mandate_status": "ACTIVE",
        "source_ids": ["r12-f4a-test"],
    }


def _valid_exception(dep_id="a"):
    return {
        "dependency_id": dep_id,
        "classification": "DEFERRED_NON_BLOCKING",
        "evidence_refs": ["fail-closed-proof-1"],
        "fail_closed_contract_id": "contract-non-consuming-a",
        "does_not_consume_unresolved_assumption": True,
        "tested": True,
        "sufficient": True,
    }


def test_direct_hold_propagates_to_dependent_ticket():
    projection = project_transitive_dependency_blocks(
        _mission([_ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"), _ticket("b", deps=["a"])])
    )

    assert projection["status"] == STATUS_PROJECTED
    assert projection["f1_projection_status"] == "SUPERVISED_MISSION_STATE_BLOCKED"
    assert projection["unique_next_ticket_id"] is None
    assert projection["transitive_dependency_blocks"][0]["reason"] == "BLOCKED_BY_HOLD(a)"
    assert projection["transitive_dependency_blocks"][0]["chain"] == ["b", "a"]


def test_multi_level_transitive_hold_preserves_root_cause_chain():
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", deps=["a"]),
            _ticket("c", deps=["b"]),
        ])
    )

    c_block = next(block for block in projection["transitive_dependency_blocks"] if block["ticket_id"] == "c")
    assert c_block["reason"] == "BLOCKED_BY_DEPENDENCY(b <- a)"
    assert c_block["chain"] == ["c", "b", "a"]
    assert c_block["root_classification"] == "HOLD"


def test_defect_open_propagates_without_becoming_pass():
    projection = project_transitive_dependency_blocks(
        _mission([_ticket("a", status="BLOCKED", blocked_reason="DEFECT_OPEN:compile"), _ticket("b", deps=["a"])])
    )

    assert projection["dependency_classifications"]["a"] == DEFECT_OPEN
    assert projection["defect_propagation"] is True
    assert projection["transitive_dependency_blocks"][0]["reason"] == "BLOCKED_BY_DEFECT_OPEN(a)"


def test_independent_ticket_continues_when_another_branch_is_blocked():
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", deps=["a"]),
            _ticket("d"),
        ])
    )

    assert projection["f1_projection_status"] == "SUPERVISED_MISSION_STATE_PROJECTED"
    assert projection["unique_next_ticket_id"] == "d"
    assert projection["eligible_ticket_ids"] == ["d"]
    assert projection["independent_continuation"] is True


def test_fail_closed_exception_allows_dependent_ticket_with_evidence():
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", deps=["a"], exceptions=[_valid_exception("a")]),
        ])
    )

    assert projection["f1_projection_status"] == "SUPERVISED_MISSION_STATE_PROJECTED"
    assert projection["unique_next_ticket_id"] == "b"
    assert projection["transitive_dependency_blocks"] == []


def test_fail_closed_exception_without_evidence_holds_closed():
    exception = _valid_exception("a")
    exception["evidence_refs"] = []
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", deps=["a"], exceptions=[exception]),
        ])
    )

    assert projection["status"] == STATUS_HELD
    assert projection["reason"] == "FAIL_CLOSED_EXCEPTION_EVIDENCE_REQUIRED"


def test_downstream_green_test_does_not_override_upstream_defect():
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="BLOCKED", blocked_reason="DEFECT_OPEN:compile"),
            _ticket("b", deps=["a"], status="PASS", evidence=["green-tests-b"]),
            _ticket("c", deps=["b"]),
        ])
    )

    b_block = next(block for block in projection["transitive_dependency_blocks"] if block["ticket_id"] == "b")
    c_block = next(block for block in projection["transitive_dependency_blocks"] if block["ticket_id"] == "c")
    assert b_block["root_ticket_id"] == "a"
    assert c_block["reason"] == "BLOCKED_BY_DEPENDENCY(b <- a)"
    assert projection["unique_next_ticket_id"] is None


def test_multiple_blocking_ancestors_are_stable_and_deterministic():
    projection1 = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", status="BLOCKED", blocked_reason="DEFECT_OPEN:runtime"),
            _ticket("c", deps=["b", "a"]),
        ])
    )
    projection2 = project_transitive_dependency_blocks(_mission(projection1["canonical_state"]["tickets"]))

    c_blocks = [block for block in projection1["transitive_dependency_blocks"] if block["ticket_id"] == "c"]
    assert [block["root_ticket_id"] for block in c_blocks] == ["a", "b"]
    assert projection1["transitive_dependency_blocks"] == projection2["transitive_dependency_blocks"]


def test_blocked_ticket_is_not_prepared_by_f3a_stepper():
    projection = project_transitive_dependency_blocks(
        _mission([_ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"), _ticket("b", deps=["a"])])
    )

    step = propose_supervised_mission_step(projection)

    assert step["status"] == F3A_HELD
    assert step["step_proposal"] is None
    assert step["executor_invoked"] is False


def test_f3a_selects_independent_ticket_not_blocked_dependent():
    projection = project_transitive_dependency_blocks(
        _mission([
            _ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"),
            _ticket("b", deps=["a"]),
            _ticket("d"),
        ])
    )

    step = propose_supervised_mission_step(projection)

    assert step["status"] == STATUS_PROPOSED
    assert step["selected_ticket_id"] == "d"
    assert step["step_proposal"]["executor_invoked"] is False
    assert step["step_proposal"]["kx108_called"] is False


def test_no_authority_or_side_effects_are_created():
    projection = project_transitive_dependency_blocks(
        _mission([_ticket("a", status="HELD", hold_reason="NEEDS_HUMAN"), _ticket("b", deps=["a"]), _ticket("d")])
    )

    assert projection["approval_created"] is False
    assert projection["kx108_called"] is False
    assert projection["binder_mutation"] is False
    assert projection["executor_invoked"] is False
    assert projection["native_memory_write"] is False
    assert projection["push_performed"] is False
    assert projection["merge_performed"] is False
