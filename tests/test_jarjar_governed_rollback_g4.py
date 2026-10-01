from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2
from jarjar_governed_rollback_bridge_v0 import (
    PREPARED_AWAITING_HUMAN_APPROVAL,
    ROLLBACK_EXECUTED_OK,
    governed_rollback_move_execute,
    governed_rollback_move_prepare,
)


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


@pytest.fixture
def world(tmp_path):
    main = tmp_path / "main"
    (main / "sub").mkdir(parents=True)
    (main / "sub" / "source.txt").write_bytes(b"rollback-me\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "g4@test.local")
    _git(main, "config", "user.name", "G4")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")

    exec_wt = tmp_path / "exec"
    _git(main, "worktree", "add", str(exec_wt), "-b", "g4-test", base_sha)

    stores = tmp_path / "stores"

    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _move(sa, da):
        da.parent.mkdir(parents=True, exist_ok=True)
        sa.rename(da)
        return {"ok": True, "error": None}

    ex.move_file.side_effect = _move

    prep = PC2.pc_v2_move_file_prepare(
        "sub/source.txt",
        "sub/moved.txt",
        execution_worktree_path=exec_wt,
        main_worktree_path=main,
        branch_name="g4-test",
        base_sha=base_sha,
        stores_base_dir=stores,
        session_id="g4-move",
    )
    result = PC2.pc_v2_move_file_execute(
        prep,
        prep["execution_authority_hash"],
        "HUMAN_G4_MOVE",
        stores_base_dir=stores,
        repo_root=exec_wt,
        session_id="g4-move",
        executor=ex,
    )
    assert result["status"] == PC2.EXECUTED_OK, result

    return {
        "main": main,
        "exec": exec_wt,
        "stores": stores,
        "sre_id": result["sealed_rollback_evidence_id"],
    }


def _rollback_executor():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _rollback(current, restore):
        current.rename(restore)
        return {"ok": True, "error": None}

    ex.rollback_move_file.side_effect = _rollback
    return ex


def test_prepare_is_non_mutating(world):
    w = world

    out = governed_rollback_move_prepare(
        w["sre_id"],
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
        session_id="g4-rb",
    )

    assert out["status"] == PREPARED_AWAITING_HUMAN_APPROVAL, out
    assert not (w["exec"] / "sub" / "source.txt").exists()
    assert (w["exec"] / "sub" / "moved.txt").exists()
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kx108_invocations_during_rollback"] == 0


def test_execute_requires_human_reference(world):
    w = world
    prepared = governed_rollback_move_prepare(
        w["sre_id"],
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
    )
    ex = _rollback_executor()

    out = governed_rollback_move_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "",
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        executor=ex,
        repo_root=w["exec"],
    )

    assert out["status"] != ROLLBACK_EXECUTED_OK
    ex.rollback_move_file.assert_not_called()


def test_execute_rejects_wrong_hash(world):
    w = world
    prepared = governed_rollback_move_prepare(
        w["sre_id"],
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
    )
    ex = _rollback_executor()

    out = governed_rollback_move_execute(
        prepared,
        "0" * 64,
        "HUMAN_G4_ROLLBACK",
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        executor=ex,
        repo_root=w["exec"],
    )

    assert out["status"] != ROLLBACK_EXECUTED_OK
    ex.rollback_move_file.assert_not_called()


def test_drift_after_prepare_blocks_before_executor(world):
    w = world
    prepared = governed_rollback_move_prepare(
        w["sre_id"],
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
    )
    (w["exec"] / "sub" / "moved.txt").write_bytes(b"drift\n")
    ex = _rollback_executor()

    out = governed_rollback_move_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "HUMAN_G4_ROLLBACK",
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        executor=ex,
        repo_root=w["exec"],
    )

    assert out["status"] != ROLLBACK_EXECUTED_OK
    assert "ROLLBACK_PRECONDITION_CHANGED" in out["reason"]
    ex.rollback_move_file.assert_not_called()


def test_execute_restores_original_path(world):
    w = world
    prepared = governed_rollback_move_prepare(
        w["sre_id"],
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
        session_id="g4-rb",
    )
    ex = _rollback_executor()

    out = governed_rollback_move_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "HUMAN_G4_ROLLBACK",
        sre_dir=w["stores"] / "sre",
        v2exec_dir=w["stores"] / "v2exec",
        executor=ex,
        repo_root=w["exec"],
        session_id="g4-rb",
    )

    assert out["status"] == ROLLBACK_EXECUTED_OK, out
    assert (w["exec"] / "sub" / "source.txt").read_bytes() == b"rollback-me\n"
    assert not (w["exec"] / "sub" / "moved.txt").exists()
    assert out["human_authorization_consumed"] is True
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kx108_invocations_during_rollback"] == 0
    assert out["executor_provider"] == "JARJAR"
