from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "scripts"
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_jarvis_workspace_binding_v0 as B
import obsidia_jarvis_workspace_launcher_v0 as L


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    return proc.stdout.strip()


def _repo(root: Path) -> Path:
    repo = root / "workspace"
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
        "workspace\n",
        encoding="utf-8",
    )

    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")

    return repo.resolve()


def _oj(root: Path) -> Path:
    oj = root / "openjarvis"
    (oj / "src").mkdir(parents=True)
    return oj.resolve()


def test_prepare_builds_native_chat_plan(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path)
    oj = _oj(tmp_path)

    binding = B.bind_workspace(
        "brody",
        repo,
        state_path=state,
    )

    plan = L.build_launch_plan(
        "brody",
        state_path=state,
        openjarvis_source=str(oj),
        openjarvis_commit="abc123",
    )

    assert plan["status"] == "READY_PREPARE_ONLY"

    assert (
        plan["session_id"]
        == binding["session_id"]
    )

    assert plan["workspace"] == str(repo)

    assert plan["native_cli"]["cwd"] == str(repo)

    assert plan["native_cli"]["argv"] == [
        "python",
        "-m",
        "openjarvis.cli",
        "chat",
    ]


def test_prepare_exports_session_and_workspace(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path)
    oj = _oj(tmp_path)

    B.bind_workspace(
        "trading",
        repo,
        state_path=state,
    )

    plan = L.build_launch_plan(
        "trading",
        state_path=state,
        openjarvis_source=str(oj),
        openjarvis_commit="abc123",
    )

    env = plan["native_cli"]["environment"]

    assert (
        env["OBSIDIA_JARVIS_SESSION_LABEL"]
        == "trading"
    )

    assert (
        env["OBSIDIA_JARVIS_WORKSPACE"]
        == str(repo)
    )

    assert (
        env["OBSIDIA_OPENJARVIS_COMMIT"]
        == "abc123"
    )


def test_native_cli_remains_blocked(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path)
    oj = _oj(tmp_path)

    B.bind_workspace(
        "gps",
        repo,
        state_path=state,
    )

    out = L.launch_workspace(
        "gps",
        state_path=state,
        openjarvis_source=str(oj),
        openjarvis_commit="abc123",
    )

    assert out["status"] == "BLOCKED"
    assert out["launch_attempted"] is False
    assert out["launch_executed"] is False

    assert out["cognitive_cli_bound"] is False
    assert out["real_launch_enabled"] is False


def test_authority_boundary(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path)
    oj = _oj(tmp_path)

    B.bind_workspace(
        "jarvis",
        repo,
        state_path=state,
    )

    plan = L.build_launch_plan(
        "jarvis",
        state_path=state,
        openjarvis_source=str(oj),
        openjarvis_commit="abc123",
    )

    assert plan["authority"] == "NONE"
    assert plan["openjarvis_authority"] == "NONE"

    assert (
        plan["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        plan["openjarvis_model_selection"]
        is False
    )

    assert plan["workspace_mutation"] is False
    assert plan["native_memory_write"] is False
    assert plan["emits_act"] is False
    assert plan["kernel_mutation"] is False


def test_missing_session_fails_closed(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    oj = _oj(tmp_path)

    try:
        L.build_launch_plan(
            "missing",
            state_path=state,
            openjarvis_source=str(oj),
            openjarvis_commit="abc123",
        )
    except L.WorkspaceBindingError:
        pass
    else:
        raise AssertionError(
            "missing session must fail"
        )


def test_missing_openjarvis_source_fails(
    tmp_path: Path,
):
    state = tmp_path / "state.json"
    repo = _repo(tmp_path)

    B.bind_workspace(
        "brody",
        repo,
        state_path=state,
    )

    try:
        L.build_launch_plan(
            "brody",
            state_path=state,
            openjarvis_source=str(
                tmp_path / "missing"
            ),
            openjarvis_commit="abc123",
        )
    except L.WorkspaceLauncherError:
        pass
    else:
        raise AssertionError(
            "missing OpenJarvis source must fail"
        )
