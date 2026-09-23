"""
J9-B4 ? Jarvis immutable candidate materializer.

ROLE
----
Translate an already-produced, already-validated Obsidure candidate.patch
into the immutable Git source identity required by the canonical J5 rail:

    candidate.patch
        -> detached temporary index
        -> immutable Git tree
        -> deterministic unreferenced commit object
        -> (source_git_commit, source_historical_path)

NON-AUTHORITY
-------------
This module:
- does not decide;
- does not authorize;
- does not call KX108;
- does not call J5/J6/J7;
- does not mutate the user worktree;
- does not mutate HEAD;
- does not mutate branches or refs;
- does not mutate the user's Git index;
- does not commit through `git commit`;
- does not push/merge/rebase/reset/checkout.

`git commit-tree` is used only as Git object plumbing. No ref is created.
The object is deterministic and can be recreated from the exact candidate
patch + exact base SHA.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Mapping

try:
    from scripts.obsidia_candidate_patch_v1 import (
        check_candidate_patch,
        load_candidate_patch_file,
    )
except ImportError:
    from obsidia_candidate_patch_v1 import (
        check_candidate_patch,
        load_candidate_patch_file,
    )


SCHEMA_VERSION = (
    "OBSIDIA_JARVIS_CANDIDATE_MATERIALIZER_V0"
)

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

AUTO_APPLY = False
AUTO_COMMIT = False
AUTO_PUSH = False
AUTO_MERGE = False
AUTO_REF_UPDATE = False
WORKTREE_MUTATION = False
INDEX_MUTATION = False

_MATERIALIZER_NAME = (
    "Obsidia Candidate Materializer"
)

_MATERIALIZER_EMAIL = (
    "candidate-materializer@obsidia.invalid"
)

_DETERMINISTIC_GIT_DATE = (
    "2000-01-01T00:00:00+00:00"
)


class CandidateMaterializationError(
    RuntimeError
):
    pass


@dataclass(frozen=True)
class MaterializedCandidateSource:
    schema_version: str
    base_sha: str
    source_git_commit: str
    source_historical_path: str
    target_path: str
    source_git_blob_sha: str
    source_content_sha256: str
    candidate_patch_sha256: str
    candidate_patch_path: str
    authority: str = AUTHORITY
    decision_authority: str = DECISION_AUTHORITY
    ref_created: bool = False
    head_mutated: bool = False
    branch_mutated: bool = False
    user_index_mutated: bool = False
    worktree_mutated: bool = False


def _sha256(
    raw: bytes,
) -> str:
    return hashlib.sha256(
        raw
    ).hexdigest()


def _run_git(
    repo_root: Path,
    args: list[str],
    *,
    env: Mapping[str, str] | None = None,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    merged_env = os.environ.copy()

    if env:
        merged_env.update(
            {
                str(k): str(v)
                for k, v in env.items()
            }
        )

    result = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=str(repo_root),
        env=merged_env,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if check and result.returncode != 0:
        stderr = result.stderr.decode(
            "utf-8",
            errors="replace",
        ).strip()

        raise CandidateMaterializationError(
            "GIT_COMMAND_FAILED:"
            + ":".join(args[:2])
            + ":"
            + stderr
        )

    return result


def _git_text(
    repo_root: Path,
    args: list[str],
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    return _run_git(
        repo_root,
        args,
        env=env,
    ).stdout.decode(
        "utf-8",
        errors="strict",
    ).strip()


def _head(
    repo_root: Path,
) -> str:
    return _git_text(
        repo_root,
        [
            "rev-parse",
            "HEAD",
        ],
    )


def _branch(
    repo_root: Path,
) -> str:
    return _git_text(
        repo_root,
        [
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
    )


def _refs_snapshot(
    repo_root: Path,
) -> bytes:
    return _run_git(
        repo_root,
        [
            "for-each-ref",
            "--format=%(refname)%00%(objectname)",
        ],
    ).stdout


def _status_snapshot(
    repo_root: Path,
) -> bytes:
    return _run_git(
        repo_root,
        [
            "status",
            "--porcelain=v1",
            "-z",
        ],
    ).stdout


def _cached_diff_snapshot(
    repo_root: Path,
) -> bytes:
    return _run_git(
        repo_root,
        [
            "diff",
            "--cached",
            "--binary",
        ],
    ).stdout


def _normalize_target(
    value: str,
) -> str:
    target = str(
        value or ""
    ).replace(
        "\\",
        "/",
    ).strip()

    if (
        not target
        or target.startswith("/")
        or target.startswith("../")
        or "/../" in target
        or target == ".."
    ):
        raise CandidateMaterializationError(
            "TARGET_PATH_INVALID"
        )

    return target


def _verify_existing_file_at_commit(
    repo_root: Path,
    commitish: str,
    path: str,
) -> None:
    result = _run_git(
        repo_root,
        [
            "cat-file",
            "-e",
            f"{commitish}:{path}",
        ],
        check=False,
    )

    if result.returncode != 0:
        raise CandidateMaterializationError(
            "MODIFICATION_ONLY_TARGET_REQUIRED:"
            + path
        )


def materialize_candidate_patch(
    *,
    repo_root: str | Path,
    candidate_patch_path: str | Path,
    base_sha: str,
    target_path: str | None = None,
) -> MaterializedCandidateSource:
    """
    Materialize one modification-only Obsidure candidate as an immutable,
    deterministic, unreferenced Git commit object.

    The user's HEAD, branch, refs, index and worktree must be byte/state
    identical before and after this function.
    """
    repo = Path(
        repo_root
    ).resolve()

    patch_path = Path(
        candidate_patch_path
    ).resolve()

    if not repo.is_dir():
        raise CandidateMaterializationError(
            "REPO_ROOT_NOT_FOUND"
        )

    if not patch_path.is_file():
        raise CandidateMaterializationError(
            "CANDIDATE_PATCH_NOT_FOUND"
        )

    base = str(
        base_sha or ""
    ).strip()

    current_head = _head(
        repo
    )

    if base != current_head:
        raise CandidateMaterializationError(
            "CANDIDATE_BASE_HEAD_MISMATCH"
        )

    spec = load_candidate_patch_file(
        patch_path,
        repo,
    )

    ok, reason = check_candidate_patch(
        spec,
        repo,
    )

    if not ok:
        raise CandidateMaterializationError(
            "CANDIDATE_PATCH_REJECTED:"
            + str(reason)
        )

    files = tuple(
        _normalize_target(x)
        for x in spec.files
    )

    if len(files) != 1:
        raise CandidateMaterializationError(
            "J9_B4_SINGLE_TARGET_REQUIRED"
        )

    exact_target = files[0]

    if target_path is not None:
        requested_target = (
            _normalize_target(
                target_path
            )
        )

        if requested_target != exact_target:
            raise CandidateMaterializationError(
                "TARGET_PATH_CANDIDATE_MISMATCH"
            )

    # J5 V0 is UPDATE_TARGET_FROM_SOURCE, not ADD/DELETE.
    _verify_existing_file_at_commit(
        repo,
        base,
        exact_target,
    )

    before_head = _head(repo)
    before_branch = _branch(repo)
    before_refs = _refs_snapshot(repo)
    before_status = _status_snapshot(repo)
    before_cached = _cached_diff_snapshot(
        repo
    )

    patch_sha = _sha256(
        patch_path.read_bytes()
    )

    if (
        getattr(
            spec,
            "sha256",
            patch_sha,
        )
        != patch_sha
    ):
        raise CandidateMaterializationError(
            "CANDIDATE_PATCH_SHA256_MISMATCH"
        )

    with tempfile.TemporaryDirectory(
        prefix="obsidia-j9b4-"
    ) as td:
        temp_root = Path(td)
        temp_index = (
            temp_root
            / "candidate.index"
        )

        isolated_env = {
            "GIT_INDEX_FILE":
                str(temp_index),
        }

        # Build an isolated index from the exact immutable base.
        _run_git(
            repo,
            [
                "read-tree",
                base,
            ],
            env=isolated_env,
        )

        # Apply candidate ONLY to isolated index.
        _run_git(
            repo,
            [
                "apply",
                "--cached",
                "--whitespace=nowarn",
                str(patch_path),
            ],
            env=isolated_env,
        )

        tree_sha = _git_text(
            repo,
            [
                "write-tree",
            ],
            env=isolated_env,
        )

        # Modification-only: target must still exist after patch.
        _verify_existing_file_at_commit(
            repo,
            tree_sha,
            exact_target,
        )

        commit_env = {
            "GIT_AUTHOR_NAME":
                _MATERIALIZER_NAME,
            "GIT_AUTHOR_EMAIL":
                _MATERIALIZER_EMAIL,
            "GIT_AUTHOR_DATE":
                _DETERMINISTIC_GIT_DATE,
            "GIT_COMMITTER_NAME":
                _MATERIALIZER_NAME,
            "GIT_COMMITTER_EMAIL":
                _MATERIALIZER_EMAIL,
            "GIT_COMMITTER_DATE":
                _DETERMINISTIC_GIT_DATE,
        }

        message = (
            "OBSIDIA_IMMUTABLE_CANDIDATE_V0\n"
            f"base={base}\n"
            f"target={exact_target}\n"
            f"candidate_patch_sha256={patch_sha}\n"
        ).encode(
            "utf-8"
        )

        source_commit = _run_git(
            repo,
            [
                "commit-tree",
                tree_sha,
                "-p",
                base,
            ],
            env=commit_env,
            input_bytes=message,
        ).stdout.decode(
            "ascii"
        ).strip()

    # Resolve exact immutable source identity.
    blob_sha = _git_text(
        repo,
        [
            "rev-parse",
            f"{source_commit}:{exact_target}",
        ],
    )

    source_bytes = _run_git(
        repo,
        [
            "show",
            f"{source_commit}:{exact_target}",
        ],
    ).stdout

    # Strong post-condition: no user-visible Git state changed.
    if _head(repo) != before_head:
        raise CandidateMaterializationError(
            "HEAD_MUTATED_BY_MATERIALIZER"
        )

    if _branch(repo) != before_branch:
        raise CandidateMaterializationError(
            "BRANCH_MUTATED_BY_MATERIALIZER"
        )

    if _refs_snapshot(repo) != before_refs:
        raise CandidateMaterializationError(
            "REFS_MUTATED_BY_MATERIALIZER"
        )

    if _status_snapshot(repo) != before_status:
        raise CandidateMaterializationError(
            "WORKTREE_MUTATED_BY_MATERIALIZER"
        )

    if (
        _cached_diff_snapshot(repo)
        != before_cached
    ):
        raise CandidateMaterializationError(
            "USER_INDEX_MUTATED_BY_MATERIALIZER"
        )

    return MaterializedCandidateSource(
        schema_version=SCHEMA_VERSION,
        base_sha=base,
        source_git_commit=source_commit,
        source_historical_path=exact_target,
        target_path=exact_target,
        source_git_blob_sha=blob_sha,
        source_content_sha256=_sha256(
            source_bytes
        ),
        candidate_patch_sha256=patch_sha,
        candidate_patch_path=str(
            patch_path
        ),
    )
