from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
for p in (WORKTREE / "scripts", WORKTREE / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_supervised_multi_ticket_loop_v1 import (  # noqa: E402
    STATUS_LOOP_AWAITING_AUTHORIZATION,
    STATUS_LOOP_AWAITING_VERIFICATION,
    STATUS_LOOP_BUDGET_EXHAUSTED,
    STATUS_LOOP_BLOCKED,
    STATUS_LOOP_EXECUTION_HOLD,
    STATUS_LOOP_MISSION_DONE_VERIFIED,
    STATUS_LOOP_RECOVERY_HOLD,
    STATUS_LOOP_VERIFICATION_HOLD,
    run_supervised_multi_ticket_loop,
)
from obsidure_supervised_mission_state_v1 import project_supervised_mission_state  # noqa: E402
from test_r12_f3b_governed_prepare_handoff import (  # noqa: E402
    _candidate,
    _git,
    _handoff,
    _projection,
    _validation,
    _world,
    TARGET as TRACKED_TARGET,
)
from test_r12_f5c1_supervised_execution_feedback_projection import _execute  # noqa: E402
from test_r12_f5c2_independent_verification import _verification  # noqa: E402


D2_TARGET = "scratch/r12_f5d2_fixture.txt"
D2_BEFORE = 'VALUE = "old"\n'
D2_AFTER1 = D2_BEFORE + 'R12_F5D2_FIRST = "governed-action"\n'
D2_AFTER2 = D2_AFTER1 + 'R12_F5D2_SECOND = "second-governed-action"\n'


def _patch_from(before: str, after: str, rel: str = D2_TARGET) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            lineterm="\n",
        )
    )


def _two_ticket_projection(world):
    _prepare_ignored_target(world)
    return _projection(
        world,
        global_budget={"remaining_actions": 4, "remaining_attempts": 4, "remaining_tickets": 2},
        acceptance_criteria=["first ticket closed", "second ticket closed"],
        tickets=[
            {
                "ticket_id": "ticket-f3b",
                "objective": "Apply first governed patch",
                "status": "PENDING",
                "authorized_paths": [D2_TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
            },
            {
                "ticket_id": "ticket-f5d2-second",
                "objective": "Apply second governed patch after first proof",
                "status": "PENDING",
                "dependency_ids": ["ticket-f3b"],
                "authorized_paths": [D2_TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["second patch realized"],
            },
        ],
    )["canonical_state"]


def _prepare_ignored_target(world):
    info_exclude = world["main"] / ".git" / "info" / "exclude"
    text = info_exclude.read_text(encoding="utf-8") if info_exclude.exists() else ""
    if "scratch/" not in text:
        info_exclude.write_text(text + "\nscratch/\n", encoding="utf-8")
    target = world["exec_wt"] / D2_TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text(D2_BEFORE, encoding="utf-8", newline="\n")
    assert _git(world["exec_wt"], "status", "--short") == ""


def _candidate_for_ticket(world, ticket_id: str, tmp_path: Path):
    if ticket_id == "ticket-f5d2-second":
        patch_content = _patch_from(D2_AFTER1, D2_AFTER2, D2_TARGET)
        patch_path = tmp_path / "second.patch"
    else:
        patch_content = _patch_from(D2_BEFORE, D2_AFTER1, D2_TARGET)
        patch_path = tmp_path / "first.patch"
    patch_path.write_text(patch_content, encoding="utf-8", newline="\n")
    return _candidate(
        world,
        patch_path=patch_path,
        patch_content=patch_content,
        files=(D2_TARGET,),
        base_sha=world["base_sha"],
    )


def _feedback_provider(world, tmp_path: Path, *, binder_limited: bool = False, fail_execution: bool = False, omit_verification: bool = False):
    calls: list[str] = []

    def provider(current_state, step):
        ticket_id = step["selected_ticket_id"]
        calls.append(ticket_id)
        candidate = _candidate_for_ticket(world, ticket_id, tmp_path)
        mission_projection = (
            current_state
            if isinstance(current_state, dict) and isinstance(current_state.get("canonical_state"), dict)
            else project_supervised_mission_state(current_state)
        )
        handoff = _handoff(
            world,
            mission_projection=mission_projection,
            supervisor_step=step,
            phase1_candidate=candidate,
            validation_evidence=_validation(world, patch_hash=candidate["candidate_patch_hash"]),
        )
        if fail_execution and ticket_id == "ticket-f3b":
            (world["exec_wt"] / TRACKED_TARGET).write_text("dirty\n", encoding="utf-8", newline="\n")
        update = __import__("obsidure_supervised_dependency_state_integration_v1").integrate_supervised_dependency_state(
            mission_projection=mission_projection,
            supervisor_step=step,
            prepare_feedback=handoff["handoff_feedback"],
        )
        outcome = _execute(
            world,
            handoff,
            update,
            auth_ref="human-r12-f5d2-authorization-" + ticket_id,
        )
        projected = __import__("obsidure_supervised_execution_feedback_projection_v1").project_supervised_execution_feedback(
            mission_update=update,
            prepare_handoff_result=handoff,
            execution_outcome=outcome,
        )
        verification = None
        if not omit_verification:
            verification = _verification(outcome, projected)
            verification["verification_id"] = "ver-r12-f5d2-" + ticket_id
            verification["mission_acceptance_criteria_results"] = [
                {"criterion": criterion, "status": "PASS", "evidence_ref": "mission-" + str(index)}
                for index, criterion in enumerate(projected["accepted_state"].get("acceptance_criteria") or [])
            ]
            if ticket_id == "ticket-f5d2-second":
                verification["acceptance_criteria_results"] = [
                    {"criterion": "second patch realized", "status": "PASS", "evidence_ref": "second-patch-realized"}
                ]
            if binder_limited:
                verification["r8_replay"]["replay_verdict"] = "VERIFIED_WITH_LIMITS"
                verification["r8_replay"]["binder_replay_status"] = "INLINE_STATUS_ONLY"
        return {
            "prepare_handoff": handoff,
            "execution_outcome": outcome,
            "verification_evidence": verification,
        }

    provider.calls = calls
    return provider


def test_two_real_governed_ticket_executions_close_mission(tmp_path):
    world = _world(tmp_path)
    provider = _feedback_provider(world, tmp_path)

    result = run_supervised_multi_ticket_loop(
        mission_state=_two_ticket_projection(world),
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )

    assert result["status"] == STATUS_LOOP_MISSION_DONE_VERIFIED
    assert provider.calls == ["ticket-f3b", "ticket-f5d2-second"]
    assert result["real_multi_ticket_executions"] == 2
    assert result["separate_authorizations"] is True
    assert len(result["r8_receipts"]) == 2
    assert result["f5_c1_feedback_count"] == 2
    assert result["f5_c2_verification_count"] == 2
    assert result["mission_completion_proof"]["completion_proof_digest"]
    assert (world["exec_wt"] / D2_TARGET).read_text(encoding="utf-8") == D2_AFTER2
    assert result["executor_invoked"] is False
    assert result["approval_created"] is False
    assert result["binder_mutation"] is False


def test_binder_limited_proof_stays_hold_not_done(tmp_path):
    world = _world(tmp_path)
    provider = _feedback_provider(world, tmp_path, binder_limited=True)

    result = run_supervised_multi_ticket_loop(
        mission_state=_two_ticket_projection(world),
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )

    assert result["status"] == STATUS_LOOP_VERIFICATION_HOLD
    assert result["reason"] == "BINDER_DECISION_RECONSTRUCTION_REQUIRED"
    assert result["mission_completion_proof"] is None


def test_missing_authorization_and_budget_and_revocation_hold_before_execution(tmp_path):
    world = _world(tmp_path)
    state = _two_ticket_projection(world)

    missing = run_supervised_multi_ticket_loop(
        mission_state=state,
        feedback_provider=lambda _state, _step: None,
        checkpoint_store_dir=tmp_path / "checkpoints-missing",
    )
    assert missing["status"] == STATUS_LOOP_AWAITING_AUTHORIZATION

    exhausted = dict(state)
    exhausted["global_budget"] = {"remaining_actions": 0}
    assert run_supervised_multi_ticket_loop(
        mission_state=exhausted,
        feedback_provider=lambda _state, _step: None,
        checkpoint_store_dir=tmp_path / "checkpoints-budget",
    )["status"] == STATUS_LOOP_BUDGET_EXHAUSTED

    revoked = dict(state)
    revoked["mandate_revoked"] = True
    assert run_supervised_multi_ticket_loop(
        mission_state=revoked,
        feedback_provider=lambda _state, _step: None,
        checkpoint_store_dir=tmp_path / "checkpoints-revoked",
    )["status"] == STATUS_LOOP_BLOCKED


def test_execution_failure_exposes_r10_repair_without_retry(tmp_path):
    world = _world(tmp_path)
    provider = _feedback_provider(world, tmp_path, fail_execution=True)

    result = run_supervised_multi_ticket_loop(
        mission_state=_two_ticket_projection(world),
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )

    assert result["status"] == STATUS_LOOP_EXECUTION_HOLD
    outcome = result["controller_trace"]["execution_outcomes"][0]
    assert outcome["r10_repair_classification"]["repair_feedback_mode"] == "R10_CLASSIFICATION_ONLY"
    assert outcome["r10_repair_classification"]["repair_launch_allowed"] is False
    assert result["controller_trace"]["execution_outcomes"] == [outcome]
    assert provider.calls == ["ticket-f3b"]


def test_crash_resume_waits_for_verification_and_prevents_duplicate_act(tmp_path):
    world = _world(tmp_path)
    provider = _feedback_provider(world, tmp_path, omit_verification=True)

    first = run_supervised_multi_ticket_loop(
        mission_state=_two_ticket_projection(world),
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    assert first["status"] == STATUS_LOOP_AWAITING_VERIFICATION
    assert first["real_multi_ticket_executions"] == 1

    resume = run_supervised_multi_ticket_loop(
        mission_state=first["canonical_state"],
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    assert resume["status"] == STATUS_LOOP_AWAITING_VERIFICATION
    assert resume["duplicate_mutation_prevented"] is True
    assert provider.calls == ["ticket-f3b"]


def test_authorization_reuse_is_rejected_before_second_mutation(tmp_path):
    world = _world(tmp_path)
    base_provider = _feedback_provider(world, tmp_path)

    def provider(current_state, step):
        feedback = base_provider(current_state, step)
        feedback["execution_outcome"]["authority_reference"]["human_authorization_reference"] = "same-human-authorization"
        return feedback

    result = run_supervised_multi_ticket_loop(
        mission_state=_two_ticket_projection(world),
        feedback_provider=provider,
        checkpoint_store_dir=tmp_path / "checkpoints",
    )
    assert result["status"] == STATUS_LOOP_EXECUTION_HOLD
    assert result["reason"] == "AUTHORIZATION_REUSED"
    assert result["real_multi_ticket_executions"] == 1
