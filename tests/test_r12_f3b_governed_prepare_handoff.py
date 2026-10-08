from __future__ import annotations

import difflib
import hashlib
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
for p in (WORKTREE, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL  # noqa: E402
from obsidure_supervised_mission_state_v1 import project_supervised_mission_state  # noqa: E402
from obsidure_supervised_mission_stepper_v1 import propose_supervised_mission_step  # noqa: E402
from obsidure_supervised_prepare_handoff_v1 import (  # noqa: E402
    EXPECTED_NEXT_STATE,
    STATUS_HELD,
    STATUS_PREPARED,
    STATUS_REJECTED,
    prepare_supervised_mission_handoff,
)

TARGET = "scripts/r12_f3b_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nR12_F3B = "prepare-only"\n'


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _patch(rel: str = TARGET, after: str = AFTER) -> str:
    return "".join(
        difflib.unified_diff(
            BEFORE.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            lineterm="\n",
        )
    )


def _world(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "config", "core.autocrlf", "false")
    _git(main, "config", "user.email", "r12f3b@test.com")
    _git(main, "config", "user.name", "r12f3b")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r12-f3b-branch"
    _git(main, "worktree", "add", str(exec_wt), "-b", branch, base_sha)
    patch_dir = tmp_path / "phase1"
    patch_dir.mkdir()
    patch_path = patch_dir / "candidate.patch"
    patch_content = _patch()
    patch_path.write_text(patch_content, encoding="utf-8", newline="\n")
    return {
        "main": main,
        "exec_wt": exec_wt,
        "branch": branch,
        "base_sha": base_sha,
        "stores": tmp_path / "stores",
        "patch_path": patch_path,
        "patch_content": patch_content,
    }


def _candidate(world, *, patch_path=None, patch_content=None, files=(TARGET,), base_sha=None, status="PLAN_PROPOSED"):
    patch_content = patch_content if patch_content is not None else Path(patch_path or world["patch_path"]).read_text(encoding="utf-8")
    return {
        "session_id": "r12f3b",
        "session_contract": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": status,
        "targets": list(files),
        "candidate_patch_hash": _sha(patch_content),
        "candidate_files": list(files),
        "plan": {
            "status": status,
            "base_sha": base_sha or world["base_sha"],
            "scope_mode": "EXPLICIT_CHILD_TARGET",
            "candidate_patch_hash": _sha(patch_content),
            "candidate_patch_files": list(files),
            "candidate_patch_source": str(patch_path or world["patch_path"]),
            "display_objective": "Prepare R12-F3-B governed handoff fixture",
            "human_approval_required": True,
        },
        "producer_authority": "NONE",
        "backend_authority": "NONE",
        "decision_authority": "KX108_ONLY",
        "phase2_executed": False,
        "human_approval_synthesized": False,
        "approval_token_exposed": False,
        "repo_mutation": False,
        "mutated_repo": False,
        "world_action": False,
    }


def _mission(world, **overrides):
    data = {
        "mission_id": "mission-r12-f3b",
        "human_mandate_reference": "mandate-r12-f3b",
        "mandate_status": "ACTIVE",
        "mission_authority": "KX108_ONLY",
        "repository_identity": "repo://r12-f3b-disposable",
        "local_root": str(world["main"]),
        "worktree": str(world["exec_wt"]),
        "branch": world["branch"],
        "base_sha": world["base_sha"],
        "current_head": world["base_sha"],
        "original_goal": "Prepare one governed handoff from a supervised mission ticket.",
        "acceptance_criteria": ["prepare handoff is produced", "no execution occurs"],
        "bounded_authorized_scope": {
            "authorized_paths": [TARGET],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
        },
        "global_budget": {"remaining_actions": 2, "remaining_attempts": 2, "remaining_tickets": 1},
        "timebox": {"expired": False},
        "evidence_refs": ["model-evidence-r12-f3b", "mission-candidate-r12-f3b"],
        "explicit_unknowns": ["human approval still required"],
        "source_ids": ["r12-f3a"],
        "tickets": [
            {
                "ticket_id": "ticket-f3b",
                "objective": "Prepare governed patch handoff",
                "status": "PENDING",
                "authorized_paths": [TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
                "unknowns": ["execution not authorized"],
            }
        ],
    }
    data.update(overrides)
    return data


def _projection(world, **overrides):
    return project_supervised_mission_state(_mission(world, **overrides))


def _step(world, projection=None):
    return propose_supervised_mission_step(projection or _projection(world))


def _inventory():
    return {"inventory_snapshot_id": "inv-r12-f3b", "status": "VERIFIED", "capabilities": ["OBSIDIA_NATIVE_SELF_BUILD_PHASE1"]}


def _deficiency():
    return {"deficiency_evidence_id": "def-r12-f3b", "status": "VERIFIED", "summary": "supervised ticket requires prepare handoff"}


def _validation(world, *, patch_hash=None):
    return {"validation_evidence_id": "val-r12-f3b", "status": "PASS", "candidate_patch_hash": patch_hash or _sha(world["patch_content"]), "tests": ["r12-f3b-contract"]}


def _handoff(world, **overrides):
    projection = overrides.pop("mission_projection", _projection(world))
    step = overrides.pop("supervisor_step", _step(world, projection))
    candidate = overrides.pop("phase1_candidate", _candidate(world))
    return prepare_supervised_mission_handoff(
        supervisor_step=step,
        mission_projection=projection,
        phase1_candidate=candidate,
        inventory_snapshot=overrides.pop("inventory_snapshot", _inventory()),
        deficiency_evidence=overrides.pop("deficiency_evidence", _deficiency()),
        validation_evidence=overrides.pop("validation_evidence", _validation(world, patch_hash=candidate["candidate_patch_hash"])),
        stores_base_dir=world["stores"],
        session_id="r12-f3b",
        **overrides,
    )


def test_valid_proposal_reaches_r9_prepare_only(tmp_path):
    world = _world(tmp_path)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _handoff(world)

    assert out["status"] == STATUS_PREPARED
    assert out["prepare_handoff"] is True
    assert out["r9_prepare_result"]["status"] == "R11_SELF_BUILD_PREPARED"
    assert out["r9_prepare_result"]["prepared_action"]["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["r9_prepare_result"]["prepared_action"]["executor_invoked"] is False
    assert out["r9_prepare_result"]["prepared_action"]["physical_mutation"] is False
    assert out["handoff_feedback"]["expected_next_state"] == EXPECTED_NEXT_STATE
    assert out["handoff_feedback"]["prepared_not_verified"] is True
    assert out["handoff_feedback"]["prepared_not_closed"] is True
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["mission_executed"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_wrong_ticket_id_wrong_mandate_and_stale_base_reject_or_hold(tmp_path):
    world = _world(tmp_path)
    step = _step(world)
    wrong_ticket = dict(step)
    wrong_ticket["step_proposal"] = dict(step["step_proposal"])
    wrong_ticket["step_proposal"]["selected_ticket_id"] = "ticket-other"
    out = _handoff(world, supervisor_step=wrong_ticket)
    assert out["status"] == STATUS_REJECTED
    assert out["reason"].startswith("SUPERVISOR_PROPOSAL_BINDING_MISMATCH")

    wrong_mandate = dict(step)
    wrong_mandate["step_proposal"] = dict(step["step_proposal"])
    wrong_mandate["step_proposal"]["mandate_reference"] = "mandate-other"
    out = _handoff(world, supervisor_step=wrong_mandate)
    assert out["status"] == STATUS_REJECTED
    assert out["reason"].startswith("SUPERVISOR_PROPOSAL_BINDING_MISMATCH")

    stale = _projection(world, current_head="f" * 40)
    out = _handoff(world, mission_projection=stale, supervisor_step=_step(world, stale))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "PROJECT_HEAD_STALE"


def test_revoked_mandate_and_exhausted_budget_hold(tmp_path):
    world = _world(tmp_path)
    revoked = _projection(world, mandate_revoked=True)
    out = _handoff(world, mission_projection=revoked, supervisor_step=_step(world, revoked))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "HUMAN_MANDATE_REVOKED"

    exhausted = _projection(world, global_budget={"remaining_actions": 0})
    out = _handoff(world, mission_projection=exhausted, supervisor_step=_step(world, exhausted))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_missing_r9_evidence_and_prepare_failure_report_exact_hold(tmp_path):
    world = _world(tmp_path)

    out = _handoff(world, validation_evidence=None)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "VALIDATION_EVIDENCE_REQUIRED"
    assert out["prepare_handoff"] is False
    assert out["executor_invoked"] is False

    bad = _validation(world, patch_hash="f" * 64)
    out = _handoff(world, validation_evidence=bad)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "VALIDATION_EVIDENCE_PATCH_HASH_MISMATCH"


def test_duplicate_and_forged_feedback_are_rejected(tmp_path):
    world = _world(tmp_path)
    first = _handoff(world)

    dup = _handoff(world, prior_feedback=first["handoff_feedback"])
    assert dup["status"] == STATUS_HELD
    assert dup["reason"] == "DUPLICATE_PREPARE_FEEDBACK"

    forged = dict(first["handoff_feedback"])
    forged["proposal_hash"] = "0" * 64
    forged_out = _handoff(world, prior_feedback=forged)
    assert forged_out["status"] == STATUS_REJECTED
    assert forged_out["reason"] == "FORGED_PREPARE_FEEDBACK"


def test_scope_mismatch_forged_proposal_and_wrong_candidate_hold(tmp_path):
    world = _world(tmp_path)
    out = _handoff(world, phase1_candidate=_candidate(world, files=("scripts/other.py",)))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TICKET_TARGET_SCOPE_EXCEEDED"

    step = _step(world)
    forged = dict(step)
    forged["step_proposal"] = dict(step["step_proposal"])
    forged["step_proposal"]["project"] = dict(step["step_proposal"]["project"])
    forged["step_proposal"]["project"]["base_sha"] = "f" * 40
    out = _handoff(world, supervisor_step=forged)
    assert out["status"] == STATUS_REJECTED
    assert out["reason"].startswith("PROJECT_BINDING_MISMATCH")


def test_independent_ticket_selection_unchanged_and_unknowns_preserved(tmp_path):
    world = _world(tmp_path)
    projection = _projection(
        world,
        tickets=[
            {"ticket_id": "ticket-blocked", "objective": "Blocked", "status": "BLOCKED", "blocked_reason": "UPSTREAM"},
            {"ticket_id": "ticket-dependent", "objective": "Dependent", "status": "PENDING", "dependency_ids": ["ticket-blocked"]},
            {
                "ticket_id": "ticket-f3b",
                "objective": "Independent prepare",
                "status": "PENDING",
                "authorized_paths": [TARGET],
                "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
                "acceptance_criteria": ["R9 prepare result exists"],
                "unknowns": ["semantic uncertainty preserved"],
            },
        ],
    )
    step = _step(world, projection)
    out = _handoff(world, mission_projection=projection, supervisor_step=step)

    assert step["selected_ticket_id"] == "ticket-f3b"
    assert out["status"] == STATUS_PREPARED
    assert "semantic uncertainty preserved" in out["semantic_unknowns"]
    assert out["handoff_feedback"]["prepared_not_verified"] is True


def test_no_execution_or_authority_regression(tmp_path):
    world = _world(tmp_path)

    out = _handoff(world)

    for key in (
        "approval_created",
        "kx108_called",
        "binder_mutation",
        "executor_invoked",
        "repair_loop_invoked",
        "physical_mutation",
        "filesystem_execution",
        "network_or_model_call",
        "memory_write",
        "native_memory_write",
        "ticket_completed",
        "mission_executed",
        "mission_verified",
        "mission_closed",
        "autonomous_retry",
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        assert out[key] is False
        assert out["handoff_feedback"][key] is False
