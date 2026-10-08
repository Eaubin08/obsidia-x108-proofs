from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL
from obsidure_repair_r9_adapter_v1 import (
    STATUS_HELD,
    STATUS_PREPARED,
    STATUS_STOPPED,
    adapt_validated_repair_to_r9_prepare,
)
from periphery.agents.obsidure_repair_contract import (
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
    RepairVerdict,
)


TARGET = "periphery/repair_target.py"
BEFORE = "value = 1\n"
AFTER = "value = 2\n"


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


@pytest.fixture
def repair_world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "r10b1@test.com")
    _git(main, "config", "user.name", "r10b1")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    _git(main, "worktree", "add", str(exec_wt), "-b", "r10-b1-branch", base_sha)
    return {"main": main, "exec_wt": exec_wt, "base_sha": base_sha, "stores": tmp_path / "stores"}


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _material(world, *, after=AFTER, request_id="rr_r10", proposal_id="rp_r10", verdict_status="PASS"):
    base_file_sha = _sha_file(world["exec_wt"] / TARGET)
    request = RepairRequest(
        request_id=request_id,
        objective="repair target",
        failure_mode="BUILD_ERROR",
        summary="failure_mode=BUILD_ERROR",
        repo_targets=[TARGET],
        attempts_spent=1,
        tests_hint=["repair-sandbox-verdict"],
    )
    proposal = RepairProposal(
        proposal_id=proposal_id,
        request_id=request_id,
        rationale="repair target",
        candidate_files=[
            RepairCandidateFile(
                path=TARGET,
                full_content=after,
                change_kind="MODIFY",
                base_sha256=base_file_sha,
                rationale="fix value",
            )
        ],
        tests_to_run=["repair-sandbox-verdict"],
        confidence="HIGH",
    )
    verdict = RepairVerdict(
        verdict_id="rv_r10",
        request_id=request_id,
        proposal_id=proposal_id,
        status=verdict_status,
        tested_artifacts=[{"path": TARGET, "sha256": _sha_text(after)}],
        tests_executed=[{"command": "pytest", "status": "PASS"}],
    )
    c278 = {
        "evidence": "CONTINUOUS",
        "request_id": request_id,
        "proposal_id": proposal_id,
    }
    return request, proposal, c278, verdict


def _adapt(world, *material, **kwargs):
    request, proposal, c278, verdict = material or _material(world)
    return adapt_validated_repair_to_r9_prepare(
        repair_request=request,
        repair_proposal=proposal,
        c278_evidence=c278,
        repair_verdict=verdict,
        base_commit_sha=world["base_sha"],
        repo_identity_ref="obsidia-openjarvis-install-v0",
        execution_worktree_path=world["exec_wt"],
        main_worktree_path=world["main"],
        branch_name="r10-b1-branch",
        stores_base_dir=world["stores"],
        session_id="r10-b1",
        **kwargs,
    )


def test_valid_repair_candidate_reaches_r9_prepare_without_execution(repair_world):
    before = (repair_world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _adapt(repair_world, *_material(repair_world))

    assert out["status"] == STATUS_PREPARED
    assert out["r9_proposal"].proposal_kind == "REPAIR"
    assert "\n+++ b/periphery/repair_target.py" in out["patch_content"]
    assert out["r9_manifest"].to_dict()["proposal_id"] == out["r9_proposal"].proposal_id
    assert out["r9_validation"].validation_verdict == "VALID"
    assert out["prepared_action"]["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["prepared_action"]["handoff_to_governed_prepare"] is True
    assert out["prepared_action"]["executor_invoked"] is False
    assert out["prepared_action"]["physical_mutation"] is False
    assert out["approval_created"] is False
    assert out["kx108_called"] is False
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["commit_created"] is False
    assert out["push_performed"] is False
    assert out["merge_performed"] is False
    assert (repair_world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_declared_only_evidence_is_not_sufficient_for_b3_valid(repair_world):
    out = _adapt(repair_world, *_material(repair_world), evidence_verification="DECLARED")

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "R9_B3_VALIDATION_NOT_VALID"
    assert out["validation_verdict"] == "INCOMPLETE"
    assert out["handoff_created"] is False


def test_missing_tested_artifact_is_incomplete_before_handoff(repair_world):
    request, proposal, c278, verdict = _material(repair_world)
    verdict.tested_artifacts.clear()

    out = _adapt(repair_world, request, proposal, c278, verdict)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TESTED_ARTIFACT_HASH_MISSING"
    assert out["handoff_created"] is False


def test_c278_divergent_and_failed_sandbox_verdict_do_not_handoff(repair_world):
    request, proposal, c278, verdict = _material(repair_world)
    c278["evidence"] = "DIVERGENT"

    out = _adapt(repair_world, request, proposal, c278, verdict)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "C278_NOT_CONTINUOUS"
    assert out["handoff_created"] is False

    request, proposal, c278, verdict = _material(repair_world, verdict_status="BLOCKED")
    out = _adapt(repair_world, request, proposal, c278, verdict)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "REPAIR_VERDICT_NOT_PASS"


def test_repair_proposal_and_tested_patch_substitution_rejected(repair_world):
    request, proposal, c278, verdict = _material(repair_world)
    proposal.request_id = "rr_forged"

    out = _adapt(repair_world, request, proposal, c278, verdict)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "REPAIR_PROPOSAL_REQUEST_MISMATCH"

    request, proposal, c278, verdict = _material(repair_world)
    verdict.tested_artifacts[0]["sha256"] = "f" * 64
    out = _adapt(repair_world, request, proposal, c278, verdict)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "TESTED_PATCH_SUBSTITUTION"


def test_out_of_scope_protected_path_and_base_drift_rejected(repair_world):
    request, proposal, c278, verdict = _material(repair_world)
    proposal.candidate_files[0].path = "../escape.py"

    out = _adapt(repair_world, request, proposal, c278, verdict)

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "REPAIR_PROPOSAL_INVALID"

    request, proposal, c278, verdict = _material(repair_world)
    proposal.candidate_files[0].path = "proofs/lean/Obsidia/Seal.lean"
    out = _adapt(repair_world, request, proposal, c278, verdict)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "REPAIR_PROPOSAL_INVALID"

    request, proposal, c278, verdict = _material(repair_world)
    (repair_world["exec_wt"] / TARGET).write_text("value = 999\n", encoding="utf-8")
    out = _adapt(repair_world, request, proposal, c278, verdict)
    assert out["status"] == STATUS_HELD
    assert out["reason"] == "BASE_SHA_DRIFT"


def test_mission_revoked_holds_delegated_route(repair_world):
    out = _adapt(
        repair_world,
        *_material(repair_world),
        require_delegation=True,
        mission_context={
            "status": "REVOKED",
            "allowed_targets": [TARGET],
            "allowed_operations": ["APPLY_PATCH"],
            "allowed_tools": ["APPLY_PATCH"],
        },
    )

    assert out["status"] == STATUS_HELD
    assert out["reason"] == "MISSION_REVOKED"
    assert out["handoff_created"] is False


def test_repair_budget_repeated_failure_and_oscillation_stop(repair_world):
    request, proposal, c278, verdict = _material(repair_world)
    request.attempts_spent = 2
    out = _adapt(repair_world, request, proposal, c278, verdict, repair_budget=2)
    assert out["status"] == STATUS_STOPPED
    assert out["reason"] == "REPAIR_BUDGET_EXHAUSTED"

    request, proposal, c278, verdict = _material(repair_world)
    first = _adapt(repair_world, request, proposal, c278, verdict)
    digest = first["stop_conditions"]["failure_digest"]
    out = _adapt(repair_world, request, proposal, c278, verdict, attempt_history=({"failure_digest": digest},))
    assert out["status"] == STATUS_STOPPED
    assert out["reason"] == "REPEATED_IDENTICAL_FAILURE"

    request, proposal, c278, verdict = _material(repair_world)
    patch_hash = _sha_text(first["patch_content"])
    out = _adapt(
        repair_world,
        request,
        proposal,
        c278,
        verdict,
        attempt_history=(
            {"tested_patch_hash": patch_hash},
            {"tested_patch_hash": "b" * 64},
        ),
    )
    assert out["status"] == STATUS_STOPPED
    assert out["reason"] == "OSCILLATING_REPAIR_STATE"


def test_same_immutable_inputs_are_deterministic(repair_world):
    material = _material(repair_world)
    first = _adapt(repair_world, *material)
    second = _adapt(repair_world, *material)

    assert first["r9_proposal"].proposal_id == second["r9_proposal"].proposal_id
    assert first["r9_manifest"].manifest_id == second["r9_manifest"].manifest_id
    assert first["r9_validation"].validation_id == second["r9_validation"].validation_id
    assert first["r9_handoff"].handoff_id == second["r9_handoff"].handoff_id
    assert first["tested_patch_hash"] == second["tested_patch_hash"]
