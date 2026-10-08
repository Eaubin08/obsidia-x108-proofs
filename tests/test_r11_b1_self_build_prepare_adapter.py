from __future__ import annotations

import hashlib
import difflib
import subprocess
import sys
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL
from obsidure_self_build_r9_prepare_adapter_v1 import (
    STATUS_HELD,
    STATUS_PREPARED,
    STATUS_REJECTED,
    adapt_self_build_candidate_to_r9_prepare,
)


TARGET = "scripts/obsidia_selfbuild_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nSELF_BUILD_NOTE = "bounded"\n'


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


@pytest.fixture
def self_build_world(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "config", "core.autocrlf", "false")
    _git(main, "config", "user.email", "r11b1@test.com")
    _git(main, "config", "user.name", "r11b1")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "r11-b1-branch", base_sha)
    patch_dir = tmp_path / "phase1"
    patch_dir.mkdir()
    patch_path = patch_dir / "candidate.patch"
    patch_content = _patch()
    patch_path.write_text(patch_content, encoding="utf-8")
    return {
        "main": main,
        "exec_wt": exec_wt,
        "base_sha": base_sha,
        "stores": tmp_path / "stores",
        "patch_path": patch_path,
        "patch_content": patch_content,
    }


def _candidate(world, *, patch_path=None, patch_content=None, files=(TARGET,), status="PLAN_PROPOSED", base_sha=None):
    patch_content = patch_content if patch_content is not None else Path(patch_path or world["patch_path"]).read_text(encoding="utf-8")
    return {
        "session_id": "jsb-r11b1",
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
            "display_objective": "Prepare bounded self-build candidate",
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


def _mission(status="ACTIVE", *, allowed=(TARGET,), max_actions=1, executed_actions=0, max_iterations=1, used_iterations=0):
    return {
        "mission_id": "mission-r11-b1",
        "status": status,
        "allowed_target_paths": list(allowed),
        "allowed_operation_shapes": ["UPDATE_TARGET_FROM_SOURCE"],
        "allowed_tools": ["EDIT"],
        "max_actions": max_actions,
        "executed_actions": executed_actions,
        "max_iterations": max_iterations,
        "used_iterations": used_iterations,
    }


def _inventory():
    return {
        "inventory_snapshot_id": "inv-r11-b1",
        "status": "VERIFIED",
        "capabilities": ["OBSIDIA_NATIVE_SELF_BUILD_PHASE1"],
    }


def _deficiency():
    return {
        "deficiency_evidence_id": "def-r11-b1",
        "status": "VERIFIED",
        "summary": "bounded improvement needed",
    }


def _validation(world, *, patch_hash=None):
    return {
        "validation_evidence_id": "val-r11-b1",
        "status": "PASS",
        "candidate_patch_hash": patch_hash or _sha(world["patch_content"]),
        "tests": ["focused-self-build-validation"],
    }


def _adapt(world, **overrides):
    candidate = overrides.pop("phase1_candidate", _candidate(world))
    return adapt_self_build_candidate_to_r9_prepare(
        phase1_candidate=candidate,
        mission_context=overrides.pop("mission_context", _mission()),
        inventory_snapshot=overrides.pop("inventory_snapshot", _inventory()),
        deficiency_evidence=overrides.pop("deficiency_evidence", _deficiency()),
        validation_evidence=overrides.pop("validation_evidence", _validation(world, patch_hash=candidate["candidate_patch_hash"])),
        base_commit_sha=overrides.pop("base_commit_sha", world["base_sha"]),
        repo_identity_ref="obsidia-openjarvis-install-v0",
        execution_worktree_path=world["exec_wt"],
        main_worktree_path=world["main"],
        branch_name="r11-b1-branch",
        stores_base_dir=world["stores"],
        session_id="r11-b1",
    )


def test_valid_phase1_candidate_reaches_r9_b5_prepare_only(self_build_world):
    before = (self_build_world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _adapt(self_build_world)

    assert out["status"] == STATUS_PREPARED
    assert out["phase1_candidate_bound"] is True
    assert out["inventory_snapshot_bound"] is True
    assert out["deficiency_evidence_bound"] is True
    assert out["human_mission_bound"] is True
    assert out["non_amplification_check"] == "PASS"
    assert out["r9_proposal"].proposal_kind == "BUILD"
    assert out["r9_validation"].validation_verdict == "VALID"
    assert out["prepared_action"]["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["prepared_action"]["handoff_to_governed_prepare"] is True
    assert out["prepared_action"]["executor_invoked"] is False
    assert out["prepared_action"]["physical_mutation"] is False
    assert out["approval_created"] is False
    assert out["kx108_called"] is False
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["memory_write"] is False
    assert out["capability_expansion"] is False
    assert (self_build_world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_plan_only_or_missing_evidence_holds(self_build_world):
    out = _adapt(self_build_world, validation_evidence=None)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "VALIDATION_EVIDENCE_REQUIRED"
    assert out["handoff_created"] is False

    out = _adapt(self_build_world, inventory_snapshot=None)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "INVENTORY_SNAPSHOT_REQUIRED"

    out = _adapt(self_build_world, deficiency_evidence=None)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "DEFICIENCY_EVIDENCE_REQUIRED"


def test_missing_or_substituted_validation_evidence_holds(self_build_world):
    bad = _validation(self_build_world, patch_hash="f" * 64)

    out = _adapt(self_build_world, validation_evidence=bad)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "VALIDATION_EVIDENCE_PATCH_HASH_MISMATCH"


def test_mission_revoked_closed_or_budget_exhausted_holds(self_build_world):
    out = _adapt(self_build_world, mission_context=_mission("REVOKED"))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_REVOKED"

    out = _adapt(self_build_world, mission_context=_mission("CLOSED"))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_CLOSED"

    out = _adapt(self_build_world, mission_context=_mission(executed_actions=1))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_ACTION_BUDGET_EXHAUSTED"

    out = _adapt(self_build_world, mission_context=_mission(used_iterations=1))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_ITERATION_BUDGET_EXHAUSTED"


def test_out_of_scope_patch_and_patch_substitution_rejected(self_build_world, tmp_path):
    out = _adapt(self_build_world, mission_context=_mission(allowed=("scripts/other.py",)))

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_TARGET_SCOPE_EXCEEDED"

    patch_path = tmp_path / "substituted.patch"
    patch_content = _patch(rel="scripts/other.py", after='VALUE = "old"\nOTHER = "x"\n')
    patch_path.write_text(patch_content, encoding="utf-8")
    candidate = _candidate(self_build_world, patch_path=patch_path, patch_content=patch_content, files=(TARGET,))

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "CANDIDATE_TARGET_SUBSTITUTION"


def test_capability_escalation_candidate_rejected(self_build_world, tmp_path):
    patch_path = tmp_path / "escalation.patch"
    patch_content = (
        "".join(
            difflib.unified_diff(
                BEFORE.splitlines(keepends=True),
                'VALUE = "old"\nimport subprocess\n'.splitlines(keepends=True),
                fromfile=f"a/{TARGET}",
                tofile=f"b/{TARGET}",
                lineterm="\n",
            )
        )
    )
    patch_path.write_text(patch_content, encoding="utf-8")
    candidate = _candidate(self_build_world, patch_path=patch_path, patch_content=patch_content)

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "NON_AMPLIFICATION_HOLD_REQUIRED"
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False


def test_base_sha_and_patch_hash_mismatch_hold_or_reject(self_build_world, tmp_path):
    candidate = _candidate(self_build_world, base_sha="f" * 40)

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "BASE_SHA_MISMATCH"

    patch_path = tmp_path / "tampered.patch"
    patch_path.write_text(self_build_world["patch_content"] + "\n", encoding="utf-8")
    candidate = _candidate(self_build_world, patch_path=patch_path, patch_content=self_build_world["patch_content"])

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "CANDIDATE_PATCH_HASH_MISMATCH"


def test_wrong_repository_patch_location_rejected(self_build_world):
    inside = self_build_world["main"] / "candidate.patch"
    inside.write_text(self_build_world["patch_content"], encoding="utf-8")
    candidate = _candidate(self_build_world, patch_path=inside)

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "CANDIDATE_PATCH_INSIDE_REPO"


def test_plan_proposed_is_required_before_validation(self_build_world):
    candidate = _candidate(self_build_world, status="DRAFT")

    out = _adapt(self_build_world, phase1_candidate=candidate)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "PHASE1_PLAN_NOT_PROPOSED"
    assert out["executor_invoked"] is False
