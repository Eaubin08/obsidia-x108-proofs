from __future__ import annotations

import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
for p in (WORKTREE, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import obsidia_canonical_receipt_replay_v1 as R8_REPLAY
import obsidia_realized_state_reconciliation_v1 as R8_RECONCILE
from obsidure_local_developer_mission_adapter_v1 import (
    STATUS_EXECUTED,
    STATUS_HELD,
    STATUS_PREPARED,
    STATUS_REJECTED,
    run_local_developer_mission,
)


TARGET = "scripts/obsidia_dev_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nDEV_MISSION = "bounded"\n'


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
    _git(main, "config", "user.email", "r11b2@test.com")
    _git(main, "config", "user.name", "r11b2")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r11-b2-branch"
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
        "artifact_root": tmp_path / "artifacts",
        "patch_path": patch_path,
        "patch_content": patch_content,
    }


def _mission(world, **overrides):
    data = {
        "mission_id": "mission-r11-b2",
        "status": "ACTIVE",
        "repository_identity": "obsidia-openjarvis-install-v0",
        "local_root": str(world["main"]),
        "main_worktree": str(world["main"]),
        "worktree": str(world["exec_wt"]),
        "branch": world["branch"],
        "base_sha": world["base_sha"],
        "objective": "Add bounded developer mission fixture",
        "acceptance_criteria": ["fixture constant is present"],
        "allowed_target_paths": [TARGET],
        "allowed_operations": ["UPDATE_TARGET_FROM_SOURCE"],
        "approved_tools": [
            "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
            "OBSIDIA_NATIVE_SOLVE_STACK_V1",
            "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
            "PYTEST",
            "GIT_APPLY_CHECK",
        ],
        "test_commands": ["python -m pytest tests/test_r11_b2_local_developer_mission_adapter.py"],
        "mission_budget": 1,
        "attempt_limit": 1,
        "mission_authority": "KX108_ONLY",
    }
    data.update(overrides)
    return data


def _provider(status="VERIFIED"):
    return {
        "provider_id": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": status,
        "availability_evidence_id": "provider-r11-b2",
    }


def _candidate(world, *, patch_path=None, patch_content=None, files=(TARGET,), status="PLAN_PROPOSED", base_sha=None):
    patch_content = patch_content if patch_content is not None else Path(patch_path or world["patch_path"]).read_text(encoding="utf-8")
    return {
        "session_id": "dev-r11b2",
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
            "display_objective": "Local developer mission candidate",
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


def _inventory():
    return {
        "inventory_snapshot_id": "inv-r11-b2",
        "status": "VERIFIED",
        "capabilities": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"],
    }


def _deficiency():
    return {
        "deficiency_evidence_id": "def-r11-b2",
        "status": "VERIFIED",
        "summary": "bounded developer change requested",
    }


def _validation(world, patch_hash=None):
    return {
        "validation_evidence_id": "val-r11-b2",
        "status": "PASS",
        "candidate_patch_hash": patch_hash or _sha(world["patch_content"]),
        "tests": ["bounded-disposable-validation"],
    }


def _run(world, **overrides):
    candidate = overrides.pop("phase1_candidate", _candidate(world))
    return run_local_developer_mission(
        mission_contract=overrides.pop("mission_contract", _mission(world)),
        provider_config=overrides.pop("provider_config", _provider()),
        inventory_snapshot=overrides.pop("inventory_snapshot", _inventory()),
        deficiency_evidence=overrides.pop("deficiency_evidence", _deficiency()),
        validation_evidence=overrides.pop("validation_evidence", _validation(world, candidate["candidate_patch_hash"])),
        phase1_candidate=candidate,
        artifact_root=world["artifact_root"],
        stores_base_dir=world["stores"],
        session_id="r11-b2",
        **overrides,
    )


def test_valid_bounded_mission_reaches_r11_b1_and_r9_prepare_only(tmp_path):
    world = _world(tmp_path)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _run(world)

    assert out["status"] == STATUS_PREPARED
    assert out["mission_kind"] == "LOCAL_DEVELOPER"
    assert out["local_provider_verified"] is True
    assert out["r11_b1_integration"] is True
    assert out["r9_governed_prepare"] is True
    assert out["prepared_action"]["status"] == "PREPARED_AWAITING_HUMAN_APPROVAL"
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["memory_write"] is False
    assert out["commit_created"] is False
    assert out["push_performed"] is False
    assert out["merge_performed"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_missing_revoked_authority_and_exhausted_budget_hold(tmp_path):
    world = _world(tmp_path)

    out = _run(world, mission_contract=_mission(world, mission_authority="NONE"))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_AUTHORITY_NOT_KX108_ONLY"

    out = _run(world, mission_contract=_mission(world, status="REVOKED"))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_REVOKED"

    out = _run(world, mission_contract=_mission(world, mission_budget=0))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_BUDGET_EXHAUSTED"


def test_wrong_repository_worktree_base_and_scope_hold_or_reject(tmp_path):
    world = _world(tmp_path)

    out = _run(world, mission_contract=_mission(world, base_sha="f" * 40))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "WORKTREE_BASE_SHA_MISMATCH"

    out = _run(world, mission_contract=_mission(world, worktree=str(world["main"])))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "WORKTREE_BRANCH_MISMATCH"

    out = _run(world, mission_contract=_mission(world, allowed_target_paths=["scripts/other.py"]))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_TARGET_SCOPE_EXCEEDED"


def test_model_unavailable_and_candidate_tampering_hold_or_reject(tmp_path):
    world = _world(tmp_path)

    out = _run(world, provider_config=_provider("UNAVAILABLE"))
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MODEL_UNAVAILABLE"

    tampered = world["patch_content"] + "\n"
    tampered_path = world["artifact_root"] / "tampered.patch"
    tampered_path.parent.mkdir(parents=True)
    tampered_path.write_text(tampered, encoding="utf-8")
    candidate = _candidate(world, patch_path=tampered_path, patch_content=world["patch_content"])

    out = _run(world, phase1_candidate=candidate)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "CANDIDATE_PATCH_HASH_MISMATCH"


def test_successful_governed_disposable_execution_writes_r8_evidence(tmp_path):
    world = _world(tmp_path)
    prepared = _run(world)
    eah = prepared["prepared_action"]["execution_authority_hash"]

    out = _run(
        world,
        execute_authorized=True,
        human_authorized_eah=eah,
        human_authorization_reference="human-r11-b2-test-authorization",
    )

    assert out["status"] == STATUS_EXECUTED
    assert out["r9_b6_authorized_execution"] is True
    assert out["r8_evidence"] is True
    assert out["action_evidence_id"].startswith("aev-")
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == AFTER
    replay = R8_REPLAY.replay_action_evidence(out["action_evidence_id"], stores_base_dir=world["stores"])
    assert replay["replay_verdict"] in {"VERIFIED", "VERIFIED_WITH_LIMITS"}
    reconciliation = R8_RECONCILE.reconcile_action_evidence(out["action_evidence_id"], stores_base_dir=world["stores"])
    assert reconciliation["reconciliation_status"] == "MATCH"


def test_authorized_execution_requires_matching_eah(tmp_path):
    world = _world(tmp_path)

    out = _run(
        world,
        execute_authorized=True,
        human_authorized_eah="f" * 64,
        human_authorization_reference="human-r11-b2-test-authorization",
    )

    assert out["status"] == STATUS_REJECTED
    assert out["reason"] == "HUMAN_AUTHORIZED_EAH_MISMATCH"
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == BEFORE


def test_repair_feedback_is_explicit_and_does_not_reclassify_normal_missions(tmp_path):
    world = _world(tmp_path)

    class FakeAgent:
        def __init__(self):
            self.calls = 0

        def ingest_repair_execution_outcome(self, **kwargs):
            self.calls += 1
            return {"classification": "EXECUTED_VERIFIED", "recommendation": "STOP_SUCCESS", "kwargs": kwargs}

    fake_agent = FakeAgent()
    prepared = _run(world)
    eah = prepared["prepared_action"]["execution_authority_hash"]

    out = _run(
        world,
        execute_authorized=True,
        human_authorized_eah=eah,
        human_authorization_reference="human-r11-b2-test-authorization",
        repair_feedback={"agent": fake_agent, "prepared_repair": {"repair_lineage": {"id": "explicit"}}},
    )

    assert out["mission_kind"] == "LOCAL_DEVELOPER"
    assert out["r10_feedback"]["classification"] == "EXECUTED_VERIFIED"
    assert fake_agent.calls == 1


def test_both_cli_interfaces_are_preserved_and_legacy_direct_apply_stays_disabled():
    obsidure_cli = (WORKTREE / "scripts" / "obsidure_cli.py").read_text(encoding="utf-8")
    global_cli = (WORKTREE / "scripts" / "obsidia_cli.py").read_text(encoding="utf-8")

    assert "--objective" in obsidure_cli
    assert "--dry-run" in obsidure_cli
    assert "--apply" in obsidure_cli
    assert "LEGACY_DIRECT_APPLY_DISABLED" in obsidure_cli
    assert "AgentObsidure" in obsidure_cli

    assert "OBSIDURE_PROPOSAL_READER_V2" in global_cli
    assert "OBSIDIA_TERMINAL_OBSIDURE_BRIDGE_V1" in global_cli
    assert "obsidure-task" in global_cli
    assert "subprocess.run" not in global_cli
