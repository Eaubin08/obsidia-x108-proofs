from __future__ import annotations

import difflib
import hashlib
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from apps.obsidia_api import main as api_main
from apps.obsidia_api.main import app
from apps.obsidia_api.routes import supervised_missions as S

client = TestClient(app)

TARGET = "scripts/r12_f6c1_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nR12_F6C1 = "prepare-only"\n'


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


def _world(tmp_path: Path) -> dict[str, object]:
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "config", "core.autocrlf", "false")
    _git(main, "config", "user.email", "r12f6c1@test.com")
    _git(main, "config", "user.name", "r12f6c1")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r12-f6-c1-branch"
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
        "patch_path": patch_path,
        "patch_content": patch_content,
        "checkpoint_store": tmp_path / "checkpoints",
        "prepare_store": tmp_path / "prepare-store",
    }


def _candidate(world: dict[str, object], *, files=(TARGET,), patch_path=None, patch_content=None):
    patch_path = Path(patch_path or world["patch_path"])
    patch_content = patch_content if patch_content is not None else patch_path.read_text(encoding="utf-8")
    return {
        "session_id": "r12-f6-c1",
        "session_contract": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": "PLAN_PROPOSED",
        "targets": list(files),
        "candidate_patch_hash": _sha(patch_content),
        "candidate_files": list(files),
        "plan": {
            "status": "PLAN_PROPOSED",
            "base_sha": world["base_sha"],
            "scope_mode": "EXPLICIT_CHILD_TARGET",
            "candidate_patch_hash": _sha(patch_content),
            "candidate_patch_files": list(files),
            "candidate_patch_source": str(patch_path),
            "display_objective": "Prepare supervised mission ingress fixture",
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


def _request(world: dict[str, object], **overrides):
    base = {
        "human_request": "Prepare a bounded supervised mission fixture.",
        "repository_context": {
            "repository_identity": "repo://r12-f6-c1-disposable",
            "local_root": str(world["main"]),
            "worktree": str(world["exec_wt"]),
            "branch": world["branch"],
            "base_sha": world["base_sha"],
        },
        "proposed_scope": {
            "objective": "Prepare a bounded supervised mission fixture.",
            "target_paths": [TARGET],
            "operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "tools": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"],
            "test_commands": ["python -m pytest tests/api/test_supervised_mission_prepare_ingress_api.py"],
            "acceptance_criteria": ["checkpoint saved"],
        },
        "human_mandate": {
            "mission_id": "mission-r12-f6-c1",
            "status": "ACTIVE",
            "mission_authority": "KX108_ONLY",
            "authorized_target_paths": [TARGET],
            "authorized_operations": ["UPDATE_TARGET_FROM_SOURCE"],
            "approved_tools": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"],
            "mission_budget": 2,
            "attempt_limit": 2,
            "attempt_index": 0,
        },
        "provider_config": {
            "provider_id": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
            "status": "VERIFIED",
            "availability_evidence_id": "provider-r12-f6-c1",
        },
        "phase1_candidate": _candidate(world),
        "inventory_snapshot": {
            "inventory_snapshot_id": "inv-r12-f6-c1",
            "status": "VERIFIED",
            "capabilities": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"],
        },
        "deficiency_evidence": {
            "deficiency_evidence_id": "def-r12-f6-c1",
            "status": "VERIFIED",
            "summary": "supervised prepare ingress required",
        },
        "validation_evidence": {
            "validation_evidence_id": "val-r12-f6-c1",
            "status": "PASS",
            "candidate_patch_hash": _sha(str(world["patch_content"])),
            "tests": ["bounded-disposable-validation"],
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged = dict(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = value
    return base


def _ready_candidate(validated):
    contract = {
        "mission_id": validated["human_mandate"]["mission_id"],
        "status": "ACTIVE",
        "human_mandate_reference": "mandate-r12-f6-c1",
        "repository_identity": validated["repository_context"]["repository_identity"],
        "local_root": validated["repository_context"]["local_root"],
        "worktree": validated["repository_context"]["worktree"],
        "branch": validated["repository_context"]["branch"],
        "base_sha": validated["repository_context"]["base_sha"],
        "current_head": validated["repository_context"]["base_sha"],
        "objective": validated["proposed_scope"]["objective"],
        "acceptance_criteria": validated["proposed_scope"]["acceptance_criteria"],
        "allowed_target_paths": validated["human_mandate"]["authorized_target_paths"],
        "allowed_operations": validated["human_mandate"]["authorized_operations"],
        "test_commands": validated["proposed_scope"]["test_commands"],
        "mission_budget": validated["human_mandate"]["mission_budget"],
        "attempt_limit": validated["human_mandate"]["attempt_limit"],
        "attempt_index": 0,
        "mission_authority": "KX108_ONLY",
        "revoked": False,
    }
    return {
        "adapter_schema_version": "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1",
        "status": "R12_MISSION_CANDIDATE_READY_FOR_R11_B2",
        "mission_kind": "LOCAL_DEVELOPER",
        "semantic_context": {
            "frame": {
                "missing": [],
                "ambiguities": [],
                "unresolved_references": [],
                "closure_blockers": [],
                "contradictions": [],
            },
            "open_items": {},
            "mission_references": [],
        },
        "mission_contract": contract,
        "human_mandate_bound": True,
        "mission_candidate_is_executable": False,
        "r11_b2_compatible_contract": True,
        "decision_authority": "KX108_ONLY",
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "memory_write": False,
        "graphiti_write": False,
        "legacy_direct_apply": False,
        "real_brody_runtime_verified": True,
        "real_local_model_verified": True,
        "model_call_used": True,
        "local_model_evidence_source_ref": "model-evidence:qwen:r12-f6-c1",
        "local_model_evidence": {
            "source_ref": "model-evidence:qwen:r12-f6-c1",
            "provider": "QWEN_LOCAL",
            "model": "qwen2.5-3b-instruct-q4_k_m",
            "evidence_hash": "c" * 64,
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "allowed_to_act": False,
        },
        "brody_runtime_evidence": {"response_hash": "d" * 64, "model_call_used": True, "readonly": True},
        "provenance": {"source": "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1"},
    }


def _install_paths(monkeypatch, world):
    monkeypatch.setattr(S, "_DEFAULT_STORE", Path(world["checkpoint_store"]))
    monkeypatch.setattr(S, "_DEFAULT_PREPARE_STORE", Path(world["prepare_store"]))
    monkeypatch.setattr(S, "_build_mission_candidate", _ready_candidate)


def test_valid_request_prepares_and_saves_canonical_checkpoint(monkeypatch, tmp_path):
    world = _world(tmp_path)
    _install_paths(monkeypatch, world)

    response = client.post("/api/supervised-missions/prepare-only", json=_request(world))

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == S.PREPARE_STATUS_ACCEPTED
    assert data["state"] == "PREPARED_AWAITING_APPROVAL"
    assert data["checkpoint_id"].startswith("smc-")
    assert data["provider_provenance"]["real_local_model_verified"] is True
    assert data["provider_provenance"]["model_call_used"] is True
    assert data["executor_invoked"] is False
    assert data["approval_created"] is False
    assert data["memory_write"] is False
    assert (Path(world["exec_wt"]) / TARGET).read_text(encoding="utf-8") == BEFORE

    projection = client.get(f"/api/supervised-missions/checkpoints/{data['checkpoint_id']}/projection")
    assert projection.status_code == 200
    assert projection.json()["mission_id"] == "mission-r12-f6-c1"


def test_missing_revoked_or_invalid_mandate_fails_closed(monkeypatch, tmp_path):
    world = _world(tmp_path)
    _install_paths(monkeypatch, world)

    missing = _request(world)
    missing.pop("human_mandate")
    assert client.post("/api/supervised-missions/prepare-only", json=missing).status_code == 422

    revoked = client.post(
        "/api/supervised-missions/prepare-only",
        json=_request(world, human_mandate={"status": "REVOKED", "revoked": True}),
    ).json()
    assert revoked["status"] == S.PREPARE_STATUS_HELD
    assert revoked["reason"] == "HUMAN_MANDATE_REVOKED"

    invalid = client.post(
        "/api/supervised-missions/prepare-only",
        json=_request(world, human_mandate={"mission_authority": "BRODY"}),
    ).json()
    assert invalid["reason"] == "MISSION_AUTHORITY_NOT_KX108_ONLY"


def test_stale_dirty_scope_and_provider_unavailable_hold(monkeypatch, tmp_path):
    world = _world(tmp_path)
    _install_paths(monkeypatch, world)

    stale = client.post(
        "/api/supervised-missions/prepare-only",
        json=_request(world, repository_context={"base_sha": "f" * 40}),
    ).json()
    assert stale["reason"] == "STALE_BASE_SHA"

    scope = client.post(
        "/api/supervised-missions/prepare-only",
        json=_request(world, proposed_scope={"target_paths": ["scripts/out_of_scope.py"]}),
    ).json()
    assert scope["reason"] == "SCOPE_VIOLATION"

    provider = client.post(
        "/api/supervised-missions/prepare-only",
        json=_request(world, provider_config={"status": "UNAVAILABLE"}),
    ).json()
    assert provider["reason"] == "PROVIDER_UNAVAILABLE"

    (Path(world["exec_wt"]) / "dirty.txt").write_text("dirty", encoding="utf-8")
    dirty = client.post("/api/supervised-missions/prepare-only", json=_request(world)).json()
    assert dirty["reason"] == "WORKTREE_DIRTY"


def test_prepare_hold_and_f4b_rejection_are_not_reported_as_success(monkeypatch, tmp_path):
    world = _world(tmp_path)
    _install_paths(monkeypatch, world)

    no_validation = _request(world)
    no_validation.pop("validation_evidence")
    held = client.post("/api/supervised-missions/prepare-only", json=no_validation).json()
    assert held["status"] == S.PREPARE_STATUS_HELD
    assert held["reason"] == "VALIDATION_EVIDENCE_REQUIRED"
    assert held["checkpoint_id"] is None

    def reject_f4b(**_kwargs):
        return {
            "status": "R12_F4_B_DEPENDENCY_STATE_HELD",
            "reason": "F4B_TEST_REJECTION",
            "mission_update_accepted": False,
        }

    monkeypatch.setattr(S, "integrate_supervised_dependency_state", reject_f4b)
    rejected = client.post("/api/supervised-missions/prepare-only", json=_request(world)).json()
    assert rejected["status"] == S.PREPARE_STATUS_HELD
    assert rejected["reason"] == "F4B_TEST_REJECTION"
    assert rejected["checkpoint_projection_available"] is False


def test_api_key_policy_and_no_authority_side_effects(monkeypatch, tmp_path):
    world = _world(tmp_path)
    _install_paths(monkeypatch, world)
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "secret")

    denied = client.post("/api/supervised-missions/prepare-only", json=_request(world))

    assert denied.status_code == 401
    assert denied.json()["error"] == "unauthorized"
    monkeypatch.setattr(api_main, "_EXPECTED_API_KEY", "")

    allowed = client.post("/api/supervised-missions/prepare-only", json=_request(world)).json()
    for key in (
        "emits_act",
        "approval_created",
        "automatic_approval",
        "kx108_called",
        "binder_mutation",
        "executor_invoked",
        "repair_loop_invoked",
        "filesystem_execution",
        "memory_write",
        "native_memory_write",
        "commit_created",
        "push_performed",
        "merge_performed",
    ):
        assert allowed[key] is False
