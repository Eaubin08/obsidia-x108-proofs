"""
R8-C2 — TOOLING_ENGINEERING_V1 candidate producer.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(
    __file__
).resolve().parents[1]

SCRIPTS = ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPTS),
    )


import obsidure_tooling_candidate_v1 as C


def git(
    repo: Path,
    *args: str,
) -> str:

    proc = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    return proc.stdout.strip()


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

    git(
        repo,
        "config",
        "core.autocrlf",
        "true",
    )

    files = {
        (
            "scripts/"
            "obsidia_build.py"
        ): (
            'VALUE = "old"\r\n'
        ),

        (
            "scripts/"
            "obsidia_cli.py"
        ): (
            'CLI = "old"\r\n'
        ),

        (
            "scripts/gates/"
            "danger.py"
        ): (
            'GATE = "sealed"\r\n'
        ),

        (
            "tests/"
            "test_build.py"
        ): (
            'EXPECTED = "old"\r\n'
        ),

        (
            "periphery/"
            "demo.py"
        ): (
            'P = "old"\r\n'
        ),
    }

    for rel, content in (
        files.items()
    ):

        path = (
            repo
            / rel
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            content.encode(
                "utf-8"
            )
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


def outside_source(
    tmp_path: Path,
    name: str,
    content: str,
) -> Path:

    root = (
        tmp_path
        / "external_sources"
    )

    root.mkdir(
        exist_ok=True
    )

    path = (
        root
        / name
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path


def test_scripts_and_test_cotarget_candidate(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    build_source = outside_source(
        tmp_path,
        "build.py",
        'VALUE = "new"\n',
    )

    test_source = outside_source(
        tmp_path,
        "test.py",
        'EXPECTED = "new"\n',
    )

    candidate = C.produce_candidate(
        repo,
        "R8-C2 proof",
        [
            (
                "scripts/obsidia_build.py",
                build_source,
            ),
            (
                "tests/test_build.py",
                test_source,
            ),
        ],
        tmp_path
        / "artifacts",
    )

    assert candidate.files == (
        "scripts/obsidia_build.py",
        "tests/test_build.py",
    )

    raw = (
        candidate
        .patch_path
        .read_bytes()
    )

    assert (
        hashlib.sha256(
            raw
        ).hexdigest()
        == candidate.patch_sha256
    )


def test_build_phase1_exact_scope_and_zero_worktree(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    source = outside_source(
        tmp_path,
        "build.py",
        'VALUE = "new"\n',
    )

    candidate = C.produce_candidate(
        repo,
        "modify tooling",
        [
            (
                "scripts/obsidia_build.py",
                source,
            )
        ],
        tmp_path
        / "artifacts",
    )

    before = git(
        repo,
        "worktree",
        "list",
        "--porcelain",
    )

    plan = C.build_phase1_plan(
        repo,
        candidate,
    )

    after = git(
        repo,
        "worktree",
        "list",
        "--porcelain",
    )

    assert (
        plan["status"]
        == "PLAN_PROPOSED"
    )

    assert (
        plan["scope_mode"]
        == "EXPLICIT_CHILD_TARGET"
    )

    assert (
        plan[
            "approved_scope_proposal"
        ]
        == [
            "scripts/obsidia_build.py"
        ]
    )

    assert (
        plan[
            "candidate_patch_hash"
        ]
        == candidate.patch_sha256
    )

    assert (
        plan[
            "candidate_producer_authority"
        ]
        == "NONE"
    )

    assert before == after


@pytest.mark.parametrize(
    "target",
    [
        "periphery/demo.py",
        "scripts/gates/danger.py",
        "proofs/V18_x.json",
        "../scripts/obsidia_build.py",
    ],
)
def test_non_tooling_or_protected_target_rejected(
    tmp_path,
    target,
):

    source = outside_source(
        tmp_path,
        "x.py",
        "X = 1\n",
    )

    with pytest.raises(
        C.ToolingCandidateError
    ):
        C.produce_candidate(
            make_repo(
                tmp_path
            ),
            "bad target",
            [
                (
                    target,
                    source,
                )
            ],
            tmp_path
            / "artifacts",
        )


def test_tests_only_candidate_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    source = outside_source(
        tmp_path,
        "test.py",
        'EXPECTED = "new"\n',
    )

    with pytest.raises(
        C.ToolingCandidateError,
        match=(
            "REQUIRES_SCRIPT_TARGET"
        ),
    ):
        C.produce_candidate(
            repo,
            "tests only",
            [
                (
                    "tests/test_build.py",
                    source,
                )
            ],
            tmp_path
            / "artifacts",
        )


def test_new_script_rejected_modification_only(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    source = outside_source(
        tmp_path,
        "new.py",
        "X = 1\n",
    )

    with pytest.raises(
        C.ToolingCandidateError,
        match=(
            "TOOLING_MODIFICATION_ONLY"
        ),
    ):
        C.produce_candidate(
            repo,
            "new file",
            [
                (
                    "scripts/obsidia_new.py",
                    source,
                )
            ],
            tmp_path
            / "artifacts",
        )


def test_source_inside_repo_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    inside = (
        repo
        / "source.py"
    )

    inside.write_text(
        'VALUE = "new"\n',
        encoding="utf-8",
    )

    with pytest.raises(
        C.ToolingCandidateError,
        match=(
            "SOURCE_MUST_BE_OUTSIDE_REPO"
        ),
    ):
        C.produce_candidate(
            repo,
            "inside source",
            [
                (
                    "scripts/obsidia_build.py",
                    inside,
                )
            ],
            tmp_path
            / "outside",
        )


def test_dirty_target_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    target = (
        repo
        / "scripts"
        / "obsidia_build.py"
    )

    target.write_text(
        'VALUE = "dirty"\n',
        encoding="utf-8",
    )

    source = outside_source(
        tmp_path,
        "build.py",
        'VALUE = "new"\n',
    )

    with pytest.raises(
        C.ToolingCandidateError,
        match="TOOLING_BASE_DIRTY",
    ):
        C.produce_candidate(
            repo,
            "dirty",
            [
                (
                    "scripts/obsidia_build.py",
                    source,
                )
            ],
            tmp_path
            / "outside",
        )


def test_candidate_content_changes_approval_identity(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    source_a = outside_source(
        tmp_path,
        "a.py",
        'VALUE = "a"\n',
    )

    source_b = outside_source(
        tmp_path,
        "b.py",
        'VALUE = "b"\n',
    )

    a = C.produce_candidate(
        repo,
        "same objective",
        [
            (
                "scripts/obsidia_build.py",
                source_a,
            )
        ],
        tmp_path
        / "a-artifacts",
    )

    b = C.produce_candidate(
        repo,
        "same objective",
        [
            (
                "scripts/obsidia_build.py",
                source_b,
            )
        ],
        tmp_path
        / "b-artifacts",
    )

    plan_a = C.build_phase1_plan(
        repo,
        a,
    )

    plan_b = C.build_phase1_plan(
        repo,
        b,
    )

    assert (
        a.patch_sha256
        != b.patch_sha256
    )

    assert (
        plan_a["session_id"]
        != plan_b["session_id"]
    )

    assert (
        plan_a[
            "next_human_action"
        ]
        != plan_b[
            "next_human_action"
        ]
    )


def test_output_inside_repo_rejected(
    tmp_path,
):

    repo = make_repo(
        tmp_path
    )

    source = outside_source(
        tmp_path,
        "build.py",
        'VALUE = "new"\n',
    )

    with pytest.raises(
        C.ToolingCandidateError,
        match=(
            "OUTPUT_MUST_BE_OUTSIDE_REPO"
        ),
    ):
        C.produce_candidate(
            repo,
            "inside output",
            [
                (
                    "scripts/obsidia_build.py",
                    source,
                )
            ],
            repo
            / "artifacts",
        )


def test_self_check_non_sovereign():

    truth = C.self_check()

    assert (
        truth["route"]
        == "TOOLING_ENGINEERING_V1"
    )

    assert (
        truth[
            "producer_authority"
        ]
        == "NONE"
    )

    assert (
        truth[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        truth["modification_only"]
        is True
    )

    for key in (
        "auto_apply",
        "auto_commit",
        "auto_push",
        "auto_merge",
        "world_action",
    ):
        assert truth[key] is False
