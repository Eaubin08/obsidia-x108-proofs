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
from obsidure_supervised_dependency_state_integration_v1 import integrate_supervised_dependency_state  # noqa: E402
from obsidure_supervised_execution_outcome_bridge_v1 import (  # noqa: E402
    HOLD_AWAITING_VALID_AUTHORIZATION,
    PHASE_EXECUTED_OBSERVED,
    PHASE_EXECUTION_FAILED,
    PHASE_OUTCOME_UNCERTAIN,
    STATUS_EXECUTION_OUTCOME,
    STATUS_HELD,
    execute_supervised_governed_ticket,
    reconcile_supervised_execution_outcome,
)
from test_r12_f3b_governed_prepare_handoff import (  # noqa: E402
    AFTER,
    TARGET,
    _handoff,
    _projection,
    _step,
    _world,
)


def _prepared_update(world):
    projection = _projection(world)
    step = _step(world, projection)
    handoff = _handoff(world, mission_projection=projection, supervisor_step=step)
    update = integrate_supervised_dependency_state(
        mission_projection=projection,
        supervisor_step=step,
        prepare_feedback=handoff["handoff_feedback"],
    )
    assert update["status"] == "R12_F4_B_DEPENDENCY_STATE_UPDATED"
    return projection, step, handoff, update


def _execute(world, handoff, update, **kwargs):
    action = handoff["r9_prepare_result"]["prepared_action"]
    return execute_supervised_governed_ticket(
        mission_update=update,
        prepare_handoff_result=handoff,
        human_authorized_execution_authority_hash=kwargs.pop("eah", action["execution_authority_hash"]),
        human_authorization_reference=kwargs.pop("auth_ref", "human-r12-f5b-authorization"),
        stores_base_dir=world["stores"],
        repo_root=world["exec_wt"],
        session_id="r12-f5b",
        **kwargs,
    )


def _plain(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def test_authorized_disposable_execution_records_r8_replay_and_reconciliation(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)

    out = _execute(world, handoff, update)

    assert out["status"] == STATUS_EXECUTION_OUTCOME
    assert out["execution_phase"] == PHASE_EXECUTED_OBSERVED
    assert out["executor_invoked"] is True
    assert out["physical_mutation"] is True
    assert out["action_evidence_id"].startswith("aev-")
    assert out["r8_replay"]["replay_verdict"] in {"VERIFIED", "VERIFIED_WITH_LIMITS"}
    assert out["realized_state_reconciliation"]["reconciliation_status"] == R8_REC.STATUS_MATCH
    assert out["pending_verification_status"] == "AWAITING_INDEPENDENT_VERIFICATION"
    assert out["ticket_verified"] is False
    assert out["ticket_closed"] is False
    assert out["mission_done"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == AFTER


def test_missing_or_wrong_approval_holds_without_executor(tmp_path):
    world = _world(tmp_path)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")
    _, _, handoff, update = _prepared_update(world)

    missing = execute_supervised_governed_ticket(
        mission_update=update,
        prepare_handoff_result=handoff,
        stores_base_dir=world["stores"],
        repo_root=world["exec_wt"],
    )
    wrong = _execute(world, handoff, update, eah="0" * 64)

    assert missing["status"] == STATUS_HELD
    assert missing["reason"] == HOLD_AWAITING_VALID_AUTHORIZATION
    assert missing["executor_invoked"] is False
    assert wrong["status"] == STATUS_HELD
    assert wrong["reason"] == HOLD_AWAITING_VALID_AUTHORIZATION
    assert wrong["executor_invoked"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_revoked_mandate_stale_head_patch_mismatch_and_exhausted_budget_hold(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)

    revoked = deepcopy(update)
    revoked["accepted_state"]["mandate_revoked"] = True
    assert _execute(world, handoff, revoked)["reason"] == "HUMAN_MANDATE_REVOKED"

    stale = _execute(world, handoff, update, observed_project_head="c" * 40)
    assert stale["status"] == STATUS_HELD
    assert stale["reason"] == "PROJECT_HEAD_STALE"

    exhausted = deepcopy(update)
    exhausted["accepted_state"]["global_budget"]["remaining_actions"] = 0
    assert _execute(world, handoff, exhausted)["reason"] == "MISSION_BUDGET_EXHAUSTED"

    mismatch = _plain(handoff)
    mismatch["handoff_feedback"]["r9_candidate_reference"]["candidate_patch_hash"] = "f" * 64
    assert _execute(world, mismatch, update)["reason"] == "PREPARED_PATCH_HASH_MISMATCH"


def test_blocked_dependency_never_enters_executor(tmp_path):
    world = _world(tmp_path)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")
    _, _, handoff, update = _prepared_update(world)
    blocked = deepcopy(update)
    blocked["transitive_dependency_blocks"] = [{"ticket_id": "ticket-f3b", "reason": "BLOCKED_BY_HOLD(upstream)"}]

    out = _execute(world, handoff, blocked)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TICKET_BLOCKED_BY_DEPENDENCY"
    assert out["executor_invoked"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_executor_failure_feedback_is_classified_without_retry(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)
    (world["exec_wt"] / TARGET).write_text("dirty\n", encoding="utf-8", newline="\n")

    out = _execute(world, handoff, update)

    assert out["status"] == STATUS_EXECUTION_OUTCOME
    assert out["execution_phase"] == PHASE_EXECUTION_FAILED
    assert out["executor_invoked"] is True
    assert out["physical_mutation"] is False
    assert out["realized_state_reconciliation"]["reconciliation_status"] == R8_REC.STATUS_NOT_REALIZED
    assert out["r10_repair_classification"]["repair_feedback_mode"] == "R10_CLASSIFICATION_ONLY"
    assert out["r10_repair_classification"]["repair_launch_allowed"] is False
    assert out["automatic_retry"] is False


def test_missing_r8_receipt_is_uncertain_hold(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)

    def fake_executor(*args, **kwargs):
        return {"status": "EXECUTED_OK", "reason": None}

    out = _execute(world, handoff, update, executor=fake_executor)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSING_R8_RECEIPT"
    assert out["execution_phase"] == PHASE_OUTCOME_UNCERTAIN
    assert out["executor_invoked"] is True


def test_contradictory_realized_state_holds_during_recovered_reconciliation(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)
    first = _execute(world, handoff, update)
    receipt_path = world["stores"] / "receipts" / f"{first['action_evidence_id']}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["realized_state"]["post_state_ref"]["after_digests"][TARGET] = "0" * 64
    receipt_path.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")

    recovered = reconcile_supervised_execution_outcome(
        mission_update=update,
        prepare_handoff_result=handoff,
        action_evidence_id=first["action_evidence_id"],
        stores_base_dir=world["stores"],
    )

    assert recovered["status"] == STATUS_HELD
    assert recovered["execution_phase"] == PHASE_OUTCOME_UNCERTAIN
    assert recovered["reason"].startswith("R8_REPLAY_NOT_VERIFIED") or recovered["reason"].startswith("R8_RECONCILIATION")


def test_duplicate_execution_attempt_requires_reconciliation_no_replay(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)
    first = _execute(world, handoff, update)

    duplicate = _execute(world, handoff, update, prior_execution_outcome=first)

    assert duplicate["status"] == STATUS_HELD
    assert duplicate["reason"] == "DUPLICATE_EXECUTION_ATTEMPT_REQUIRES_RECONCILIATION"
    assert duplicate["executor_invoked"] is False


def test_no_authority_escalation_regression(tmp_path):
    world = _world(tmp_path)
    _, _, handoff, update = _prepared_update(world)
    out = _execute(world, handoff, update)

    for key in (
        "approval_created_by_supervisor",
        "authorization_inferred",
        "binder_mutation",
        "memory_write",
        "native_memory_write",
        "automatic_retry",
        "repair_loop_invoked",
        "ticket_verified",
        "ticket_closed",
        "mission_done",
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        assert out[key] is False
