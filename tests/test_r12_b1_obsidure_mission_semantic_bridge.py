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

from obsidure_local_developer_mission_adapter_v1 import STATUS_HELD as R11_HELD
from obsidure_local_developer_mission_adapter_v1 import STATUS_PREPARED as R11_PREPARED
from obsidure_local_developer_mission_adapter_v1 import run_local_developer_mission
from obsidure_mission_semantic_bridge_v1 import (
    STATUS_HELD,
    STATUS_READY,
    build_brody_obsidure_mission_candidate,
    build_brody_readonly_context_packet,
    build_mission_semantic_context,
)

TARGET = "scripts/r12_b1_fixture.py"
BEFORE = 'VALUE = "old"\n'
AFTER = 'VALUE = "old"\nR12_B1 = "semantic-bridge"\n'


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
    _git(main, "config", "user.email", "r12b1@test.com")
    _git(main, "config", "user.name", "r12b1")
    _git(main, "config", "commit.gpgsign", "false")
    (main / "scripts").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8", newline="\n")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r12-b1-branch"
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
        "repository_identity": "r12-b1-disposable",
        "local_root": str(world["main"]),
        "main_worktree": str(world["main"]),
        "worktree": str(world["exec_wt"]),
        "branch": world["branch"],
        "base_sha": world["base_sha"],
    }


def _scope(**overrides):
    data = {
        "objective": "Prepare bounded semantic bridge fixture repair",
        "target_paths": [TARGET],
        "operations": ["UPDATE_TARGET_FROM_SOURCE"],
        "tools": [
            "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
            "OBSIDIA_NATIVE_SOLVE_STACK_V1",
            "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1",
            "PYTEST",
            "GIT_APPLY_CHECK",
        ],
        "test_commands": ["python -m pytest tests/test_r12_b1_obsidure_mission_semantic_bridge.py"],
        "acceptance_criteria": ["fixture constant is present"],
    }
    data.update(overrides)
    return data


def _mandate(**overrides):
    data = {
        "mission_id": "mission-r12-b1",
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


def _provider(status="VERIFIED"):
    return {
        "provider_id": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": status,
        "availability_evidence_id": "provider-r12-b1",
    }


def _candidate(world, *, rel=TARGET, patch_path=None, patch_content=None):
    patch_content = patch_content if patch_content is not None else Path(patch_path or world["patch_path"]).read_text(encoding="utf-8")
    return {
        "session_id": "dev-r12b1",
        "session_contract": "OBSIDIA_NATIVE_TOOLING_SESSION_V1",
        "status": "PLAN_PROPOSED",
        "targets": [rel],
        "candidate_patch_hash": _sha(patch_content),
        "candidate_files": [rel],
        "plan": {
            "status": "PLAN_PROPOSED",
            "base_sha": world["base_sha"],
            "scope_mode": "EXPLICIT_CHILD_TARGET",
            "candidate_patch_hash": _sha(patch_content),
            "candidate_patch_files": [rel],
            "candidate_patch_source": str(patch_path or world["patch_path"]),
            "display_objective": "R12-B1 semantic bridge candidate",
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
    return {"inventory_snapshot_id": "inv-r12-b1", "status": "VERIFIED", "capabilities": ["OBSIDIA_NATIVE_TOOLING_SESSION_V1"]}


def _deficiency():
    return {"deficiency_evidence_id": "def-r12-b1", "status": "VERIFIED", "summary": "semantic mission requested"}


def _validation(world, patch_hash=None):
    return {"validation_evidence_id": "val-r12-b1", "status": "PASS", "candidate_patch_hash": patch_hash or _sha(world["patch_content"]), "tests": ["contract-e2e"]}


_DEFAULT_MANDATE = object()

def _bridge(world, *, mandate=_DEFAULT_MANDATE, scope=None, request="Reprends le dernier correctif, retrouve le test qui a échoué et prépare une nouvelle mission de réparation.", explicit=None):
    return build_brody_obsidure_mission_candidate(
        human_request=request,
        repository_context=_repo(world),
        proposed_scope=scope or _scope(),
        human_mandate=_mandate() if mandate is _DEFAULT_MANDATE else mandate,
        explicit_references=explicit,
        brody_context_packet=build_brody_readonly_context_packet(session_id="r12-b1-test", request_text=request),
        provider_config=_provider(),
    )


def _run_r11(world, bridge, candidate=None):
    candidate = candidate or _candidate(world)
    return run_local_developer_mission(
        mission_contract=bridge["mission_contract"],
        provider_config=bridge["provider_config"],
        inventory_snapshot=_inventory(),
        deficiency_evidence=_deficiency(),
        validation_evidence=_validation(world, candidate["candidate_patch_hash"]),
        phase1_candidate=candidate,
        artifact_root=world["artifact_root"],
        stores_base_dir=world["stores"],
        session_id="r12-b1",
    )


def test_explicit_mission_patch_test_and_attempt_references_resolve(tmp_path):
    world = _world(tmp_path)
    explicit = {
        "dernier correctif": {"kind": "patch", "patch_id": "patch-r12-b1"},
        "test qui a échoué": {"kind": "test", "test_id": "test-r12-b1"},
        "mission": {"kind": "mission", "mission_id": "mission-r12-b1"},
        "attempt": {"kind": "attempt", "attempt_id": "attempt-r12-b1"},
    }
    bridge = _bridge(world, explicit=explicit, request="Reprends le dernier correctif, le test qui a échoué, cette mission et cet attempt.")
    refs = bridge["semantic_context"]["mission_references"]

    assert bridge["status"] == STATUS_READY
    assert {r["resolved_id"] for r in refs if r["status"] == "RESOLVED_EXPLICIT"} >= {
        "patch-r12-b1", "test-r12-b1", "mission-r12-b1", "attempt-r12-b1"
    }
    assert all(r["nearest_event_fallback"] is False for r in refs)


def test_ambiguous_anaphoric_and_unknown_event_remain_unresolved():
    context = build_mission_semantic_context("Reprends le dernier correctif et ce test inconnu.")
    refs = context["mission_references"]

    assert any(r["surface"] == "dernier correctif" and r["status"] == "UNRESOLVED" for r in refs)
    assert any(r["reason"] == "EXPLICIT_ID_REQUIRED" for r in refs)
    assert context["interpretation_promoted_to_fact"] is False
    assert context["memory_write"] is False


def test_projected_occurrence_is_not_treated_as_observed_and_timestamp_not_fabricated():
    context = build_mission_semantic_context("Paul lancera le test demain. J'ai observé ce lancement.")
    semantic_ref = context["semantic_event_references"]["references"][0]

    assert context["events"][0]["occurrence_claim"] == "PROJECTED_FUTURE"
    assert semantic_ref["resolution_status"] == "AMBIGUOUS"
    assert semantic_ref["metadata"]["occurrence_conflict"] is True
    assert context["absolute_timestamp_fabricated"] is False
    assert any(t["resolution_status"] == "UNRESOLVED_RELATIVE" for t in context["temporal_attachments"])


def test_cross_frame_reference_cannot_be_silently_linked():
    wrong = {"this patch": {"kind": "patch", "patch_id": "patch-r12-b1", "source_frame": "frame:other"}}
    context = build_mission_semantic_context("Please resume this patch.", explicit_references=wrong)
    ref = context["mission_references"][0]

    assert ref["status"] == "UNRESOLVED"
    assert ref["reason"] == "CROSS_FRAME_REFERENCE_REJECTED"
    assert ref["fabricated_id"] is False


def test_contradictions_survive_review_join_and_temporal_order_is_relative_only():
    contradiction = build_mission_semantic_context("Lance le test mais ne lance pas le test.")
    temporal = build_mission_semantic_context("prépare le build puis lance le test")

    assert contradiction["frame"]["contradictions"]
    assert any(r["dimension"] == "contradiction" for join in contradiction["review_joins"] for r in join["readings"])
    assert contradiction["review_joins"][0]["metadata"]["truth"] is None
    assert temporal["temporal_attachments"][0]["relation_type"] == "BEFORE"
    assert temporal["temporal_attachments"][0]["metadata"]["absolute_time"] is False
    assert temporal["temporal_attachments"][0]["metadata"]["causal_flow_invented"] is False


def test_brody_cannot_grant_authorization_and_missing_mandate_cannot_reach_execution(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world, mandate=None)

    assert bridge["status"] == STATUS_HELD
    assert bridge["reason"] == "HUMAN_MANDATE_REQUIRED"
    assert bridge["brody_authority"] == "NONE"
    assert bridge["approval_created"] is False
    assert bridge["mission_candidate_is_executable"] is False
    out = _run_r11(world, bridge)
    assert out["status"] == R11_HELD
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False


def test_candidate_cannot_bypass_existing_r11_b2_scope_validation(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world, mandate=_mandate(authorized_target_paths=["scripts/other.py"]))

    out = _run_r11(world, bridge)

    assert out["status"] == R11_HELD
    assert out["reason"] == "MISSION_TARGET_SCOPE_EXCEEDED"
    assert out["executor_invoked"] is False


def test_contract_e2e_prepare_only_reaches_r11_b2_without_execution(tmp_path):
    world = _world(tmp_path)
    bridge = _bridge(world)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _run_r11(world, bridge)

    assert bridge["human_mandate_bound"] is True
    assert bridge["mission_contract"]["mission_authority"] == "KX108_ONLY"
    assert out["status"] == R11_PREPARED
    assert out["prepared_action"]["status"] == "PREPARED_AWAITING_HUMAN_APPROVAL"
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_existing_cli_behavior_is_unchanged_and_legacy_direct_apply_blocked():
    obsidure_cli = (WORKTREE / "scripts" / "obsidure_cli.py").read_text(encoding="utf-8")
    global_cli = (WORKTREE / "scripts" / "obsidia_cli.py").read_text(encoding="utf-8")

    assert "LEGACY_DIRECT_APPLY_DISABLED" in obsidure_cli
    assert "--objective" in obsidure_cli and "--dry-run" in obsidure_cli and "--apply" in obsidure_cli
    assert "OBSIDURE_PROPOSAL_READER_V2" in global_cli
    assert "OBSIDIA_TERMINAL_OBSIDURE_BRIDGE_V1" in global_cli
    assert "obsidure-task" in global_cli


def test_brody_context_packet_boundary_is_preserved():
    packet = build_brody_readonly_context_packet(session_id="r12-b1-boundary", request_text="prepare context")
    context = build_mission_semantic_context("prépare le build", brody_context_packet=packet)

    assert context["brody_context_packet"]["decision_authority"] == "KX108_ONLY"
    assert context["brody_context_packet"]["readonly"] is True
    assert context["brody_context_packet"]["emits_act"] is False
    assert context["brody_context_packet"]["memory_write"] is False
    assert context["brody_authority"] == "NONE"
    assert context["sens_authority"] == "NONE"