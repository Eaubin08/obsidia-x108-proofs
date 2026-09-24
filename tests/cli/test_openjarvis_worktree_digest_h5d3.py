from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import (
    obsidia_openjarvis_adapter_v0 as A,
)


def _git(
    repo: Path,
    *args: str,
):
    return subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )


def test_worktree_digest_changes_with_runtime_source(
    tmp_path,
):
    repo = tmp_path / "oj"

    repo.mkdir()

    _git(
        repo,
        "init",
    )

    _git(
        repo,
        "config",
        "user.email",
        "h5d3@example.invalid",
    )

    _git(
        repo,
        "config",
        "user.name",
        "H5D3",
    )

    tracked = repo / "tracked.txt"

    tracked.write_text(
        "base\n",
        encoding="utf-8",
    )

    _git(
        repo,
        "add",
        "tracked.txt",
    )

    _git(
        repo,
        "commit",
        "-m",
        "base",
    )

    clean = A._git_worktree_digest(
        repo
    )

    assert isinstance(
        clean,
        str,
    )

    assert len(clean) == 64

    tracked.write_text(
        "modified\n",
        encoding="utf-8",
    )

    modified = A._git_worktree_digest(
        repo
    )

    assert modified != clean

    untracked = repo / "new.txt"

    untracked.write_text(
        "one\n",
        encoding="utf-8",
    )

    with_untracked = (
        A._git_worktree_digest(
            repo
        )
    )

    assert with_untracked != modified

    untracked.write_text(
        "two\n",
        encoding="utf-8",
    )

    changed_untracked = (
        A._git_worktree_digest(
            repo
        )
    )

    assert (
        changed_untracked
        != with_untracked
    )


def test_trusted_worktree_digest_validation(
    tmp_path,
):
    trusted_session = (
        "jws-0123456789abcdef0123"
    )

    valid = "a" * 64

    adapter = (
        A.OpenJarvisObsidiaCognitivePilotAdapter(
            source_root=str(tmp_path),
            expected_commit=("0" * 40),
            trusted_session_id=trusted_session,
            trusted_worktree_digest=valid,
        )
    )

    assert (
        adapter.trusted_worktree_digest
        == valid
    )

    with pytest.raises(
        ValueError,
        match=(
            "TRUSTED_WORKTREE_DIGEST_INVALID"
        ),
    ):
        A.OpenJarvisObsidiaCognitivePilotAdapter(
            source_root=str(tmp_path),
            expected_commit=("0" * 40),
            trusted_session_id=trusted_session,
            trusted_worktree_digest="bad",
        )
