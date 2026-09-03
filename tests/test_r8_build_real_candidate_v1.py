"""
R8-B1 — real candidate.patch transport and bounded application.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_build as B

from obsidia_candidate_patch_v1 import (
    CANDIDATE_PATCH_MODE,
    apply_candidate_patch,
    bind_candidate_to_objective,
    load_candidate_patch_file,
    parse_candidate_patch_files,
)


PATCH_A = """diff --git a/periphery/demo.py b/periphery/demo.py
--- a/periphery/demo.py
+++ b/periphery/demo.py
@@ -1 +1 @@
-VALUE = "old"
+VALUE = "new"
"""


PATCH_B = """diff --git a/periphery/demo.py b/periphery/demo.py
--- a/periphery/demo.py
+++ b/periphery/demo.py
@@ -1 +1 @@
-VALUE = "old"
+VALUE = "different"
"""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    _git(repo, "init")

    (repo / "periphery").mkdir()
    (repo / "tests").mkdir()

    (repo / "periphery" / "demo.py").write_text(
        'VALUE = "old"\n',
        encoding="utf-8",
    )

    (repo / "tests" / "test_demo.py").write_text(
        "from pathlib import Path\n"
        "\n"
        "def test_demo():\n"
        "    text = Path('periphery/demo.py').read_text()\n"
        "    assert 'VALUE = \"new\"' in text\n",
        encoding="utf-8",
    )

    _git(repo, "add", ".")

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


def test_parse_candidate_files():
    assert parse_candidate_patch_files(PATCH_A) == (
        "periphery/demo.py",
    )


def test_candidate_hash_binds_exact_content(tmp_path):
    repo = _make_repo(tmp_path)

    a = tmp_path / "a.patch"
    b = tmp_path / "b.patch"

    a.write_text(PATCH_A, encoding="utf-8")
    b.write_text(PATCH_B, encoding="utf-8")

    spec_a = load_candidate_patch_file(a, repo)
    spec_b = load_candidate_patch_file(b, repo)

    assert spec_a.sha256 != spec_b.sha256
    assert spec_a.files == spec_b.files


def test_candidate_changes_approval_identity(tmp_path):
    repo = _make_repo(tmp_path)

    a = tmp_path / "a.patch"
    b = tmp_path / "b.patch"

    a.write_text(PATCH_A, encoding="utf-8")
    b.write_text(PATCH_B, encoding="utf-8")

    spec_a = load_candidate_patch_file(a, repo)
    spec_b = load_candidate_patch_file(b, repo)

    obj_a = bind_candidate_to_objective(
        "R8 candidate",
        spec_a,
    )

    obj_b = bind_candidate_to_objective(
        "R8 candidate",
        spec_b,
    )

    sha = B.get_base_sha(repo)

    plan_a = B.compute_plan(
        obj_a,
        sha,
        repo,
        explicit_scope=list(spec_a.files),
    )

    plan_b = B.compute_plan(
        obj_b,
        sha,
        repo,
        explicit_scope=list(spec_b.files),
    )

    assert plan_a["session_id"] != plan_b["session_id"]
    assert (
        plan_a["next_human_action"]
        != plan_b["next_human_action"]
    )


def test_git_apply_real_candidate_in_isolated_repo(tmp_path):
    repo = _make_repo(tmp_path)

    p = tmp_path / "candidate.patch"
    p.write_text(PATCH_A, encoding="utf-8")

    spec = load_candidate_patch_file(p, repo)

    result = apply_candidate_patch(
        spec,
        repo,
    )

    assert result["ok"] is True

    changed = (
        repo
        / "periphery"
        / "demo.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'VALUE = "new"' in changed


def test_builder_phase2_uses_real_candidate(tmp_path):
    repo = _make_repo(tmp_path)
    state = tmp_path / "state"

    patch_path = tmp_path / "candidate.patch"
    patch_path.write_text(
        PATCH_A,
        encoding="utf-8",
    )

    spec = load_candidate_patch_file(
        patch_path,
        repo,
    )

    authority_objective = bind_candidate_to_objective(
        "R8 real candidate E2E",
        spec,
    )

    sha = B.get_base_sha(repo)

    plan = B.compute_plan(
        authority_objective,
        sha,
        repo,
        explicit_scope=list(spec.files),
    )

    token = plan["next_human_action"]

    B.cmd_execute(
        authority_objective,
        token,
        repo_root=repo,
        state_dir=state,
        explicit_scope=list(spec.files),
        candidate_patch_spec=spec,
    )

    worktree = (
        repo.parent
        / plan["worktree_proposal"]
    )

    try:
        assert worktree.exists()

        content = (
            worktree
            / "periphery"
            / "demo.py"
        ).read_text(
            encoding="utf-8"
        )

        assert 'VALUE = "new"' in content

        receipt_path = (
            state
            / plan["session_id"]
            / "receipt.json"
        )

        assert receipt_path.exists()

        receipt = json.loads(
            receipt_path.read_text(
                encoding="utf-8"
            )
        )

        assert receipt["candidate_patch_mode"] == (
            CANDIDATE_PATCH_MODE
        )

        assert receipt["candidate_patch_hash"] == (
            spec.sha256
        )

        assert receipt["candidate_patch_files"] == [
            "periphery/demo.py"
        ]

        assert receipt["candidate_patch_apply"]["ok"] is True

        assert (
            "tests/fixtures/terminal_build_bounded/target.txt"
            not in receipt.get(
                "actual_touched_files",
                [],
            )
        )

    finally:
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
