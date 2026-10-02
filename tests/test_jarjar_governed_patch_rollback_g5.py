from __future__ import annotations

import hashlib
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
from jarjar_governed_patch_rollback_bridge_v0 import (
    PREPARED_AWAITING_HUMAN_APPROVAL,
    ROLLBACK_EXECUTED_OK,
    governed_rollback_patch_execute,
    governed_rollback_patch_prepare,
)


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


@pytest.fixture
def world(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    target = main / "target.txt"
    target.write_bytes(b"before\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "g5@test.local")
    _git(main, "config", "user.name", "G5")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")

    exec_wt = tmp_path / "exec"
    _git(main, "worktree", "add", str(exec_wt), "-b", "g5-test", base_sha)
    stores = tmp_path / "stores"

    patch = (
        "--- a/target.txt\n"
        "+++ b/target.txt\n"
        "@@ -1 +1 @@\n"
        "-before\n"
        "+after\n"
    )

    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _apply(repo_root, patch_content, target_paths):
        assert target_paths == ["target.txt"]
        (Path(repo_root) / "target.txt").write_bytes(b"after\n")
        return {"ok": True, "error": None}

    ex.apply_patch.side_effect = _apply

    prep = PC2.pc_v2_apply_patch_prepare(
        patch,
        execution_worktree_path=exec_wt,
        main_worktree_path=main,
        branch_name="g5-test",
        base_sha=base_sha,
        stores_base_dir=stores,
        session_id="g5-patch",
    )
    result = PC2.pc_v2_apply_patch_execute(
        prep,
        prep["execution_authority_hash"],
        "HUMAN_G5_PATCH",
        stores_base_dir=stores,
        repo_root=exec_wt,
        session_id="g5-patch",
        executor=ex,
    )
    assert result["status"] == PC2.EXECUTED_OK, result
    assert len(result["sealed_rollback_evidence_ids"]) == 1

    return {
        "main": main,
        "exec": exec_wt,
        "stores": stores,
        "sre_id": result["sealed_rollback_evidence_ids"][0],
        "sar_id": result["sealed_apply_receipt_id"],
    }


def _rollback_executor():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _restore(target, restore_content, expected_current_sha256):
        current = target.read_bytes()
        if hashlib.sha256(current).hexdigest() != expected_current_sha256:
            return {"ok": False, "error": "rollback target drifted"}
        target.write_bytes(restore_content)
        return {
            "ok": True,
            "error": None,
            "executor": "NativeFilesystemBackend",
            "data": {"restored_sha256": hashlib.sha256(restore_content).hexdigest()},
        }

    ex.restore_file_bytes_guarded.side_effect = _restore
    return ex


def _prepare(w):
    return governed_rollback_patch_prepare(
        w["sre_id"],
        w["sar_id"],
        sre_dir=w["stores"] / "sre",
        sar_dir=w["stores"] / "sar",
        v2exec_dir=w["stores"] / "v2exec",
        repo_root=w["exec"],
        session_id="g5-rb",
    )


def test_prepare_is_non_mutating(world):
    out = _prepare(world)
    assert out["status"] == PREPARED_AWAITING_HUMAN_APPROVAL, out
    assert (world["exec"] / "target.txt").read_bytes() == b"after\n"
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kx108_invocations_during_rollback"] == 0


def test_execute_requires_human_reference(world):
    prepared = _prepare(world)
    ex = _rollback_executor()
    out = governed_rollback_patch_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "",
        sre_dir=world["stores"] / "sre",
        sar_dir=world["stores"] / "sar",
        v2exec_dir=world["stores"] / "v2exec",
        executor=ex,
        repo_root=world["exec"],
    )
    assert out["status"] != ROLLBACK_EXECUTED_OK
    ex.restore_file_bytes_guarded.assert_not_called()


def test_drift_after_prepare_blocks_before_executor(world):
    prepared = _prepare(world)
    (world["exec"] / "target.txt").write_bytes(b"drift\n")
    ex = _rollback_executor()
    out = governed_rollback_patch_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "HUMAN_G5_ROLLBACK",
        sre_dir=world["stores"] / "sre",
        sar_dir=world["stores"] / "sar",
        v2exec_dir=world["stores"] / "v2exec",
        executor=ex,
        repo_root=world["exec"],
    )
    assert out["status"] != ROLLBACK_EXECUTED_OK
    assert "ROLLBACK_PRECONDITION_CHANGED" in out["reason"]
    ex.restore_file_bytes_guarded.assert_not_called()


def test_execute_restores_exact_preimage(world):
    prepared = _prepare(world)
    ex = _rollback_executor()
    out = governed_rollback_patch_execute(
        prepared,
        prepared["rollback_authority_hash"],
        "HUMAN_G5_ROLLBACK",
        sre_dir=world["stores"] / "sre",
        sar_dir=world["stores"] / "sar",
        v2exec_dir=world["stores"] / "v2exec",
        executor=ex,
        repo_root=world["exec"],
        session_id="g5-rb",
    )
    assert out["status"] == ROLLBACK_EXECUTED_OK, out
    assert (world["exec"] / "target.txt").read_bytes() == b"before\n"
    assert out["restored_sha256"] == hashlib.sha256(b"before\n").hexdigest()
    assert out["human_authorization_consumed"] is True
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kx108_invocations_during_rollback"] == 0


def test_multifile_patch_is_explicitly_deferred(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    (main / "a.txt").write_bytes(b"a\n")
    (main / "b.txt").write_bytes(b"b\n")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "g5@test.local")
    _git(main, "config", "user.name", "G5")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec"
    _git(main, "worktree", "add", str(exec_wt), "-b", "g5-multi", base_sha)
    stores = tmp_path / "stores"

    patch = (
        "--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-a\n+A\n"
        "--- a/b.txt\n+++ b/b.txt\n@@ -1 +1 @@\n-b\n+B\n"
    )
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def _apply(repo_root, patch_content, target_paths):
        (Path(repo_root) / "a.txt").write_bytes(b"A\n")
        (Path(repo_root) / "b.txt").write_bytes(b"B\n")
        return {"ok": True, "error": None}

    ex.apply_patch.side_effect = _apply
    prep = PC2.pc_v2_apply_patch_prepare(
        patch,
        execution_worktree_path=exec_wt,
        main_worktree_path=main,
        branch_name="g5-multi",
        base_sha=base_sha,
        stores_base_dir=stores,
    )
    result = PC2.pc_v2_apply_patch_execute(
        prep,
        prep["execution_authority_hash"],
        "HUMAN_G5_PATCH",
        stores_base_dir=stores,
        repo_root=exec_wt,
        executor=ex,
    )
    assert result["status"] == PC2.EXECUTED_OK
    out = governed_rollback_patch_prepare(
        result["sealed_rollback_evidence_ids"][0],
        result["sealed_apply_receipt_id"],
        sre_dir=stores / "sre",
        sar_dir=stores / "sar",
        v2exec_dir=stores / "v2exec",
        repo_root=exec_wt,
    )
    assert out["status"] != PREPARED_AWAITING_HUMAN_APPROVAL
    assert out["reason"] == "G5A_SINGLE_TARGET_REQUIRED"
