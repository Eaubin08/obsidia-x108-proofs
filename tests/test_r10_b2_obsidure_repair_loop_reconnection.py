from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_pc_capabilities_v2 import PREPARED_AWAITING_HUMAN_APPROVAL
from periphery.agents import agent_obsidure as agent_module
from periphery.agents.agent_obsidure import AgentObsidure
from periphery.agents.obsidure_repair_contract import (
    ErrorContextRecord,
    REPAIR_BOUNDARY,
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


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "r10b2@test.com")
    _git(main, "config", "user.name", "r10b2")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r10-b2-branch"
    _git(main, "worktree", "add", str(exec_wt), "-b", branch, base_sha)
    return {
        "main": main,
        "exec_wt": exec_wt,
        "base_sha": base_sha,
        "branch": branch,
        "stores": tmp_path / "stores",
    }


def _agent(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_module, "PROPOSALS_DIR", tmp_path / "proposals")
    return AgentObsidure(api_base="http://127.0.0.1:1", verbose=False)


def _install_snapshot(agent: AgentObsidure, world, *, verdict_status="PASS", c278="CONTINUOUS", artifact_hash=None):
    request = RepairRequest(
        request_id="rr_r10b2",
        objective="repair target",
        failure_mode="BUILD_ERROR",
        summary="failure_mode=BUILD_ERROR",
        repo_targets=[TARGET],
        attempts_spent=2,
        error_contexts=[
            ErrorContextRecord(attempt=1, error_type="BUILD_ERROR", raw_details="first failure"),
            ErrorContextRecord(attempt=2, error_type="BUILD_ERROR", raw_details="second failure"),
        ],
        tests_hint=["repair-sandbox-verdict"],
        boundary=dict(REPAIR_BOUNDARY),
    )
    proposal = RepairProposal(
        proposal_id="rp_r10b2",
        request_id="rr_r10b2",
        rationale="repair target",
        candidate_files=[
            RepairCandidateFile(
                path=TARGET,
                full_content=AFTER,
                change_kind="MODIFY",
                base_sha256=_sha_file(world["exec_wt"] / TARGET),
                rationale="fix value",
            )
        ],
        tests_to_run=["repair-sandbox-verdict"],
        confidence="HIGH",
        boundary=dict(REPAIR_BOUNDARY),
    )
    verdict = RepairVerdict(
        verdict_id="rv_r10b2",
        request_id="rr_r10b2",
        proposal_id="rp_r10b2",
        status=verdict_status,
        tested_artifacts=[{"path": TARGET, "sha256": artifact_hash or _sha_text(AFTER)}],
        tests_executed=[{"command": "pytest", "status": "PASS"}],
        boundary=dict(REPAIR_BOUNDARY),
    )
    agent._last_repair_request = request
    agent._last_repair_proposal = proposal
    agent._last_proposal_meaning_validation = {
        "evidence": c278,
        "request_id": "rr_r10b2",
        "proposal_id": "rp_r10b2",
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": "KX108_ONLY",
    }
    agent._last_repair_verdict = verdict
    return request, proposal, verdict


def _prepare(agent, world, **kwargs):
    return agent.prepare_last_validated_repair(
        base_commit_sha=kwargs.pop("base_commit_sha", world["base_sha"]),
        repo_identity_ref=kwargs.pop("repo_identity_ref", "obsidia-openjarvis-install-v0"),
        execution_worktree_path=kwargs.pop("execution_worktree_path", world["exec_wt"]),
        main_worktree_path=kwargs.pop("main_worktree_path", world["main"]),
        branch_name=kwargs.pop("branch_name", world["branch"]),
        stores_base_dir=kwargs.pop("stores_base_dir", world["stores"]),
        session_id="r10-b2",
        **kwargs,
    )


def test_valid_repair_snapshot_reaches_r10_b1_and_b5_without_execution(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _install_snapshot(agent, world)
    before = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")

    out = _prepare(agent, world)

    assert out["status"] == "R10_REPAIR_PREPARED"
    assert out["prepared_action"]["status"] == PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["prepared_action"]["handoff_to_governed_prepare"] is True
    assert out["prepared_action"]["executor_invoked"] is False
    assert out["prepared_action"]["physical_mutation"] is False
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["kx108_called"] is False
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before


def test_missing_snapshot_and_missing_explicit_context_hold(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)

    out = _prepare(agent, world)
    assert out["status"] == "R10_REPAIR_HELD"
    assert out["reason"] == "REPAIR_REQUEST_MISSING"

    _install_snapshot(agent, world)
    out = _prepare(agent, world, base_commit_sha="")
    assert out["status"] == "R10_REPAIR_HELD"
    assert out["reason"] == "EXPLICIT_CONTEXT_MISSING"


def test_partial_blocked_and_noncontinuous_c278_hold(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)

    _install_snapshot(agent, world, verdict_status="PARTIAL")
    out = _prepare(agent, world)
    assert out["reason"] == "REPAIR_VERDICT_NOT_PASS"

    _install_snapshot(agent, world, verdict_status="BLOCKED")
    out = _prepare(agent, world)
    assert out["reason"] == "REPAIR_VERDICT_NOT_PASS"

    _install_snapshot(agent, world, c278="DIVERGENT")
    out = _prepare(agent, world)
    assert out["reason"] == "C278_NOT_CONTINUOUS"


def test_base_branch_revoked_budget_and_history_fail_closed(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _install_snapshot(agent, world)

    out = _prepare(agent, world, base_commit_sha="b" * 40)
    assert out["reason"] == "BASE_SHA_MISMATCH"

    out = _prepare(agent, world, branch_name="wrong-branch")
    assert out["reason"] == "BRANCH_MISMATCH"

    out = _prepare(agent, world, mission_context={"status": "REVOKED"})
    assert out["reason"] == "MISSION_REVOKED"

    out = _prepare(agent, world, repair_budget=2)
    assert out["status"] == "R10_REPAIR_STOPPED"
    assert out["reason"] == "REPAIR_BUDGET_EXHAUSTED"

    out = _prepare(agent, world, attempt_history=({"repair_request_id": "other", "agent_attempt": 1},))
    assert out["status"] == "R10_REPAIR_HELD"
    assert out["reason"] == "ATTEMPT_HISTORY_INCONSISTENT"

    out = _prepare(agent, world, attempt_history=({"agent_attempt": 99},))
    assert out["reason"] == "ATTEMPT_HISTORY_INCONSISTENT"


def test_repeated_failure_oscillation_and_tampered_evidence_hold(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _install_snapshot(agent, world)

    first = _prepare(agent, world)
    digest = first["stop_conditions"]["failure_digest"]
    patch_hash = first["tested_patch_hash"]

    out = _prepare(agent, world, attempt_history=({"failure_digest": digest},))
    assert out["status"] == "R10_REPAIR_STOPPED"
    assert out["reason"] == "REPEATED_IDENTICAL_FAILURE"

    out = _prepare(
        agent,
        world,
        attempt_history=(
            {"tested_patch_hash": patch_hash},
            {"tested_patch_hash": "b" * 64},
        ),
    )
    assert out["status"] == "R10_REPAIR_STOPPED"
    assert out["reason"] == "OSCILLATING_REPAIR_STATE"

    _install_snapshot(agent, world, artifact_hash="f" * 64)
    out = _prepare(agent, world)
    assert out["status"] == "R10_REPAIR_HELD"
    assert out["reason"] == "TESTED_PATCH_SUBSTITUTION"


def test_actual_agent_chronology_is_passed_to_r10_b1(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _install_snapshot(agent, world)

    import obsidure_repair_r9_adapter_v1 as adapter

    seen = {}

    def fake_adapter(**kwargs):
        seen.update(kwargs)
        return {
            "adapter_schema_version": "OBSIDURE_REPAIR_R9_ADAPTER_V1",
            "status": "R10_REPAIR_PREPARED",
            "executor_invoked": False,
            "physical_mutation": False,
        }

    monkeypatch.setattr(adapter, "adapt_validated_repair_to_r9_prepare", fake_adapter)

    out = _prepare(agent, world, attempt_history=({"agent_attempt": 2, "outcome": "RETRY_FAILED"},))

    assert out["status"] == "R10_REPAIR_PREPARED"
    history = seen["attempt_history"]
    assert history[0]["agent_attempt"] == 1
    assert history[0]["repair_request_id"] == "rr_r10b2"
    assert history[1]["agent_attempt"] == 2
    assert history[2]["outcome"] == "RETRY_FAILED"
    assert seen["repair_request"]["error_contexts"][0]["attempt"] == 1


def test_missing_tested_artifact_holds_before_handoff(tmp_path, monkeypatch):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _, _, verdict = _install_snapshot(agent, world)
    verdict.tested_artifacts.clear()

    out = _prepare(agent, world)

    assert out["status"] == "R10_REPAIR_HELD"
    assert out["reason"] == "TESTED_ARTIFACT_HASH_MISSING"
    assert out["handoff_created"] is False
