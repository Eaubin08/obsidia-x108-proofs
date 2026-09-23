from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(_SCRIPTS),
    )


import obsidia_jarvis_candidate_materializer_v0 as M


def _git(
    root: Path,
    *args: str,
) -> str:
    r = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )

    return r.stdout.strip()


def _repo(
    tmp_path: Path,
):
    root = tmp_path / "repo"
    root.mkdir()

    _git(
        root,
        "init",
        "-q",
    )

    _git(
        root,
        "config",
        "user.name",
        "J9 Test",
    )

    _git(
        root,
        "config",
        "user.email",
        "j9@test.invalid",
    )

    target = (
        root
        / "periphery"
        / "j9b4_target.txt"
    )

    target.parent.mkdir(
        parents=True
    )

    before = (
        b"J9_B4\nstate: BEFORE\n"
    )

    after = (
        b"J9_B4\nstate: AFTER\n"
    )

    target.write_bytes(
        before
    )

    _git(
        root,
        "add",
        ".",
    )

    _git(
        root,
        "commit",
        "-q",
        "-m",
        "base",
    )

    base = _git(
        root,
        "rev-parse",
        "HEAD",
    )

    target.write_bytes(
        after
    )

    patch = (
        tmp_path
        / "candidate.patch"
    )

    patch.write_text(
        _git(
            root,
            "diff",
            "--",
            "periphery/j9b4_target.txt",
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    _git(
        root,
        "checkout",
        "--",
        "periphery/j9b4_target.txt",
    )

    assert target.read_bytes() == before
    assert _git(root, "status", "--porcelain") == ""

    return {
        "root": root,
        "target": target,
        "target_rel":
            "periphery/j9b4_target.txt",
        "before": before,
        "after": after,
        "patch": patch,
        "base": base,
    }


def test_materializes_exact_candidate_without_user_git_state_mutation(
    tmp_path,
):
    w = _repo(tmp_path)

    head_before = _git(
        w["root"],
        "rev-parse",
        "HEAD",
    )

    branch_before = _git(
        w["root"],
        "rev-parse",
        "--abbrev-ref",
        "HEAD",
    )

    refs_before = _git(
        w["root"],
        "for-each-ref",
        "--format=%(refname)%00%(objectname)",
    )

    result = (
        M.materialize_candidate_patch(
            repo_root=w["root"],
            candidate_patch_path=w["patch"],
            base_sha=w["base"],
        )
    )

    assert (
        result.source_historical_path
        == w["target_rel"]
    )

    assert (
        result.target_path
        == w["target_rel"]
    )

    assert (
        result.base_sha
        == w["base"]
    )

    assert len(
        result.source_git_commit
    ) in (40, 64)

    assert (
        result.source_content_sha256
        == hashlib.sha256(
            w["after"]
        ).hexdigest()
    )

    assert (
        result.ref_created
        is False
    )

    # Immutable source contains exact candidate bytes.
    source_text = _git(
        w["root"],
        "show",
        (
            result.source_git_commit
            + ":"
            + w["target_rel"]
        ),
    )

    assert (
        source_text.encode()
        + b"\n"
        == w["after"]
    )

    # User repository view is untouched.
    assert (
        _git(
            w["root"],
            "rev-parse",
            "HEAD",
        )
        == head_before
    )

    assert (
        _git(
            w["root"],
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        )
        == branch_before
    )

    assert (
        _git(
            w["root"],
            "for-each-ref",
            "--format=%(refname)%00%(objectname)",
        )
        == refs_before
    )

    assert (
        _git(
            w["root"],
            "status",
            "--porcelain",
        )
        == ""
    )

    assert (
        w["target"].read_bytes()
        == w["before"]
    )


def test_materialization_is_deterministic(
    tmp_path,
):
    w = _repo(tmp_path)

    a = M.materialize_candidate_patch(
        repo_root=w["root"],
        candidate_patch_path=w["patch"],
        base_sha=w["base"],
    )

    b = M.materialize_candidate_patch(
        repo_root=w["root"],
        candidate_patch_path=w["patch"],
        base_sha=w["base"],
    )

    assert (
        a.source_git_commit
        == b.source_git_commit
    )

    assert (
        a.source_git_blob_sha
        == b.source_git_blob_sha
    )

    assert (
        a.source_content_sha256
        == b.source_content_sha256
    )


def test_stale_base_fails_closed(
    tmp_path,
):
    w = _repo(tmp_path)

    stale = (
        "0" * len(w["base"])
    )

    with pytest.raises(
        M.CandidateMaterializationError,
        match="CANDIDATE_BASE_HEAD_MISMATCH",
    ):
        M.materialize_candidate_patch(
            repo_root=w["root"],
            candidate_patch_path=w["patch"],
            base_sha=stale,
        )


def test_explicit_target_mismatch_fails_closed(
    tmp_path,
):
    w = _repo(tmp_path)

    with pytest.raises(
        M.CandidateMaterializationError,
        match="TARGET_PATH_CANDIDATE_MISMATCH",
    ):
        M.materialize_candidate_patch(
            repo_root=w["root"],
            candidate_patch_path=w["patch"],
            base_sha=w["base"],
            target_path="other.txt",
        )


def test_multi_target_candidate_is_rejected(
    tmp_path,
):
    w = _repo(tmp_path)

    second = (
        w["root"]
        / "periphery"
        / "second.txt"
    )

    second.write_bytes(
        b"SECOND BEFORE\n"
    )

    _git(
        w["root"],
        "add",
        ".",
    )

    _git(
        w["root"],
        "commit",
        "-q",
        "-m",
        "second base",
    )

    base = _git(
        w["root"],
        "rev-parse",
        "HEAD",
    )

    w["target"].write_bytes(
        w["after"]
    )

    second.write_bytes(
        b"SECOND AFTER\n"
    )

    patch = (
        tmp_path
        / "multi.patch"
    )

    patch.write_text(
        _git(
            w["root"],
            "diff",
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    _git(
        w["root"],
        "checkout",
        "--",
        ".",
    )

    with pytest.raises(
        M.CandidateMaterializationError,
        match="J9_B4_SINGLE_TARGET_REQUIRED",
    ):
        M.materialize_candidate_patch(
            repo_root=w["root"],
            candidate_patch_path=patch,
            base_sha=base,
        )


def test_materializer_has_no_ref_or_user_worktree_commands():
    src = Path(
        M.__file__
    ).read_text(
        encoding="utf-8-sig"
    )

    assert (
        '"commit-tree"'
        in src
    )

    for forbidden in (
        '"update-ref"',
        '"checkout"',
        '"reset"',
        '"merge"',
        '"rebase"',
        '"push"',
        '"commit",',
        "os.replace(",
        ".write_bytes(",
    ):
        assert forbidden not in src

    assert (
        "AUTO_REF_UPDATE = False"
        in src
    )

    assert (
        "WORKTREE_MUTATION = False"
        in src
    )

    assert (
        "INDEX_MUTATION = False"
        in src
    )
