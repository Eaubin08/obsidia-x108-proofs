from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(
    __file__
).resolve().parents[2]

BRIDGE = (
    ROOT
    / "scripts"
    / "obsidia_openjarvis_mcp_bridge_v0.py"
)


def _git(repo, *args):
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    _git(repo, "init")

    _git(
        repo,
        "config",
        "user.email",
        "mcp@example.invalid",
    )

    _git(
        repo,
        "config",
        "user.name",
        "MCP Test",
    )

    scripts = repo / "scripts"
    scripts.mkdir()

    target = (
        scripts
        / "obsidia_mcp_fixture.py"
    )

    target.write_text(
        '"""fixture"""\n\n'
        "VALUE = 1\n",
        encoding="utf-8",
    )

    _git(
        repo,
        "add",
        ".",
    )

    _git(
        repo,
        "commit",
        "-m",
        "fixture",
    )

    return repo


def _objective():
    spec = {
        "strategies": [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "OPENJARVIS MCP "
                    "SELF BUILD CANDIDATE ONLY"
                ),
            }
        ]
    }

    return (
        "Prepare a bounded peripheral "
        "tooling candidate. Candidate only. "
        "No apply. No commit. No push. "
        "No merge.\n"
        "NATIVE_SOLVE_JSON="
        + json.dumps(
            spec,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def test_mcp_bridge_static_surface():
    text = BRIDGE.read_text(
        encoding="utf-8",
    )

    assert (
        'tool_id = (\n'
        '        "obsidia_self_build_phase1"\n'
        "    )"
        in text
    )

    assert "shell_exec" not in text
    assert "file_write" not in text
    assert "git_commit" not in text


def test_real_openjarvis_mcp_loader_to_obsidia_phase1(
    tmp_path,
    monkeypatch,
):
    source = os.environ.get(
        "OBSIDIA_OPENJARVIS_SOURCE"
    )

    commit = os.environ.get(
        "OBSIDIA_OPENJARVIS_COMMIT"
    )

    if not source or not commit:
        pytest.skip(
            "real OpenJarvis source "
            "not configured"
        )

    repo = _repo(
        tmp_path
    )

    head = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    local = (
        tmp_path
        / "localappdata"
    )

    local.mkdir()

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(local),
    )

    monkeypatch.setenv(
        "OBSIDIA_CLI_REPO_ROOT",
        str(repo),
    )

    monkeypatch.setenv(
        "OBSIDIA_CLI_EXPECTED_HEAD",
        head,
    )

    source_src = (
        Path(source)
        / "src"
    )

    if str(source_src) not in sys.path:
        sys.path.insert(
            0,
            str(source_src),
        )

    from openjarvis.mcp.loader import (
        load_mcp_tools_from_config,
    )

    cfg = SimpleNamespace(
        enabled=True,
        servers=json.dumps(
            [
                {
                    "name": "obsidia",
                    "command": (
                        sys.executable
                    ),
                    "args": [
                        "-B",
                        str(BRIDGE),
                    ],
                    "include_tools": [
                        "obsidia_self_build_phase1"
                    ],
                }
            ]
        ),
    )

    before_head = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    before_status = _git(
        repo,
        "status",
        "--porcelain=v1",
    ).stdout

    tools, clients = (
        load_mcp_tools_from_config(
            cfg,
            allowed_names={
                "obsidia_self_build_phase1"
            },
        )
    )

    try:
        assert len(tools) == 1

        tool = tools[0]

        assert (
            tool.spec.name
            == "obsidia_self_build_phase1"
        )

        result = tool.execute(
            objective=_objective(),
            target_path=(
                "scripts/obsidia_mcp_fixture.py"
            ),
        )

        assert result.success is True

        payload = json.loads(
            result.content
        )

        assert (
            payload["mission_state"]
            == "MISSION_COMPLETE"
        )

        assert (
            payload["phase1_status"]
            == "PLAN_PROPOSED"
        )

        assert (
            payload["phase2_executed"]
            is False
        )

        assert (
            payload["repo_mutation"]
            is False
        )

        assert (
            payload["authority"]
            == "NONE"
        )

        assert (
            payload[
                "decision_authority"
            ]
            == "KX108_ONLY"
        )

        assert (
            "HUMAN_APPROVED_BUILD_SESSION="
            not in result.content
        )

    finally:
        for client in clients:
            client.close()

    after_head = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    after_status = _git(
        repo,
        "status",
        "--porcelain=v1",
    ).stdout

    assert after_head == before_head

    assert (
        after_status
        == before_status
        == ""
    )
