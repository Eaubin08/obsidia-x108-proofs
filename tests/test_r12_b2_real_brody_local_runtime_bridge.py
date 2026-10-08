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

from obsidure_local_developer_mission_adapter_v1 import STATUS_PREPARED as R11_PREPARED
from obsidure_local_developer_mission_adapter_v1 import run_local_developer_mission
from obsidure_mission_semantic_bridge_v1 import (
    R12_B2_RUNTIME_SCHEMA_VERSION,
    STATUS_HELD,
    build_real_brody_obsidure_mission_candidate,
    run_real_brody_local_runtime_bridge,
)

TARGET = "scripts/r12_b2_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nR12_B2 = "real-brody-runtime-bridge"\n'


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _patch(rel: str = TARGET) -> str:
    return "".join(
        difflib.unified_diff(
            BEFORE.splitlines(keepends=True),
            AFTER.splitlines(keepends=True),
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
    _git(main, "config", "user.email", "r12b2@test.com")
    _git(main, "config", "user.name", "r12b2")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r12-b2-branch"
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


def _repo(world):
    return {
        "repository_identity": "r12-b2-disposable",
        "local_root": str(world["main"]),
        "main_worktree": str(world["main"]),
        "worktree": str(world["exec_wt"]),
        "branch": world["branch"],
        "base_sha": world["base_sha"],
    }


def _scope(**overrides):
    data = {
        "objective": "Prepare a bounded R12-B2 Brody runtime bridge fixture",
        "target_paths": [TARGET],
        "operations": ["UPDATE_TARGET_FROM_SOURCE"],
        "tools": [
            "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
            "OBSIDIA_NATIVE_SOLVE_STACK_V1",
            "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
            "PYTEST",
            "GIT_APPLY_CHECK",
        ],
        "test_commands": ["python -m pytest tests/test_r12_b2_real_brody_local_runtime_bridge.py"],
        "acceptance_criteria": ["R12_B2 fixture constant is present"],
    }
    data.update(overrides)
    return data


def _mandate(**overrides):
    data = {
        "mission_id": "mission-r12-b2",
        "status": "ACTIVE",
        "mission_authority": "KX108_ONLY",
        "authorized_target_paths": [TARGET],
        "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
        "approved_tools": [
            "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
            "OBSIDIA_NATIVE_SOLVE_STACK_V1",
            "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
            "PYTEST",
            "GIT_APPLY_CHECK",
        ],
        "mission_budget": 1,
        "attempt_limit": 1,
    }
    data.update(overrides)
    return data


def _provider():
    return {
        "provider_id": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": "VERIFIED",
        "availability_evidence_id": "provider-r12-b2",
    }


def _candidate(world):
    patch_content = world["patch_content"]
    return {
        "session_id": "dev-r12b2",
        "session_contract": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": "PLAN_PROPOSED",
        "targets": [TARGET],
        "candidate_patch_hash": _sha(patch_content),
        "candidate_files": [TARGET],
        "plan": {
            "status": "PLAN_PROPOSED",
            "base_sha": world["base_sha"],
            "scope_mode": "EXPLICIT_CHILD_TARGET",
            "candidate_patch_hash": _sha(patch_content),
            "candidate_patch_files": [TARGET],
            "candidate_patch_source": str(world["patch_path"]),
            "display_objective": "R12-B2 real Brody runtime bridge candidate",
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
        "inventory_snapshot_id": "inv-r12-b2",
        "status": "VERIFIED",
        "capabilities": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"],
    }


def _deficiency():
    return {
        "deficiency_evidence_id": "def-r12-b2",
        "status": "VERIFIED",
        "summary": "real Brody runtime interpreted a local developer mission",
    }


def _validation(world):
    return {
        "validation_evidence_id": "val-r12-b2",
        "status": "PASS",
        "candidate_patch_hash": _sha(world["patch_content"]),
        "tests": ["r12-b2-disposable-contract"],
    }


_DEFAULT_MANDATE = object()


def _bridge(world, *, mandate=_DEFAULT_MANDATE, request=None, explicit=None):
    return build_real_brody_obsidure_mission_candidate(
        human_request=request
        or "Use Brody to prepare a bounded local developer mission for this repository fixture.",
        repository_context=_repo(world),
        proposed_scope=_scope(),
        human_mandate=_mandate() if mandate is _DEFAULT_MANDATE else mandate,
        explicit_references=explicit,
        provider_config=_provider(),
        session_id="r12-b2-test",
        language="en",
    )


def test_real_brody_runtime_invocation_preserves_readonly_boundary():
    evidence = run_real_brody_local_runtime_bridge(
        human_request="R12-B2 readonly probe: prepare mission semantics only.",
        session_id="r12-b2-runtime-test",
        language="en",
    )

    assert evidence["status"] == "R12_REAL_BRODY_RUNTIME_READY"
    assert evidence["adapter_schema_version"] == R12_B2_RUNTIME_SCHEMA_VERSION
    assert evidence["runtime_available"] is True
    assert evidence["model_id"] == "BRODY_FULL_RUNTIME_ORCHESTRATOR_V5B_READONLY"
    assert evidence["model_call_used"] is False
    assert evidence["provider_status"] in {"NOT_REQUESTED", "DISABLED_BY_POLICY"}
    assert evidence["response_hash"]
    assert evidence["decision_authority"] == "KX108_ONLY"
    assert evidence["executor_invoked"] is False
    assert evidence["memory_write"] is False


def test_real_brody_mission_candidate_reaches_r11_b2_prepare_only(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = run_local_developer_mission(
        mission_contract=bridge["mission_contract"],
        provider_config=bridge["provider_config"],
        inventory_snapshot=_inventory(),
        deficiency_evidence=_deficiency(),
        validation_evidence=_validation(world),
        phase1_candidate=_candidate(world),
        artifact_root=world["artifact_root"],
        stores_base_dir=world["stores"],
        session_id="r12-b2",
    )

    assert bridge["real_brody_runtime_verified"] is True
    assert bridge["real_local_model_verified"] is False
    assert bridge["mission_prepare_only"] is True
    assert bridge["brody_runtime_evidence"]["response_hash"]
    assert out["status"] == R11_PREPARED
    assert out["r11_b1_integration"] is True
    assert out["r9_governed_prepare"] is True
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_missing_mandate_holds_after_real_brody_runtime(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world, mandate=None)

    assert bridge["status"] == STATUS_HELD
    assert bridge["reason"] == "HUMAN_MANDATE_REQUIRED"
    assert bridge["brody_runtime_connected"] is True
    assert bridge["approval_created"] is False
    assert bridge["executor_invoked"] is False


def test_ambiguous_reference_is_preserved_not_fabricated(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world, request="Resume the previous patch and prepare a mission.")
    refs = bridge["semantic_context"]["mission_references"]

    assert any(r["status"] == "UNRESOLVED" for r in refs)
    assert any(r["reason"] == "EXPLICIT_ID_REQUIRED" for r in refs)
    assert all(r["nearest_event_fallback"] is False for r in refs)
    assert bridge["semantic_context"]["interpretation_promoted_to_fact"] is False


def test_existing_clis_and_authority_surfaces_are_unchanged():
    obsidure_cli = (WORKTREE / "scripts" / "obsidure_cli.py").read_text(encoding="utf-8")
    global_cli = (WORKTREE / "scripts" / "obsidia_cli.py").read_text(encoding="utf-8")

    assert "LEGACY_DIRECT_APPLY_DISABLED" in obsidure_cli
    assert "--objective" in obsidure_cli and "--dry-run" in obsidure_cli and "--apply" in obsidure_cli
    assert "OBSIDURE_PROPOSAL_READER_V2" in global_cli
    assert "OBSIDIA_TERMINAL_OBSIDURE_BRIDGE_V1" in global_cli
    assert "obsidure-task" in global_cli
