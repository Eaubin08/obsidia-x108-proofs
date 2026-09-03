"""
OBSIDIA REAL CANDIDATE PATCH V1

Artefact non souverain.

Responsabilités:
- lire un unified diff UTF-8;
- calculer son SHA-256 intégral;
- extraire exactement ses fichiers;
- vérifier qu'il s'applique en readonly;
- l'appliquer uniquement dans le worktree fourni par obsidia_build.

Aucune décision.
Aucun commit.
Aucun push.
Aucun merge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess


CANDIDATE_PATCH_MODE = "REAL_UNIFIED_DIFF_V1"
MAX_CANDIDATE_PATCH_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class CandidatePatchSpec:
    source_path: str
    text: str
    sha256: str
    files: tuple[str, ...]
    mode: str = CANDIDATE_PATCH_MODE


def _safe_repo_relative(raw: str) -> str:
    value = raw.strip()

    if not value:
        raise ValueError("CANDIDATE_EMPTY_PATH")

    if "\\" in value:
        raise ValueError("CANDIDATE_BACKSLASH_PATH_REJECTED")

    p = PurePosixPath(value)

    if p.is_absolute():
        raise ValueError("CANDIDATE_ABSOLUTE_PATH_REJECTED")

    if ".." in p.parts or "." in p.parts:
        raise ValueError("CANDIDATE_TRAVERSAL_REJECTED")

    if value.startswith("-"):
        raise ValueError("CANDIDATE_OPTIONLIKE_PATH_REJECTED")

    return str(p)


def parse_candidate_patch_files(text: str) -> tuple[str, ...]:
    if not text.strip():
        raise ValueError("CANDIDATE_PATCH_EMPTY")

    if "\x00" in text:
        raise ValueError("CANDIDATE_PATCH_NUL_REJECTED")

    forbidden = (
        "GIT binary patch",
        "Binary files ",
        "rename from ",
        "rename to ",
        "copy from ",
        "copy to ",
    )

    for marker in forbidden:
        if marker in text:
            raise ValueError(
                f"CANDIDATE_PATCH_UNSUPPORTED:{marker.strip()}"
            )

    files: list[str] = []

    for line in text.splitlines():
        if not line.startswith("diff --git "):
            continue

        parts = line.split()

        # V1: espaces/quotes dans les chemins refusés explicitement.
        if len(parts) != 4:
            raise ValueError("CANDIDATE_DIFF_HEADER_UNSUPPORTED")

        left = parts[2]
        right = parts[3]

        if not left.startswith("a/") or not right.startswith("b/"):
            raise ValueError("CANDIDATE_DIFF_PREFIX_INVALID")

        left_path = _safe_repo_relative(left[2:])
        right_path = _safe_repo_relative(right[2:])

        # R8-B1 traite MODIFY uniquement.
        # CREATE/DELETE/RENAME seront une extension séparée.
        if left_path != right_path:
            raise ValueError("CANDIDATE_RENAME_REJECTED")

        if left_path not in files:
            files.append(left_path)

    if not files:
        raise ValueError("CANDIDATE_NO_DIFF_FILES")

    return tuple(files)


def load_candidate_patch_file(
    path: str | Path,
    repo_root: str | Path,
) -> CandidatePatchSpec:

    source = Path(path).expanduser()

    if not source.is_file():
        raise ValueError(f"CANDIDATE_PATCH_NOT_FOUND:{source}")

    raw = source.read_bytes()

    if len(raw) > MAX_CANDIDATE_PATCH_BYTES:
        raise ValueError(
            f"CANDIDATE_PATCH_TOO_LARGE:{len(raw)}"
        )

    # Candidate patches have one canonical byte representation.
    # Unlike ObjectiveSpec transport, a patch BOM is rejected rather
    # than normalized because its exact bytes participate in authority.
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("CANDIDATE_PATCH_BOM_REJECTED")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CANDIDATE_PATCH_NOT_UTF8") from exc

    files = parse_candidate_patch_files(text)

    root = Path(repo_root).resolve()

    for rel in files:
        target = (root / rel).resolve()

        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError("CANDIDATE_ESCAPES_REPO") from exc

        # V1 = modification de fichiers existants uniquement.
        if not target.is_file():
            raise ValueError(
                f"CANDIDATE_TARGET_NOT_EXISTING_FILE:{rel}"
            )

    # Integral SHA-256 of the exact candidate.patch bytes.
    digest = hashlib.sha256(raw).hexdigest()

    return CandidatePatchSpec(
        source_path=str(source.resolve()),
        text=text,
        sha256=digest,
        files=files,
    )


def bind_candidate_to_objective(
    objective: str,
    spec: CandidatePatchSpec,
) -> str:

    payload = json.dumps(
        {
            "mode": spec.mode,
            "sha256": spec.sha256,
            "files": list(spec.files),
        },
        sort_keys=True,
        separators=(",", ":"),
    )

    return (
        objective.rstrip()
        + "\n\n"
        + "--- OBSIDIA_CANDIDATE_BINDING_V1 ---\n"
        + payload
    )


def check_candidate_patch(
    spec: CandidatePatchSpec,
    repo_root: str | Path,
) -> tuple[bool, str]:

    patch_bytes = spec.text.encode("utf-8")

    proc = subprocess.run(
        [
            "git",
            "apply",
            "--check",
            "--whitespace=nowarn",
            "-",
        ],
        input=patch_bytes,
        capture_output=True,
        cwd=Path(repo_root),
        timeout=30,
    )

    raw_msg = (
        proc.stdout
        or proc.stderr
        or b""
    )

    msg = raw_msg.decode(
        "utf-8",
        errors="replace",
    ).strip()

    return proc.returncode == 0, msg[:1000]


def apply_candidate_patch(
    spec: CandidatePatchSpec,
    worktree_root: str | Path,
) -> dict:

    root = Path(worktree_root)

    check_ok, check_msg = check_candidate_patch(
        spec,
        root,
    )

    if not check_ok:
        return {
            "ok": False,
            "phase": "GIT_APPLY_CHECK",
            "message": check_msg,
            "files": list(spec.files),
            "sha256": spec.sha256,
        }

    patch_bytes = spec.text.encode("utf-8")

    proc = subprocess.run(
        [
            "git",
            "apply",
            "--whitespace=nowarn",
            "-",
        ],
        input=patch_bytes,
        capture_output=True,
        cwd=root,
        timeout=30,
    )

    raw_msg = (
        proc.stdout
        or proc.stderr
        or b""
    )

    msg = raw_msg.decode(
        "utf-8",
        errors="replace",
    ).strip()

    return {
        "ok": proc.returncode == 0,
        "phase": "GIT_APPLY",
        "message": msg[:1000],
        "files": list(spec.files),
        "sha256": spec.sha256,
    }
