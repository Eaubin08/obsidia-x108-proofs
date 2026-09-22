from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "scripts"
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )

import obsidia_jarvis_workspace_binding_v0 as W


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            *args,
        ],
        capture_output=True,
        text=True,
        shell=False,
        check=True,
    )

    return proc.stdout.strip()


def _repo(
    root: Path,
    name: str,
) -> Path:
    repo = root / name
    repo.mkdir()

    _git(repo, "init")
    _git(
        repo,
        "config",
        "user.email",
        "test@example.invalid",
    )
    _git(
        repo,
        "config",
        "user.name",
        "Obsidia Test",
    )

    (repo / "README.md").write_text(
        name + "\n",
        encoding="utf-8",
    )

    _git(repo, "add", "README.md")
    _git(
        repo,
        "commit",
        "-m",
        "initial",
    )

    return repo.resolve()


def test_bind_is_idempotent(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path, "repo-a")

    first = W.bind_workspace(
        "brody",
        repo,
        state_path=state,
    )

    second = W.bind_workspace(
        "brody",
        repo,
        state_path=state,
    )

    assert (
        first["session_id"]
        == second["session_id"]
    )

    assert first["workspace"] == str(repo)
    assert first["active"] is True

    active = W.list_bindings(
        state_path=state,
        active_only=True,
    )

    assert len(active) == 1
    assert active[0]["label"] == "brody"

    assert first["authority"] == "NONE"
    assert (
        first["decision_authority"]
        == "KX108_ONLY"
    )
    assert (
        first["jarvis_memory_is_canonical"]
        is False
    )
    assert first["native_memory_write"] is False
    assert first["emits_act"] is False
    assert first["kernel_mutation"] is False


def test_same_workspace_cannot_have_two_active_sessions(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path, "repo-a")

    W.bind_workspace(
        "brody",
        repo,
        state_path=state,
    )

    with pytest.raises(
        W.WorkspaceBindingError,
        match="workspace already bound",
    ):
        W.bind_workspace(
            "other",
            repo,
            state_path=state,
        )


def test_same_label_cannot_move_while_active(
    tmp_path: Path,
):
    state = tmp_path / "state.json"

    repo_a = _repo(tmp_path, "repo-a")
    repo_b = _repo(tmp_path, "repo-b")

    W.bind_workspace(
        "trading",
        repo_a,
        state_path=state,
    )

    with pytest.raises(
        W.WorkspaceBindingError,
        match="session label already bound",
    ):
        W.bind_workspace(
            "trading",
            repo_b,
            state_path=state,
        )


def test_close_releases_workspace(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path, "repo-a")

    first = W.bind_workspace(
        "gps",
        repo,
        state_path=state,
    )

    closed = W.close_binding(
        first["session_id"],
        state_path=state,
    )

    assert closed["active"] is False
    assert closed["closed_at"]

    second = W.bind_workspace(
        "gps-next",
        repo,
        state_path=state,
    )

    assert second["active"] is True
    assert (
        second["session_id"]
        != first["session_id"]
    )


def test_resolve_by_label_and_session_id(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path, "repo-a")

    binding = W.bind_workspace(
        "jarvis",
        repo,
        state_path=state,
    )

    by_label = W.resolve_binding(
        "jarvis",
        state_path=state,
    )

    by_id = W.resolve_binding(
        binding["session_id"],
        state_path=state,
    )

    assert by_label == by_id


def test_non_git_directory_is_rejected(
    tmp_path: Path,
):
    plain = tmp_path / "plain"
    plain.mkdir()

    with pytest.raises(
        W.WorkspaceBindingError,
    ):
        W.inspect_workspace(plain)


def test_subdirectory_is_rejected(
    tmp_path: Path,
):
    repo = _repo(tmp_path, "repo-a")
    child = repo / "child"
    child.mkdir()

    with pytest.raises(
        W.WorkspaceBindingError,
        match="workspace must be",
    ):
        W.inspect_workspace(child)
