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

# R8_CANDIDATE_PATCH_ADD_SUPPORT_V1

def _r8_add_support_module():
    import importlib.util
    import sys
    from pathlib import Path

    module_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "obsidia_candidate_patch_v1.py"
    )

    name = "obsidia_candidate_patch_v1_add_support_test"

    spec = importlib.util.spec_from_file_location(
        name,
        module_path,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[
        name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


def _r8_add_support_repo(tmp_path):
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        result = subprocess.run(
            [
                "git",
                *args,
            ],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        assert result.returncode == 0, (
            result.stdout
            + "\n"
            + result.stderr
        )

        return result

    git("init")
    git(
        "config",
        "user.email",
        "r8-add-test@example.invalid",
    )
    git(
        "config",
        "user.name",
        "R8 Add Test",
    )

    (repo / "baseline.txt").write_text(
        "BASELINE\n",
        encoding="utf-8",
    )

    git("add", ".")
    git(
        "commit",
        "-m",
        "baseline",
    )

    return repo


def _r8_write_patch(
    tmp_path,
    text,
    name="candidate.patch",
):
    path = tmp_path / name
    path.write_text(
        text,
        encoding="utf-8",
    )
    return path


def _r8_regular_add_patch():
    return (
        "diff --git a/new_file.py b/new_file.py\n"
        "new file mode 100644\n"
        "--- /dev/null\n"
        "+++ b/new_file.py\n"
        "@@ -0,0 +1 @@\n"
        '+VALUE = "NEW"\n'
    )


def test_r8_candidate_patch_strict_add_load_check_apply(
    tmp_path,
):
    import hashlib

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    patch = _r8_write_patch(
        tmp_path,
        _r8_regular_add_patch(),
    )

    spec = module.load_candidate_patch_file(
        patch,
        repo,
    )

    assert spec.files == (
        "new_file.py",
    )

    assert spec.sha256 == hashlib.sha256(
        patch.read_bytes()
    ).hexdigest()

    check_ok, check_msg = (
        module.check_candidate_patch(
            spec,
            repo,
        )
    )

    assert check_ok, check_msg

    result = module.apply_candidate_patch(
        spec,
        repo,
    )

    assert result["ok"] is True

    created = repo / "new_file.py"

    assert created.is_file()

    assert created.read_text(
        encoding="utf-8"
    ) == 'VALUE = "NEW"\n'


def test_r8_candidate_patch_add_requires_absent_target(
    tmp_path,
):
    import pytest

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    (repo / "new_file.py").write_text(
        "PREEXISTING\n",
        encoding="utf-8",
    )

    patch = _r8_write_patch(
        tmp_path,
        _r8_regular_add_patch(),
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE_ADD_TARGET_ALREADY_EXISTS:new_file.py",
    ):
        module.load_candidate_patch_file(
            patch,
            repo,
        )


def test_r8_candidate_patch_add_requires_new_file_mode(
    tmp_path,
):
    import pytest

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    malformed = (
        "diff --git a/new_file.py b/new_file.py\n"
        "--- /dev/null\n"
        "+++ b/new_file.py\n"
        "@@ -0,0 +1 @@\n"
        '+VALUE = "NEW"\n'
    )

    patch = _r8_write_patch(
        tmp_path,
        malformed,
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE_ADD_MODE_UNSUPPORTED:new_file.py",
    ):
        module.load_candidate_patch_file(
            patch,
            repo,
        )


def test_r8_candidate_patch_add_rejects_symlink_mode(
    tmp_path,
):
    import pytest

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    symlink_patch = (
        "diff --git a/new_link b/new_link\n"
        "new file mode 120000\n"
        "--- /dev/null\n"
        "+++ b/new_link\n"
        "@@ -0,0 +1 @@\n"
        "+target\n"
    )

    patch = _r8_write_patch(
        tmp_path,
        symlink_patch,
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE_ADD_MODE_UNSUPPORTED:new_link",
    ):
        module.load_candidate_patch_file(
            patch,
            repo,
        )


def test_r8_candidate_patch_add_rejects_executable_mode(
    tmp_path,
):
    import pytest

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    executable_patch = (
        "diff --git a/run.py b/run.py\n"
        "new file mode 100755\n"
        "--- /dev/null\n"
        "+++ b/run.py\n"
        "@@ -0,0 +1 @@\n"
        "+pass\n"
    )

    patch = _r8_write_patch(
        tmp_path,
        executable_patch,
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE_ADD_MODE_UNSUPPORTED:run.py",
    ):
        module.load_candidate_patch_file(
            patch,
            repo,
        )


def test_r8_candidate_patch_delete_behavior_preserved(
    tmp_path,
):
    import subprocess

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    doomed = repo / "delete_me.txt"

    doomed.write_text(
        "DELETE\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "git",
            "add",
            "delete_me.txt",
        ],
        cwd=str(repo),
        check=True,
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "add delete target",
        ],
        cwd=str(repo),
        check=True,
    )

    doomed.unlink()

    diff = subprocess.run(
        [
            "git",
            "diff",
            "--binary",
        ],
        cwd=str(repo),
        capture_output=True,
        check=True,
    ).stdout

    subprocess.run(
        [
            "git",
            "restore",
            "delete_me.txt",
        ],
        cwd=str(repo),
        check=True,
    )

    patch = tmp_path / "delete.patch"

    patch.write_bytes(
        diff
    )

    spec = module.load_candidate_patch_file(
        patch,
        repo,
    )

    check_ok, check_msg = (
        module.check_candidate_patch(
            spec,
            repo,
        )
    )

    assert check_ok, check_msg

    result = module.apply_candidate_patch(
        spec,
        repo,
    )

    assert result["ok"] is True

    assert not doomed.exists()


def test_r8_candidate_patch_modify_behavior_preserved(
    tmp_path,
):
    import subprocess

    module = _r8_add_support_module()

    repo = _r8_add_support_repo(
        tmp_path
    )

    baseline = repo / "baseline.txt"

    baseline.write_text(
        "BASELINE\nMODIFIED\n",
        encoding="utf-8",
    )

    diff = subprocess.run(
        [
            "git",
            "diff",
            "--binary",
        ],
        cwd=str(repo),
        capture_output=True,
        check=True,
    ).stdout

    subprocess.run(
        [
            "git",
            "restore",
            "baseline.txt",
        ],
        cwd=str(repo),
        check=True,
    )

    patch = tmp_path / "modify.patch"

    patch.write_bytes(
        diff
    )

    spec = module.load_candidate_patch_file(
        patch,
        repo,
    )

    check_ok, check_msg = (
        module.check_candidate_patch(
            spec,
            repo,
        )
    )

    assert check_ok, check_msg

    result = module.apply_candidate_patch(
        spec,
        repo,
    )

    assert result["ok"] is True

    assert baseline.read_text(
        encoding="utf-8"
    ) == "BASELINE\nMODIFIED\n"
