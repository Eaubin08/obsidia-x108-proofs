"""
R8-B2 — real candidate resume KX108.

Proofs:
- cmd_resume_kx108 itself has zero SYNTHETIC_* dependency;
- real candidate diff identity is exact;
- scope drift blocks before KX108;
- recorded pytest evidence is replayed;
- arbitrary commands are rejected;
- resume creates no new worktree and no commit.
"""

from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import obsidia_build as B

from obsidia_candidate_patch_v1 import (
    bind_candidate_to_objective,
    load_candidate_patch_file,
)


PATCH = """diff --git a/periphery/demo.py b/periphery/demo.py
--- a/periphery/demo.py
+++ b/periphery/demo.py
@@ -1 +1 @@
-VALUE = "old"
+VALUE = "new"
"""


def git(
    repo: Path,
    *args: str,
) -> subprocess.CompletedProcess:

    return subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def make_repo(
    tmp_path: Path,
) -> Path:

    repo = (
        tmp_path
        / "repo"
    )

    repo.mkdir()

    git(
        repo,
        "init",
    )

    (
        repo
        / "periphery"
    ).mkdir()

    (
        repo
        / "tests"
    ).mkdir()

    (
        repo
        / "periphery"
        / "demo.py"
    ).write_text(
        'VALUE = "old"\n',
        encoding="utf-8",
    )

    (
        repo
        / "tests"
        / "test_demo.py"
    ).write_text(
        "from pathlib import Path\n"
        "\n"
        "def test_demo():\n"
        "    text = Path('periphery/demo.py').read_text()\n"
        "    assert 'VALUE = \"new\"' in text\n",
        encoding="utf-8",
    )

    git(
        repo,
        "add",
        ".",
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Obsidia Test",
            "-c",
            "user.email=obsidia@test.local",
            "commit",
            "-m",
            "base",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    return repo


def cleanup(
    repo: Path,
    worktree: Path,
) -> None:

    if worktree.exists():

        subprocess.run(
            [
                "git",
                "worktree",
                "remove",
                "--force",
                str(worktree),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
        )


def make_blocked_session(
    tmp_path: Path,
    monkeypatch,
):

    repo = make_repo(
        tmp_path
    )

    state = (
        tmp_path
        / "state"
    )

    candidate_path = (
        tmp_path
        / "candidate.patch"
    )

    candidate_path.write_text(
        PATCH,
        encoding="utf-8",
    )

    spec = load_candidate_patch_file(
        candidate_path,
        repo,
    )

    objective = bind_candidate_to_objective(
        "R8-B2 real resume",
        spec,
    )

    plan = B.compute_plan(
        objective,
        B.get_base_sha(
            repo
        ),
        repo,
        explicit_scope=list(
            spec.files
        ),
    )

    monkeypatch.setattr(
        B,
        "_call_kx108",
        lambda *args, **kwargs: (
            "BLOCKED_KX108_UNAVAILABLE",
            {},
        ),
    )

    B.cmd_execute(
        objective,
        plan[
            "next_human_action"
        ],
        repo_root=repo,
        state_dir=state,
        explicit_scope=list(
            spec.files
        ),
        candidate_patch_spec=spec,
    )

    worktree = (
        repo.parent
        / plan[
            "worktree_proposal"
        ]
    )

    receipt_path = (
        state
        / plan["session_id"]
        / "receipt.json"
    )

    assert worktree.exists()
    assert receipt_path.exists()

    receipt = json.loads(
        receipt_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        receipt[
            "candidate_patch_mode"
        ]
        == "REAL_UNIFIED_DIFF_V1"
    )

    assert receipt[
        "candidate_patch_files"
    ] == [
        "periphery/demo.py"
    ]

    assert receipt.get(
        "tests_commands"
    ), receipt

    return (
        repo,
        state,
        plan,
        worktree,
        receipt_path,
    )


def test_resume_body_has_zero_synthetic_identifiers():

    source = inspect.getsource(
        B.cmd_resume_kx108
    )

    for forbidden in (
        "SYNTHETIC_TARGET",
        "SYNTHETIC_MARKER",
        "SYNTHETIC_TEST_PY",
    ):
        assert forbidden not in source


def test_real_resume_revalidates_then_calls_kx108(
    tmp_path,
    monkeypatch,
):

    (
        repo,
        state,
        plan,
        worktree,
        receipt_path,
    ) = make_blocked_session(
        tmp_path,
        monkeypatch,
    )

    try:

        head_before = git(
            worktree,
            "rev-parse",
            "HEAD",
        ).stdout.strip()

        worktrees_before = git(
            repo,
            "worktree",
            "list",
            "--porcelain",
        ).stdout

        calls = []

        def act(
            *args,
            **kwargs,
        ):
            calls.append(1)

            return (
                "ACT",
                {
                    "action": "ACT",
                },
            )

        monkeypatch.setattr(
            B,
            "_call_kx108",
            act,
        )

        rc = B.cmd_resume_kx108(
            plan[
                "session_id"
            ],
            repo_root=repo,
            state_dir=state,
        )

        assert rc == 0
        assert calls == [1]

        assert (
            git(
                worktree,
                "rev-parse",
                "HEAD",
            ).stdout.strip()
            == head_before
        )

        assert (
            git(
                repo,
                "worktree",
                "list",
                "--porcelain",
            ).stdout
            == worktrees_before
        )

        receipt = json.loads(
            receipt_path.read_text(
                encoding="utf-8"
            )
        )

        assert (
            receipt[
                "kx108_decision"
            ]
            == "ACT"
        )

        assert receipt.get(
            "resume_tests_results"
        )

        assert all(
            result["ok"]
            for result
            in receipt[
                "resume_tests_results"
            ]
        )

    finally:
        cleanup(
            repo,
            worktree,
        )


def test_real_diff_tamper_blocks_before_kx108(
    tmp_path,
    monkeypatch,
):

    (
        repo,
        state,
        plan,
        worktree,
        receipt_path,
    ) = make_blocked_session(
        tmp_path,
        monkeypatch,
    )

    try:

        target = (
            worktree
            / "periphery"
            / "demo.py"
        )

        target.write_text(
            'VALUE = "tampered"\n',
            encoding="utf-8",
        )

        git(
            worktree,
            "add",
            "periphery/demo.py",
        )

        calls = []

        def forbidden_call(
            *args,
            **kwargs,
        ):
            calls.append(1)
            return ("ACT", {})

        monkeypatch.setattr(
            B,
            "_call_kx108",
            forbidden_call,
        )

        rc = B.cmd_resume_kx108(
            plan[
                "session_id"
            ],
            repo_root=repo,
            state_dir=state,
        )

        assert rc == 2
        assert calls == []

        receipt = json.loads(
            receipt_path.read_text(
                encoding="utf-8"
            )
        )

        assert (
            receipt[
                "first_failure"
            ]
            == "RESUME_REAL_CANDIDATE_DIFF_HASH_MISMATCH"
        )

    finally:
        cleanup(
            repo,
            worktree,
        )


def test_real_scope_drift_blocks_before_kx108(
    tmp_path,
    monkeypatch,
):

    (
        repo,
        state,
        plan,
        worktree,
        _,
    ) = make_blocked_session(
        tmp_path,
        monkeypatch,
    )

    try:

        (
            worktree
            / "OUT_OF_SCOPE.txt"
        ).write_text(
            "scope drift\n",
            encoding="utf-8",
        )

        calls = []

        def forbidden_call(
            *args,
            **kwargs,
        ):
            calls.append(1)
            return ("ACT", {})

        monkeypatch.setattr(
            B,
            "_call_kx108",
            forbidden_call,
        )

        rc = B.cmd_resume_kx108(
            plan[
                "session_id"
            ],
            repo_root=repo,
            state_dir=state,
        )

        assert rc == 2
        assert calls == []

    finally:
        cleanup(
            repo,
            worktree,
        )


@pytest.mark.parametrize(
    "command",
    [
        "python dangerous.py",
        "python -m pytest tests/ -q && echo BAD",
        "git status",
        "python -m unittest tests",
    ],
)
def test_non_pytest_or_shell_command_rejected(
    command,
):

    with pytest.raises(
        ValueError
    ):
        B._resume_recorded_pytest_argv(
            command
        )
