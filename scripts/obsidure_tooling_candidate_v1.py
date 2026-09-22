"""
OBSIDURE TOOLING ENGINEERING CANDIDATE V1
=========================================

R8-C2.

Dedicated non-sovereign producer surface:

    external bounded engineering sandbox outputs
        ->
    exact existing tooling targets
        ->
    REAL_UNIFIED_DIFF_V1 candidate.patch
        ->
    Obsidia Build Phase 1

This DOES NOT broaden historical AgentObsidure PYTHON_PATCH_PROPOSAL.
That route remains periphery/* only.

TOOLING_ENGINEERING_V1:
- modification-only;
- explicit scope;
- at least one scripts/* engineering target;
- optional existing tests/*.py co-targets;
- artifacts outside repository;
- clean HEAD worktree required;
- candidate bytes hash-bound;
- KX108_ONLY downstream authority.

No apply.
No commit.
No push.
No merge.
No WorldAction.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(
    __file__
).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SCRIPT_DIR),
    )


from obsidia_candidate_patch_v1 import (
    CANDIDATE_PATCH_MODE,
    bind_candidate_to_objective,
    check_candidate_patch,
    load_candidate_patch_file,
)

import obsidia_build as BUILD


VERSION = "1.0.0"

ROUTE = "TOOLING_ENGINEERING_V1"

PRODUCER = (
    "OBSIDURE_TOOLING_ENGINEERING_CANDIDATE_V1"
)

PRODUCER_AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

AUTO_APPLY = False
AUTO_COMMIT = False
AUTO_PUSH = False
AUTO_MERGE = False
WORLD_ACTION = False

MAX_FILES = 12


class ToolingCandidateError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True
)
class Replacement:
    target: str
    source: Path


@dataclass(
    frozen=True
)
class ToolingCandidate:
    objective: str
    base_sha: str
    patch_path: Path
    manifest_path: Path
    patch_sha256: str
    files: tuple[str, ...]
    source_hashes: dict[str, str]


_ALLOWED_TOP_LEVEL = re.compile(
    r"^scripts/(?:obsidia_|obsidure_)"
    r"[A-Za-z0-9_.-]+"
    r"\.(?:py|json|ya?ml|toml|md|ps1)$"
)

_ALLOWED_PROVIDER = re.compile(
    r"^scripts/providers/"
    r"[A-Za-z0-9_./-]+"
    r"\.(?:py|json|ya?ml)$"
)

_ALLOWED_RUNTIME_WIRING = re.compile(
    r"^scripts/runtime_wiring/"
    r"[A-Za-z0-9_./-]+"
    r"\.(?:py|json|ya?ml)$"
)

_ALLOWED_TEST = re.compile(
    r"^tests/"
    r"[A-Za-z0-9_./-]+\.py$"
)


_DENIED_PREFIXES = (
    "scripts/gates/",
)

_DENIED_INFIXES = (
    "server.kernel.sealed.cjs",
    "proofs/V18_",
    "proofs/lean/57_preuves",
    "merkle_seal.json",
    "rfc3161",
)


def _sha256(
    raw: bytes,
) -> str:

    return hashlib.sha256(
        raw
    ).hexdigest()


def _head(
    repo_root: Path,
) -> str:

    return subprocess.check_output(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd=repo_root,
        text=True,
    ).strip()


def _canonical_rel(
    raw: str,
) -> str:

    value = str(
        raw or ""
    ).strip().replace(
        "\\",
        "/",
    )

    if not value:
        raise ToolingCandidateError(
            "TARGET_EMPTY"
        )

    if (
        value.startswith("/")
        or re.match(
            r"^[A-Za-z]:",
            value,
        )
    ):
        raise ToolingCandidateError(
            "TARGET_ABSOLUTE"
        )

    parts = value.split("/")

    if any(
        part in (
            "",
            ".",
            "..",
        )
        for part in parts
    ):
        raise ToolingCandidateError(
            "TARGET_TRAVERSAL"
        )

    value = "/".join(
        parts
    )

    lowered = value.lower()

    if any(
        lowered.startswith(
            prefix.lower()
        )
        for prefix
        in _DENIED_PREFIXES
    ):
        raise ToolingCandidateError(
            "TOOLING_TARGET_DENIED:"
            + value
        )

    if any(
        token.lower()
        in lowered
        for token
        in _DENIED_INFIXES
    ):
        raise ToolingCandidateError(
            "PROTECTED_TARGET_DENIED:"
            + value
        )

    if (
        _ALLOWED_TOP_LEVEL.fullmatch(
            value
        )
        or _ALLOWED_PROVIDER.fullmatch(
            value
        )
        or _ALLOWED_RUNTIME_WIRING.fullmatch(
            value
        )
        or _ALLOWED_TEST.fullmatch(
            value
        )
    ):
        return value

    raise ToolingCandidateError(
        "TARGET_OUTSIDE_TOOLING_ENGINEERING:"
        + value
    )


def _assert_external(
    repo_root: Path,
    path: Path,
    error: str,
) -> Path:

    root = repo_root.resolve()
    resolved = path.resolve()

    try:
        resolved.relative_to(
            root
        )
    except ValueError:
        return resolved

    raise ToolingCandidateError(
        error
    )


def _read_source(
    repo_root: Path,
    path: Path,
) -> tuple[str, str]:

    source = _assert_external(
        repo_root,
        path,
        "SOURCE_MUST_BE_OUTSIDE_REPO",
    )

    if (
        not source.exists()
        or not source.is_file()
    ):
        raise ToolingCandidateError(
            "SOURCE_FILE_MISSING:"
            + str(source)
        )

    raw = source.read_bytes()

    try:
        text = raw.decode(
            "utf-8-sig"
        )
    except UnicodeDecodeError as exc:
        raise ToolingCandidateError(
            "SOURCE_NOT_UTF8:"
            + str(source)
        ) from exc

    text = (
        text
        .replace(
            "\r\n",
            "\n",
        )
        .replace(
            "\r",
            "\n",
        )
    )

    return (
        text,
        _sha256(raw),
    )


def _clean_target_text(
    repo_root: Path,
    rel: str,
) -> str:
    """
    Target must:
    - already exist in HEAD;
    - be clean staged;
    - be clean unstaged.

    Physical worktree bytes are then used so Windows CRLF is represented
    exactly as git apply will consume it.
    """

    exists = subprocess.run(
        [
            "git",
            "cat-file",
            "-e",
            f"HEAD:{rel}",
        ],
        cwd=repo_root,
        capture_output=True,
    )

    if exists.returncode != 0:
        raise ToolingCandidateError(
            "TOOLING_MODIFICATION_ONLY:"
            + rel
        )

    for label, argv in (
        (
            "UNSTAGED",
            [
                "git",
                "diff",
                "--quiet",
                "--",
                rel,
            ],
        ),
        (
            "STAGED",
            [
                "git",
                "diff",
                "--cached",
                "--quiet",
                "--",
                rel,
            ],
        ),
    ):

        proc = subprocess.run(
            argv,
            cwd=repo_root,
            capture_output=True,
        )

        if proc.returncode == 1:
            raise ToolingCandidateError(
                "TOOLING_BASE_DIRTY:"
                + label
                + ":"
                + rel
            )

        if proc.returncode != 0:
            raise ToolingCandidateError(
                "TOOLING_BASE_CHECK_FAILED:"
                + label
                + ":"
                + rel
            )

    target = (
        repo_root
        / rel
    ).resolve()

    try:
        target.relative_to(
            repo_root.resolve()
        )
    except ValueError as exc:
        raise ToolingCandidateError(
            "TARGET_ESCAPE:"
            + rel
        ) from exc

    if (
        not target.exists()
        or not target.is_file()
    ):
        raise ToolingCandidateError(
            "TARGET_WORKTREE_MISSING:"
            + rel
        )

    raw = target.read_bytes()

    try:
        return raw.decode(
            "utf-8"
        )
    except UnicodeDecodeError as exc:
        raise ToolingCandidateError(
            "TARGET_NOT_UTF8:"
            + rel
        ) from exc


def _physical_new_text(
    rel: str,
    old: str,
    normalized_new: str,
) -> str:

    crlf = old.count(
        "\r\n"
    )

    total_lf = old.count(
        "\n"
    )

    bare_lf = (
        total_lf
        - crlf
    )

    total_cr = old.count(
        "\r"
    )

    bare_cr = (
        total_cr
        - crlf
    )

    if (
        crlf
        and (
            bare_lf
            or bare_cr
        )
    ):
        raise ToolingCandidateError(
            "BASE_MIXED_LINE_ENDINGS:"
            + rel
        )

    if (
        bare_cr
        and not crlf
    ):
        raise ToolingCandidateError(
            "BASE_CR_ONLY_UNSUPPORTED:"
            + rel
        )

    normalized_new = (
        normalized_new
        .replace(
            "\r\n",
            "\n",
        )
        .replace(
            "\r",
            "\n",
        )
    )

    if crlf:
        return normalized_new.replace(
            "\n",
            "\r\n",
        )

    return normalized_new


def _diff(
    rel: str,
    old: str,
    new: str,
) -> str:

    physical_new = (
        _physical_new_text(
            rel,
            old,
            new,
        )
    )

    if old == physical_new:
        return ""

    body = "".join(
        difflib.unified_diff(
            old.splitlines(
                keepends=True
            ),
            physical_new.splitlines(
                keepends=True
            ),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            n=3,
            lineterm="\n",
        )
    )

    if not body:
        return ""

    return (
        f"diff --git "
        f"a/{rel} b/{rel}\n"
        + body
    )


def _default_output_root() -> Path:

    local = os.environ.get(
        "LOCALAPPDATA"
    )

    if local:
        return (
            Path(local)
            / "Obsidia"
            / "tooling_candidate_artifacts"
        )

    return (
        Path.home()
        / ".obsidia"
        / "tooling_candidate_artifacts"
    )


def parse_replacement(
    raw: str,
) -> tuple[str, Path]:

    if "=" not in raw:
        raise ToolingCandidateError(
            "REPLACE_FORMAT_TARGET_EQUALS_SOURCE"
        )

    target, source = raw.split(
        "=",
        1,
    )

    target = _canonical_rel(
        target
    )

    if not source.strip():
        raise ToolingCandidateError(
            "REPLACEMENT_SOURCE_EMPTY"
        )

    return (
        target,
        Path(
            source.strip()
        ),
    )


def produce_candidate(
    repo_root: Path,
    objective: str,
    replacements: list[
        tuple[str, Path]
    ],
    output_root: Path | None = None,
) -> ToolingCandidate:

    repo_root = (
        repo_root.resolve()
    )

    if not objective.strip():
        raise ToolingCandidateError(
            "OBJECTIVE_EMPTY"
        )

    if (
        not replacements
        or len(replacements) > MAX_FILES
    ):
        raise ToolingCandidateError(
            "REPLACEMENT_COUNT_INVALID"
        )

    normalized: dict[
        str,
        Path,
    ] = {}

    for target_raw, source in replacements:

        target = _canonical_rel(
            target_raw
        )

        if target in normalized:
            raise ToolingCandidateError(
                "DUPLICATE_TARGET:"
                + target
            )

        normalized[
            target
        ] = source

    if not any(
        target.startswith(
            "scripts/"
        )
        for target in normalized
    ):
        raise ToolingCandidateError(
            "TOOLING_ROUTE_REQUIRES_SCRIPT_TARGET"
        )

    base_sha = _head(
        repo_root
    )

    diffs: list[str] = []

    source_hashes: dict[
        str,
        str,
    ] = {}

    effective: list[str] = []

    for target in sorted(
        normalized
    ):

        old = _clean_target_text(
            repo_root,
            target,
        )

        new, source_sha = (
            _read_source(
                repo_root,
                normalized[target],
            )
        )

        source_hashes[
            target
        ] = source_sha

        patch = _diff(
            target,
            old,
            new,
        )

        if patch:

            diffs.append(
                patch
            )

            effective.append(
                target
            )

    if not diffs:
        raise ToolingCandidateError(
            "NO_EFFECTIVE_DIFF"
        )

    patch_raw = "".join(
        diffs
    ).encode(
        "utf-8"
    )

    patch_sha = _sha256(
        patch_raw
    )

    if output_root is None:
        output_root = (
            _default_output_root()
        )

    output_root = _assert_external(
        repo_root,
        output_root,
        "OUTPUT_MUST_BE_OUTSIDE_REPO",
    )

    artifact_dir = (
        output_root
        / base_sha[:12]
        / patch_sha[:16]
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    patch_path = (
        artifact_dir
        / "candidate.patch"
    )

    manifest_path = (
        artifact_dir
        / "candidate_manifest.json"
    )

    patch_path.write_bytes(
        patch_raw
    )

    spec = (
        load_candidate_patch_file(
            patch_path,
            repo_root,
        )
    )

    if tuple(
        effective
    ) != tuple(
        spec.files
    ):
        raise ToolingCandidateError(
            "CANDIDATE_SCOPE_MISMATCH"
        )

    ok, message = (
        check_candidate_patch(
            spec,
            repo_root,
        )
    )

    if not ok:
        raise ToolingCandidateError(
            "CANDIDATE_GIT_APPLY_CHECK_FAILED:"
            + message
        )

    manifest = {
        "version": VERSION,
        "route": ROUTE,
        "producer": PRODUCER,
        "producer_authority": (
            PRODUCER_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "objective_sha256": _sha256(
            objective.encode(
                "utf-8"
            )
        ),
        "base_sha": base_sha,
        "candidate_patch_mode": (
            CANDIDATE_PATCH_MODE
        ),
        "candidate_patch": str(
            patch_path
        ),
        "candidate_patch_sha256": (
            patch_sha
        ),
        "candidate_files": list(
            spec.files
        ),
        "source_sha256": (
            source_hashes
        ),
        "modification_only": True,
        "max_files": MAX_FILES,
        "auto_apply": AUTO_APPLY,
        "auto_commit": AUTO_COMMIT,
        "auto_push": AUTO_PUSH,
        "auto_merge": AUTO_MERGE,
        "world_action": WORLD_ACTION,
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return ToolingCandidate(
        objective=objective,
        base_sha=base_sha,
        patch_path=patch_path,
        manifest_path=manifest_path,
        patch_sha256=patch_sha,
        files=tuple(
            spec.files
        ),
        source_hashes=(
            source_hashes
        ),
    )


def build_phase1_plan(
    repo_root: Path,
    candidate: ToolingCandidate,
) -> dict:

    repo_root = (
        repo_root.resolve()
    )

    if _head(
        repo_root
    ) != candidate.base_sha:
        raise ToolingCandidateError(
            "BASE_SHA_CHANGED_AFTER_PRODUCTION"
        )

    spec = load_candidate_patch_file(
        candidate.patch_path,
        repo_root,
    )

    if (
        spec.sha256
        != candidate.patch_sha256
    ):
        raise ToolingCandidateError(
            "CANDIDATE_CHANGED_AFTER_PRODUCTION"
        )

    authority_objective = (
        bind_candidate_to_objective(
            candidate.objective,
            spec,
        )
    )

    plan = BUILD.compute_plan(
        authority_objective,
        candidate.base_sha,
        repo_root,
        explicit_scope=list(
            spec.files
        ),
    )

    plan[
        "candidate_patch_mode"
    ] = CANDIDATE_PATCH_MODE

    plan[
        "candidate_patch_hash"
    ] = spec.sha256

    plan[
        "candidate_patch_files"
    ] = list(
        spec.files
    )

    plan[
        "candidate_patch_source"
    ] = str(
        candidate.patch_path
    )

    plan[
        "display_objective"
    ] = candidate.objective

    plan[
        "candidate_producer"
    ] = PRODUCER

    plan[
        "candidate_producer_authority"
    ] = PRODUCER_AUTHORITY

    return plan


def self_check() -> dict:

    return {
        "version": VERSION,
        "route": ROUTE,
        "producer": PRODUCER,
        "producer_authority": (
            PRODUCER_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "candidate_patch_mode": (
            CANDIDATE_PATCH_MODE
        ),
        "allowed_primary": [
            "scripts/obsidia_*",
            "scripts/obsidure_*",
            "scripts/providers/*",
            "scripts/runtime_wiring/*",
        ],
        "allowed_cotarget": (
            "existing tests/*.py"
        ),
        "denied": [
            "scripts/gates/*",
            "periphery/*",
            "server.kernel.*",
            "proofs/*",
        ],
        "modification_only": True,
        "max_files": MAX_FILES,
        "artifact_location": (
            "OUTSIDE_REPO"
        ),
        "auto_apply": AUTO_APPLY,
        "auto_commit": AUTO_COMMIT,
        "auto_push": AUTO_PUSH,
        "auto_merge": AUTO_MERGE,
        "world_action": (
            WORLD_ACTION
        ),
        "r8c_status": (
            "C2_TOOLING_PRODUCER_CONTRACT"
        ),
    }


def _read_objective_file(
    path: Path,
) -> str:

    raw = path.read_bytes()

    try:
        return raw.decode(
            "utf-8-sig"
        )
    except UnicodeDecodeError as exc:
        raise ToolingCandidateError(
            "OBJECTIVE_NOT_UTF8"
        ) from exc


def main(
    argv: list[str] | None = None,
) -> int:

    parser = argparse.ArgumentParser(
        prog=(
            "obsidure-tooling-candidate"
        )
    )

    parser.add_argument(
        "--repo-root",
        default=str(
            Path(__file__)
            .resolve()
            .parent
            .parent
        ),
    )

    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        metavar="TARGET=SOURCE",
    )

    parser.add_argument(
        "--objective",
    )

    parser.add_argument(
        "--objective-file",
    )

    parser.add_argument(
        "--output-root",
    )

    parser.add_argument(
        "--phase1",
        action="store_true",
    )

    parser.add_argument(
        "--self-check",
        action="store_true",
    )

    args = parser.parse_args(
        argv
    )

    if args.self_check:

        print(
            json.dumps(
                self_check(),
                indent=2,
                sort_keys=True,
            )
        )

        return 0

    if bool(
        args.objective
    ) == bool(
        args.objective_file
    ):
        parser.error(
            "exactly one of --objective "
            "or --objective-file required"
        )

    repo_root = Path(
        args.repo_root
    ).resolve()

    objective = (
        args.objective
        if args.objective
        else _read_objective_file(
            Path(
                args.objective_file
            )
        )
    )

    replacements = [
        parse_replacement(
            raw
        )
        for raw in args.replace
    ]

    output_root = (
        Path(
            args.output_root
        )
        if args.output_root
        else None
    )

    candidate = produce_candidate(
        repo_root,
        objective,
        replacements,
        output_root,
    )

    print(
        "TOOLING_CANDIDATE_PRODUCED"
    )

    print(
        f"route = {ROUTE}"
    )

    print(
        f"base_sha = "
        f"{candidate.base_sha}"
    )

    print(
        f"candidate_patch = "
        f"{candidate.patch_path}"
    )

    print(
        f"candidate_patch_sha256 = "
        f"{candidate.patch_sha256}"
    )

    print(
        "candidate_files = "
        + ", ".join(
            candidate.files
        )
    )

    print(
        f"manifest = "
        f"{candidate.manifest_path}"
    )

    print(
        "producer_authority = NONE"
    )

    print(
        "decision_authority = KX108_ONLY"
    )

    print(
        "AUTO_APPLY = false"
    )

    print(
        "AUTO_COMMIT = false"
    )

    print(
        "AUTO_PUSH = false"
    )

    print(
        "AUTO_MERGE = false"
    )

    print(
        "WORLD_ACTION = false"
    )

    if args.phase1:

        plan = build_phase1_plan(
            repo_root,
            candidate,
        )

        print()

        print(
            BUILD.format_plan_proposed(
                plan
            )
        )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
