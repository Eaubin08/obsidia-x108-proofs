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


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


@pytest.fixture
def world(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "g3@test.local")
    _git(main, "config", "user.name", "G3")
    (main / "a.txt").write_bytes(b"before\n")
    _git(main, "add", "a.txt")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec"
    _git(main, "worktree", "add", str(exec_wt), "-b", "g3-test", base_sha)
    return {
        "main": main,
        "exec": exec_wt,
        "stores": tmp_path / "stores",
        "base_sha": base_sha,
    }


def _create_prepare(w):
    return PC2.pc_v2_create_file_prepare(
        "new.txt",
        b"hello g3\n",
        execution_worktree_path=w["exec"],
        main_worktree_path=w["main"],
        branch_name="g3-test",
        base_sha=w["base_sha"],
        stores_base_dir=w["stores"],
        session_id="g3-create",
    )


def _patch_text():
    return """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-before
+after
"""


def _patch_prepare(w):
    return PC2.pc_v2_apply_patch_prepare(
        _patch_text(),
        execution_worktree_path=w["exec"],
        main_worktree_path=w["main"],
        branch_name="g3-test",
        base_sha=w["base_sha"],
        stores_base_dir=w["stores"],
        session_id="g3-patch",
    )


def _executor():
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeFilesystemBackend"

    def create_file(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {"ok": True, "error": None}

    def apply_patch(repo_root, patch_content, target_paths):
        p = subprocess.run(
            ["git", "apply", "-"],
            cwd=str(repo_root),
            input=patch_content.encode("utf-8"),
            capture_output=True,
        )
        return {
            "ok": p.returncode == 0,
            "error": p.stderr.decode("utf-8", errors="replace"),
        }

    ex.create_file.side_effect = create_file
    ex.apply_patch.side_effect = apply_patch
    return ex


def test_create_file_prepare_never_calls_executor(world):
    ex = _executor()
    out = _create_prepare(world)
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert not (world["exec"] / "new.txt").exists()
    ex.create_file.assert_not_called()


def test_create_file_execute_via_jarjar_executor(world):
    ex = _executor()
    out = _create_prepare(world)
    result = PC2.pc_v2_create_file_execute(
        out,
        out["execution_authority_hash"],
        "HUMAN_G3_CREATE",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
        session_id="g3-create",
        executor=ex,
    )
    assert result["status"] == PC2.EXECUTED_OK, result
    ex.create_file.assert_called_once()
    assert (world["exec"] / "new.txt").read_bytes() == b"hello g3\n"
    assert result["executor_provider"] == "JARJAR"
    assert result["executor_backend"] == "NativeFilesystemBackend"


def test_create_file_bad_eah_blocks_before_executor(world):
    ex = _executor()
    out = _create_prepare(world)
    result = PC2.pc_v2_create_file_execute(
        out,
        "0" * 64,
        "HUMAN_G3_CREATE",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
        executor=ex,
    )
    assert result["status"] != PC2.EXECUTED_OK
    ex.create_file.assert_not_called()
    assert not (world["exec"] / "new.txt").exists()


def test_create_file_fallback_unchanged(world):
    out = _create_prepare(world)
    result = PC2.pc_v2_create_file_execute(
        out,
        out["execution_authority_hash"],
        "HUMAN_G3_CREATE_NATIVE",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
    )
    assert result["status"] == PC2.EXECUTED_OK, result
    assert result["executor_provider"] == "OS_NATIVE"
    assert result["executor_backend"] == "atomic_path_write"


def test_apply_patch_prepare_never_calls_executor(world):
    ex = _executor()
    out = _patch_prepare(world)
    assert out["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    assert (world["exec"] / "a.txt").read_bytes() == b"before\n"
    ex.apply_patch.assert_not_called()


def test_apply_patch_execute_via_jarjar_executor(world):
    ex = _executor()
    out = _patch_prepare(world)
    result = PC2.pc_v2_apply_patch_execute(
        out,
        out["execution_authority_hash"],
        "HUMAN_G3_PATCH",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
        session_id="g3-patch",
        executor=ex,
    )
    assert result["status"] == PC2.EXECUTED_OK, result
    ex.apply_patch.assert_called_once()
    assert (world["exec"] / "a.txt").read_bytes() == b"after\n"
    assert result["executor_provider"] == "JARJAR"
    assert result["executor_backend"] == "NativeFilesystemBackend"


def test_apply_patch_bad_eah_blocks_before_executor(world):
    ex = _executor()
    out = _patch_prepare(world)
    result = PC2.pc_v2_apply_patch_execute(
        out,
        "0" * 64,
        "HUMAN_G3_PATCH",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
        executor=ex,
    )
    assert result["status"] != PC2.EXECUTED_OK
    ex.apply_patch.assert_not_called()
    assert (world["exec"] / "a.txt").read_text(encoding="utf-8") == "before\n"


def test_apply_patch_fallback_unchanged(world):
    out = _patch_prepare(world)
    result = PC2.pc_v2_apply_patch_execute(
        out,
        out["execution_authority_hash"],
        "HUMAN_G3_PATCH_NATIVE",
        stores_base_dir=world["stores"],
        repo_root=world["exec"],
    )
    assert result["status"] == PC2.EXECUTED_OK, result
    assert (world["exec"] / "a.txt").read_text(encoding="utf-8") == "after\n"
    assert result["executor_provider"] == "OS_NATIVE"
    assert result["executor_backend"] == "git.apply"
