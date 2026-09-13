from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from obsidia_repair_execution_adapter_v0 import (
    OPERATION_TYPE,
    STATUS_EXEC_READY,
    STATUS_PREP_HOLD,
    prepare_repair_governed_execution,
)

import obsidia_branching_ledger as _L
import obsidia_batch_execution as _E


TARGET = "periphery/agents/foo.py"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def _make_git_worktrees(tmp_path: Path):
    if shutil.which("git") is None:
        pytest.skip("git unavailable")

    main = tmp_path / "main"
    main.mkdir()

    _git(main, "init")
    _git(main, "config", "user.email", "r3a@example.invalid")
    _git(main, "config", "user.name", "R3A Test")

    target = main / TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"x=1\n")

    _git(main, "add", ".")
    _git(main, "commit", "-m", "base")

    base_sha = _git(main, "rev-parse", "HEAD")

    execution = tmp_path / "execution-worktree"
    branch_name = "r3a-repair-exec"

    _git(
        main,
        "worktree",
        "add",
        "-b",
        branch_name,
        str(execution),
        base_sha,
    )

    assert _git(execution, "status", "--short") == ""

    return main, execution, branch_name, base_sha


def _make_handoff(tmp_path: Path, execution: Path):
    sandbox_file = tmp_path / "sandbox" / TARGET
    sandbox_file.parent.mkdir(parents=True, exist_ok=True)

    source_bytes = b"x=2\n"
    sandbox_file.write_bytes(source_bytes)

    target_bytes = (execution / TARGET).read_bytes()

    return {
        "status": "REPAIR_HANDOFF_READY",
        "reason": None,
        "proposal_id": "rp_r3a",
        "request_id": "rr_r3a",
        "verdict_id": "rv_r3a",
        "target_path": TARGET,
        "sandbox_artifact_path": str(sandbox_file.resolve()),
        "source_content_sha256": _sha(source_bytes),
        "source_bytes_len": len(source_bytes),
        "target_pre_sha256": _sha(target_bytes),
        "operation_type": OPERATION_TYPE,
        "operation_reason": "repair: " + TARGET,
        "provenance_refs": {
            "operation_type": OPERATION_TYPE,
            "repair_request_id": "rr_r3a",
            "repair_proposal_id": "rp_r3a",
            "repair_verdict_id": "rv_r3a",
            "c278_evidence": "CONTINUOUS",
        },
        "authority": "NON_SOVEREIGN",
        "write_capability": False,
    }


def test_r3a_real_pec_planned_child_and_eah(tmp_path):
    main, execution, branch_name, base_sha = _make_git_worktrees(tmp_path)
    handoff = _make_handoff(tmp_path, execution)

    before = (execution / TARGET).read_bytes()

    result = prepare_repair_governed_execution(
        handoff=handoff,
        execution_worktree_path=execution,
        main_worktree_path=main,
        branch_name=branch_name,
        base_sha=base_sha,
        ledger_dir=tmp_path / "ledger",
        selector_dir=tmp_path / "selector",
        execution_dir=tmp_path / "execution-store",
        pre_execution_context_dir=tmp_path / "pec",
    )

    assert result["status"] == STATUS_EXEC_READY, result
    assert result["write_capability"] is False
    assert result["target_mutated"] is False
    assert result["human_approval_present"] is False
    assert result["kx108_invoked"] is False

    assert result["pre_execution_context_id"]
    assert result["pre_execution_context_record_hash"]

    eah = result["execution_authority_hash"]
    assert len(eah) == 64
    assert all(c in "0123456789abcdef" for c in eah)

    assert result["source_kind"] == _L.SOURCE_KIND_FILESYSTEM
    assert result["source_content_sha256"] == handoff["source_content_sha256"]
    assert result["ledger_source_content_sha256"] == handoff["source_content_sha256"]
    assert result["target_pre_sha256"] == handoff["target_pre_sha256"]
    assert result["sha256_triple_assert"] == "PASS"

    # PREPARE must never mutate the target.
    assert (execution / TARGET).read_bytes() == before

    # Reload persisted envelope and prove canonical child state.
    env = _E._load_execution(
        result["batch_execution_id"],
        tmp_path / "execution-store",
    )
    assert env is not None
    assert env["integrity_verified"] is True
    assert env["execution_authority_hash"] == eah
    assert _E.compute_execution_authority_hash(env) == eah

    children = env["children"]
    assert len(children) == 1

    child = children[0]
    assert child["execution_status"] == _E.PLANNED
    assert child["operation_type"] == OPERATION_TYPE
    assert child["source_kind"] == _L.SOURCE_KIND_FILESYSTEM
    assert child["source_content_sha256"] == handoff["source_content_sha256"]
    assert child["target_pre_sha256"] == handoff["target_pre_sha256"]


def test_r3a_target_drift_after_handoff_fails_before_pec(tmp_path):
    main, execution, branch_name, base_sha = _make_git_worktrees(tmp_path)
    handoff = _make_handoff(tmp_path, execution)

    # Drift APRES l'observation du handoff.
    (execution / TARGET).write_bytes(b"x=999\n")

    result = prepare_repair_governed_execution(
        handoff=handoff,
        execution_worktree_path=execution,
        main_worktree_path=main,
        branch_name=branch_name,
        base_sha=base_sha,
        ledger_dir=tmp_path / "ledger",
        selector_dir=tmp_path / "selector",
        execution_dir=tmp_path / "execution-store",
        pre_execution_context_dir=tmp_path / "pec",
    )

    assert result["status"] == STATUS_PREP_HOLD
    assert result["reason"] == "TARGET_PRECONDITION_DRIFT_AFTER_HANDOFF"
    assert result["write_capability"] is False
    assert result["kx108_invoked"] is False


def test_filesystem_source_symlink_rejected(tmp_path):
    if not hasattr(Path, "symlink_to"):
        pytest.skip("symlink unsupported")

    real = tmp_path / "real.py"
    real.write_bytes(b"x=1\n")

    link = tmp_path / "linked.py"

    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")

    result = _L.register_filesystem_source(
        source_path=link,
        target_path=TARGET,
        ledger_dir=tmp_path / "ledger",
    )

    assert result["status"] == "REJECTED"
    assert result["reason"] == "FILESYSTEM_SOURCE_SYMLINK_REJECTED"
