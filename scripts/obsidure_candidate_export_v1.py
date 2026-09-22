"""
OBSIDURE CANDIDATE EXPORT V1
============================

R8-C1.

Bridge non souverain:

    Obsidure PatchProposal
        ->
    exact sandbox outputs
        ->
    REAL_UNIFIED_DIFF_V1 candidate.patch
        ->
    Obsidia Build Phase 1

Ce module:
- ne décide rien;
- n'applique rien;
- ne crée aucun worktree;
- ne commit rien;
- ne push rien;
- ne merge rien;
- ne produit aucun WorldAction.

R8-C1 reste volontairement limité à periphery/*,
qui est la surface réelle de génération Python Obsidure existante.

Une future route distincte TOOLING_ENGINEERING devra traiter scripts/*
sans modifier cette frontière historique.

decision_authority = KX108_ONLY
producer_authority = NONE
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
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent

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

PRODUCER = (
    "OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1"
)

PRODUCER_AUTHORITY = "NONE"

DECISION_AUTHORITY = "KX108_ONLY"

AUTO_APPLY = False
AUTO_COMMIT = False
AUTO_PUSH = False
AUTO_MERGE = False
WORLD_ACTION = False

_SAFE_ID = re.compile(
    r"^[A-Za-z0-9_.-]{1,128}$"
)


class CandidateExportError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True
)
class ExportedCandidate:
    proposal_id: str
    proposal_json: Path
    proposal_sha256: str
    base_sha: str
    patch_path: Path
    manifest_path: Path
    patch_sha256: str
    files: tuple[str, ...]


def _sha256_bytes(
    raw: bytes,
) -> str:

    return hashlib.sha256(
        raw
    ).hexdigest()


def _read_json(
    path: Path,
) -> dict[str, Any]:

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CandidateExportError(
            "PROPOSAL_JSON_UNREADABLE"
        ) from exc

    try:
        data = json.loads(
            raw.decode(
                "utf-8-sig"
            )
        )
    except Exception as exc:
        raise CandidateExportError(
            "PROPOSAL_JSON_INVALID"
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise CandidateExportError(
            "PROPOSAL_JSON_NOT_OBJECT"
        )

    return data


def _git(
    repo_root: Path,
    args: list[str],
) -> str:

    proc = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=repo_root,
        capture_output=True,
    )

    if proc.returncode != 0:
        msg = (
            proc.stderr
            or proc.stdout
            or b""
        ).decode(
            "utf-8",
            errors="replace",
        )

        raise CandidateExportError(
            "GIT_READ_FAILED:"
            + msg[-300:]
        )

    return proc.stdout.decode(
        "utf-8",
        errors="strict",
    )


def _repo_head(
    repo_root: Path,
) -> str:

    return _git(
        repo_root,
        [
            "rev-parse",
            "HEAD",
        ],
    ).strip()


def _canonical_rel(
    raw: Any,
) -> str:

    value = str(
        raw or ""
    ).strip()

    value = value.replace(
        "\\",
        "/",
    )

    if not value:
        raise CandidateExportError(
            "EMPTY_PATCH_PATH"
        )

    if value.startswith(
        "/"
    ):
        raise CandidateExportError(
            "ABSOLUTE_PATCH_PATH"
        )

    if re.match(
        r"^[A-Za-z]:",
        value,
    ):
        raise CandidateExportError(
            "WINDOWS_ABSOLUTE_PATCH_PATH"
        )

    parts = value.split(
        "/"
    )

    if any(
        part in (
            "",
            ".",
            "..",
        )
        for part in parts
    ):
        raise CandidateExportError(
            "PATCH_PATH_TRAVERSAL"
        )

    canonical = "/".join(
        parts
    )

    # R8-C1 = truth of current Obsidure route.
    # NO hidden broadening toward scripts/.
    if not canonical.startswith(
        "periphery/"
    ):
        raise CandidateExportError(
            "R8C1_PERIPHERY_ONLY:"
            + canonical
        )

    return canonical


def _assert_external_output(
    repo_root: Path,
    output_dir: Path,
) -> None:

    root = repo_root.resolve()

    out = output_dir.resolve()

    try:
        out.relative_to(
            root
        )
    except ValueError:
        return

    raise CandidateExportError(
        "CANDIDATE_ARTIFACT_MUST_BE_OUTSIDE_REPO"
    )


def _default_artifact_root() -> Path:

    local = os.environ.get(
        "LOCALAPPDATA"
    )

    if local:
        return (
            Path(local)
            / "Obsidia"
            / "candidate_artifacts"
        )

    return (
        Path.home()
        / ".obsidia"
        / "candidate_artifacts"
    )


def _proposal_json_from_id(
    repo_root: Path,
    proposal_id: str,
) -> Path:

    if not _SAFE_ID.fullmatch(
        proposal_id or ""
    ):
        raise CandidateExportError(
            "INVALID_PROPOSAL_ID"
        )

    root = (
        repo_root
        / "_PATCH_PROPOSALS"
    ).resolve()

    path = (
        root
        / proposal_id
        / "proposal.json"
    ).resolve()

    try:
        path.relative_to(
            root
        )
    except ValueError as exc:
        raise CandidateExportError(
            "PROPOSAL_PATH_ESCAPE"
        ) from exc

    return path


def _sandbox_file(
    raw: Any,
    proposal_json: Path,
) -> Path:

    value = str(
        raw or ""
    ).strip()

    if not value:
        raise CandidateExportError(
            "SANDBOX_PATH_MISSING"
        )

    path = Path(
        value
    )

    if not path.is_absolute():
        path = (
            proposal_json.parent
            / path
        )

    path = path.resolve()

    if not path.exists():
        raise CandidateExportError(
            "SANDBOX_FILE_MISSING:"
            + str(path)
        )

    if not path.is_file():
        raise CandidateExportError(
            "SANDBOX_NOT_FILE:"
            + str(path)
        )

    return path


def _read_utf8_candidate_text(
    path: Path,
) -> str:

    raw = path.read_bytes()

    try:
        text = raw.decode(
            "utf-8-sig"
        )
    except UnicodeDecodeError as exc:
        raise CandidateExportError(
            "SANDBOX_NOT_UTF8:"
            + str(path)
        ) from exc

    # Artifact normalization happens BEFORE hashing.
    # candidate.patch itself is then exact-byte bound by B1.
    return (
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


def _head_file_text(
    repo_root: Path,
    rel: str,
) -> str:
    """
    Retourne le texte EXACT du worktree propre.

    L'autorité de base reste HEAD/base_sha:
    - le fichier doit exister dans HEAD;
    - staged diff = zéro;
    - unstaged diff = zéro.

    Le worktree est ensuite utilisé uniquement comme représentation
    physique de cette même base, notamment pour CRLF Windows.

    Aucun dirty worktree ne peut donc devenir une nouvelle base.
    """

    # ------------------------------------------------------------
    # Modification-only:
    # la cible doit exister dans HEAD.
    # ------------------------------------------------------------

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
        raise CandidateExportError(
            "R8C1_MODIFICATION_ONLY:"
            + rel
        )


    # ------------------------------------------------------------
    # Fail closed si la représentation du worktree ne correspond
    # plus logiquement à HEAD.
    #
    # git diff respecte les règles de conversion du repository,
    # donc un CRLF checkout propre avec core.autocrlf=true reste OK.
    # ------------------------------------------------------------

    checks = (
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
    )

    for label, argv in checks:

        proc = subprocess.run(
            argv,
            cwd=repo_root,
            capture_output=True,
        )

        if proc.returncode == 1:
            raise CandidateExportError(
                "CANDIDATE_BASE_WORKTREE_DIRTY:"
                + label
                + ":"
                + rel
            )

        if proc.returncode != 0:
            message = (
                proc.stderr
                or proc.stdout
                or b""
            ).decode(
                "utf-8",
                errors="replace",
            )

            raise CandidateExportError(
                "CANDIDATE_BASE_WORKTREE_CHECK_FAILED:"
                + label
                + ":"
                + message[-300:]
            )


    # ------------------------------------------------------------
    # Physical checkout representation.
    # ------------------------------------------------------------

    target = (
        repo_root
        / rel
    ).resolve()

    root = repo_root.resolve()

    try:
        target.relative_to(
            root
        )

    except ValueError as exc:
        raise CandidateExportError(
            "WORKTREE_TARGET_ESCAPE:"
            + rel
        ) from exc

    if (
        not target.exists()
        or not target.is_file()
    ):
        raise CandidateExportError(
            "WORKTREE_TARGET_MISSING:"
            + rel
        )

    raw = target.read_bytes()

    try:
        # utf-8, PAS utf-8-sig:
        # si un BOM existe dans le fichier cible il fait partie
        # du contenu physique à matcher.
        return raw.decode(
            "utf-8"
        )

    except UnicodeDecodeError as exc:
        raise CandidateExportError(
            "BASE_FILE_NOT_UTF8:"
            + rel
        ) from exc


def _one_file_diff(
    rel: str,
    old: str,
    new: str,
) -> str:
    """
    Produit un unified diff contre la représentation physique propre
    du worktree.

    Le contenu nouveau est adapté au style EOL de la base afin de ne
    jamais transformer artificiellement tout un fichier uniquement
    à cause de LF/CRLF.
    """

    crlf_count = old.count(
        "\r\n"
    )

    lf_count = old.count(
        "\n"
    )

    bare_lf_count = (
        lf_count
        - crlf_count
    )

    total_cr_count = old.count(
        "\r"
    )

    bare_cr_count = (
        total_cr_count
        - crlf_count
    )


    # ------------------------------------------------------------
    # Base mixte = ambiguïté physique => fail closed.
    # ------------------------------------------------------------

    if (
        crlf_count
        and (
            bare_lf_count
            or bare_cr_count
        )
    ):
        raise CandidateExportError(
            "BASE_MIXED_LINE_ENDINGS:"
            + rel
        )

    if (
        bare_cr_count
        and not crlf_count
    ):
        raise CandidateExportError(
            "BASE_CR_ONLY_LINE_ENDINGS_UNSUPPORTED:"
            + rel
        )


    # ------------------------------------------------------------
    # Normaliser d'abord la sortie sandbox.
    # ------------------------------------------------------------

    normalized_new = (
        new
        .replace(
            "\r\n",
            "\n",
        )
        .replace(
            "\r",
            "\n",
        )
    )


    # ------------------------------------------------------------
    # Puis reproduire l'EOL physique de la base.
    # ------------------------------------------------------------

    if crlf_count:

        physical_new = (
            normalized_new
            .replace(
                "\n",
                "\r\n",
            )
        )

    else:

        physical_new = (
            normalized_new
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
            fromfile=(
                f"a/{rel}"
            ),
            tofile=(
                f"b/{rel}"
            ),
            n=3,
            lineterm="\n",
        )
    )


    if not body:
        return ""


    return (
        f"diff --git "
        f"a/{rel} "
        f"b/{rel}\n"
        + body
    )


def export_proposal_candidate(
    repo_root: Path,
    proposal_json: Path,
    output_root: Path | None = None,
) -> ExportedCandidate:

    repo_root = (
        repo_root.resolve()
    )

    proposal_json = (
        proposal_json.resolve()
    )

    data = _read_json(
        proposal_json
    )

    proposal_id = str(
        data.get(
            "proposal_id"
        )
        or proposal_json.parent.name
    ).strip()

    if not _SAFE_ID.fullmatch(
        proposal_id
    ):
        raise CandidateExportError(
            "INVALID_PROPOSAL_ID"
        )

    if bool(
        data.get(
            "human_approved"
        )
    ):
        raise CandidateExportError(
            "ALREADY_HUMAN_APPROVED_PROPOSAL_REJECTED"
        )

    status = str(
        data.get(
            "status"
        )
        or ""
    ).upper()

    if status.startswith(
        "APPLIED"
    ):
        raise CandidateExportError(
            "ALREADY_APPLIED_PROPOSAL_REJECTED"
        )

    patches = data.get(
        "patches"
    )

    if (
        not isinstance(
            patches,
            list,
        )
        or not patches
    ):
        raise CandidateExportError(
            "PROPOSAL_PATCHES_EMPTY"
        )

    proposal_raw = (
        proposal_json.read_bytes()
    )

    proposal_sha = (
        _sha256_bytes(
            proposal_raw
        )
    )

    base_sha = _repo_head(
        repo_root
    )

    by_path: dict[
        str,
        Path,
    ] = {}

    for patch in patches:

        if not isinstance(
            patch,
            dict,
        ):
            raise CandidateExportError(
                "PATCH_ENTRY_NOT_OBJECT"
            )

        rel = _canonical_rel(
            patch.get(
                "path"
            )
        )

        if rel in by_path:
            raise CandidateExportError(
                "DUPLICATE_PATCH_PATH:"
                + rel
            )

        sandbox = _sandbox_file(
            patch.get(
                "sandbox_path"
            ),
            proposal_json,
        )

        by_path[
            rel
        ] = sandbox

    diffs: list[str] = []

    source_hashes: dict[
        str,
        str,
    ] = {}

    effective_files: list[
        str
    ] = []

    for rel in sorted(
        by_path
    ):

        sandbox = by_path[
            rel
        ]

        old = _head_file_text(
            repo_root,
            rel,
        )

        new = _read_utf8_candidate_text(
            sandbox
        )

        source_hashes[
            rel
        ] = _sha256_bytes(
            sandbox.read_bytes()
        )

        diff = _one_file_diff(
            rel,
            old,
            new,
        )

        if diff:
            diffs.append(
                diff
            )

            effective_files.append(
                rel
            )

    if not diffs:
        raise CandidateExportError(
            "NO_EFFECTIVE_DIFF"
        )

    patch_text = "".join(
        diffs
    )

    patch_raw = (
        patch_text.encode(
            "utf-8"
        )
    )

    patch_sha = (
        _sha256_bytes(
            patch_raw
        )
    )

    if output_root is None:
        output_root = (
            _default_artifact_root()
        )

    output_root = (
        output_root.resolve()
    )

    _assert_external_output(
        repo_root,
        output_root,
    )

    artifact_dir = (
        output_root
        / proposal_id
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

    # Reuse R8-B1 validator.
    spec = (
        load_candidate_patch_file(
            patch_path,
            repo_root,
        )
    )

    if tuple(
        effective_files
    ) != tuple(
        spec.files
    ):
        raise CandidateExportError(
            "CANDIDATE_SCOPE_VALIDATION_MISMATCH"
        )

    ok, message = (
        check_candidate_patch(
            spec,
            repo_root,
        )
    )

    if not ok:
        raise CandidateExportError(
            "CANDIDATE_GIT_APPLY_CHECK_FAILED:"
            + message
        )

    manifest = {
        "version": VERSION,
        "producer": PRODUCER,
        "producer_authority": (
            PRODUCER_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "proposal_id": (
            proposal_id
        ),
        "proposal_json": (
            str(
                proposal_json
            )
        ),
        "proposal_sha256": (
            proposal_sha
        ),
        "base_sha": (
            base_sha
        ),
        "candidate_patch_mode": (
            CANDIDATE_PATCH_MODE
        ),
        "candidate_patch": (
            str(
                patch_path
            )
        ),
        "candidate_patch_sha256": (
            patch_sha
        ),
        "candidate_files": list(
            spec.files
        ),
        "sandbox_source_sha256": (
            source_hashes
        ),
        "surface": (
            "PERIPHERY_ONLY_R8C1"
        ),
        "auto_apply": (
            AUTO_APPLY
        ),
        "auto_commit": (
            AUTO_COMMIT
        ),
        "auto_push": (
            AUTO_PUSH
        ),
        "auto_merge": (
            AUTO_MERGE
        ),
        "world_action": (
            WORLD_ACTION
        ),
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
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return ExportedCandidate(
        proposal_id=proposal_id,
        proposal_json=proposal_json,
        proposal_sha256=proposal_sha,
        base_sha=base_sha,
        patch_path=patch_path,
        manifest_path=manifest_path,
        patch_sha256=patch_sha,
        files=tuple(
            spec.files
        ),
    )


def build_phase1_plan(
    repo_root: Path,
    objective: str,
    candidate: ExportedCandidate,
) -> dict:

    repo_root = (
        repo_root.resolve()
    )

    if not objective.strip():
        raise CandidateExportError(
            "OBJECTIVE_EMPTY"
        )

    if _repo_head(
        repo_root
    ) != candidate.base_sha:
        raise CandidateExportError(
            "BASE_SHA_CHANGED_AFTER_EXPORT"
        )

    spec = load_candidate_patch_file(
        candidate.patch_path,
        repo_root,
    )

    if spec.sha256 != (
        candidate.patch_sha256
    ):
        raise CandidateExportError(
            "CANDIDATE_HASH_CHANGED_AFTER_EXPORT"
        )

    authority_objective = (
        bind_candidate_to_objective(
            objective,
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

    # Display-only metadata used by R8-B1 formatter.
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
    ] = objective

    return plan


def self_check() -> dict:

    return {
        "version": VERSION,
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
        "allowed_surface": (
            "periphery/*"
        ),
        "modification_only": True,
        "artifact_location": (
            "OUTSIDE_REPO"
        ),
        "auto_apply": (
            AUTO_APPLY
        ),
        "auto_commit": (
            AUTO_COMMIT
        ),
        "auto_push": (
            AUTO_PUSH
        ),
        "auto_merge": (
            AUTO_MERGE
        ),
        "world_action": (
            WORLD_ACTION
        ),
        "phase1_creates_worktree": False,
        "phase1_mutates_repo": False,
        "r8c_status": (
            "C1_ADAPTER_ONLY_NOT_TOOLING_ENGINEERING"
        ),
    }


def _objective(
    args,
    proposal_json: Path,
) -> str:

    if args.objective_file:

        raw = Path(
            args.objective_file
        ).read_bytes()

        try:
            return raw.decode(
                "utf-8-sig"
            )
        except UnicodeDecodeError as exc:
            raise CandidateExportError(
                "OBJECTIVE_FILE_NOT_UTF8"
            ) from exc

    if args.objective:
        return args.objective

    data = _read_json(
        proposal_json
    )

    return str(
        data.get(
            "objective"
        )
        or ""
    )


def main(
    argv: list[str] | None = None,
) -> int:

    parser = argparse.ArgumentParser(
        prog=(
            "obsidure-candidate-export"
        ),
        description=(
            "R8-C1: export an existing "
            "Obsidure proposal as an exact "
            "REAL_UNIFIED_DIFF_V1 candidate."
        ),
    )

    parser.add_argument(
        "--proposal-id",
    )

    parser.add_argument(
        "--proposal-json",
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
        "--output-root",
    )

    parser.add_argument(
        "--objective",
    )

    parser.add_argument(
        "--objective-file",
    )

    parser.add_argument(
        "--phase1",
        action="store_true",
        help=(
            "Build and print Obsidia "
            "PLAN_PROPOSED only. "
            "No approval / no Phase 2."
        ),
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

    repo_root = Path(
        args.repo_root
    ).resolve()

    if bool(
        args.proposal_id
    ) == bool(
        args.proposal_json
    ):
        parser.error(
            "exactly one of "
            "--proposal-id or "
            "--proposal-json is required"
        )

    if args.proposal_id:

        proposal_json = (
            _proposal_json_from_id(
                repo_root,
                args.proposal_id,
            )
        )

    else:

        proposal_json = Path(
            args.proposal_json
        ).resolve()

    output_root = (
        Path(
            args.output_root
        ).resolve()
        if args.output_root
        else None
    )

    candidate = (
        export_proposal_candidate(
            repo_root,
            proposal_json,
            output_root,
        )
    )

    print(
        "CANDIDATE_EXPORTED"
    )

    print(
        f"proposal_id = "
        f"{candidate.proposal_id}"
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

        objective = _objective(
            args,
            proposal_json,
        )

        plan = build_phase1_plan(
            repo_root,
            objective,
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
