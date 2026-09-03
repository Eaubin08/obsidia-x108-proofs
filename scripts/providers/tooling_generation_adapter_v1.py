"""
R8-C3a — Bounded Tooling Code Generation Adapter V1.

Purpose:
    Turn an explicit engineering objective + one exact tracked source file
    into an EXTERNAL generated-source artifact.

Important:
    This adapter does NOT create candidate.patch.
    C2 remains responsible for source -> candidate.patch.
    B1/Build remains responsible for governed mutation.

Boundary:
    decision_authority = KX108_ONLY
    generation_authority = NONE
    execution_authority = False
    memory_write = False
    kernel_mutation = False
    emits_act = False
    auto_apply = False
    auto_commit = False
    push = False
    merge = False
    world_action = False
    kx108_invoked = False

The provider receives source CONTENT and relative target metadata.
It does not receive a repository path or mutation primitive.

Repository immutability is checked before and after provider execution.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid

from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.providers.tooling_generation_contract_v1 import (
    TOOLING_GENERATION_CONTRACT,
    TOOLING_GENERATION_MODE,
    TOOLING_GENERATION_PROMPT_CONTRACT,
    ToolingGenerationProvider,
    ToolingGenerationProviderResult,
    ToolingGenerationRequest,
)


MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_PROMPT_BYTES = 8 * 1024 * 1024

_GENERATION_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


class ToolingGenerationError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def _same_path(a: Path, b: Path) -> bool:
    return os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve()))


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _run_git_readonly(
    repo: Path,
    *args: str,
) -> str:
    """
    Deliberately tiny git read surface.

    Dynamic mutation subcommands are not accepted here.
    """

    allowed_exact = {
        ("rev-parse", "HEAD"),
        ("rev-parse", "--show-toplevel"),
        ("status", "--porcelain=v1"),
    }

    if tuple(args) not in allowed_exact:
        raise ToolingGenerationError(
            "GIT_READ_SURFACE_REJECTED"
        )

    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    if proc.returncode != 0:
        raise ToolingGenerationError(
            "GIT_READ_FAILED:"
            + (proc.stderr or "").strip()[:400]
        )

    return proc.stdout.rstrip("\r\n")


def _require_tracked_target(
    repo: Path,
    rel: str,
) -> None:
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "ls-files",
            "--error-unmatch",
            "--",
            rel,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    if proc.returncode != 0:
        raise ToolingGenerationError(
            "TARGET_NOT_TRACKED"
        )


def _normalize_target_path(
    target_path: str,
) -> str:
    raw = str(target_path or "").strip()

    if not raw:
        raise ToolingGenerationError(
            "TARGET_REQUIRED"
        )

    if "\\" in raw:
        raise ToolingGenerationError(
            "TARGET_BACKSLASH_REJECTED"
        )

    if raw.startswith("/") or re.match(
        r"^[A-Za-z]:",
        raw,
    ):
        raise ToolingGenerationError(
            "TARGET_ABSOLUTE_REJECTED"
        )

    pure = PurePosixPath(raw)

    if (
        not pure.parts
        or any(
            part in ("", ".", "..")
            for part in pure.parts
        )
    ):
        raise ToolingGenerationError(
            "TARGET_TRAVERSAL_REJECTED"
        )

    return pure.as_posix()


def _canonical_prompt(
    *,
    objective: str,
    target_path: str,
    base_sha: str,
    target_before_sha256: str,
    current_source: str,
) -> str:
    payload = {
        "contract": TOOLING_GENERATION_PROMPT_CONTRACT,
        "objective": objective,
        "target_path": target_path,
        "base_sha": base_sha,
        "target_before_sha256": target_before_sha256,
        "current_source": current_source,
        "boundary": {
            "decision_authority": "KX108_ONLY",
            "provider_authority": "NONE",
            "repo_input": "READONLY",
            "output": "SOURCE_ARTIFACT_ONLY",
            "apply": False,
            "stage": False,
            "commit": False,
            "push": False,
            "merge": False,
            "memory_write": False,
            "kernel_mutation": False,
            "emits_act": False,
            "world_action": False,
        },
        "instructions": [
            (
                "Return the exact complete UTF-8 content of the target file "
                "after the proposed engineering change."
            ),
            "Return source content only.",
            "Do not use Markdown code fences.",
            "Do not emit a unified diff.",
            "Do not execute commands.",
            "Do not claim decision or execution authority.",
            "Do not claim that the output was applied.",
            "Do not mutate memory, kernel, repository, or world state.",
        ],
    }

    prompt = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ToolingGenerationError(
            "GENERATION_PROMPT_TOO_LARGE"
        )

    return prompt


def _validate_provider_result(
    result: Any,
) -> ToolingGenerationProviderResult:
    if not isinstance(
        result,
        ToolingGenerationProviderResult,
    ):
        raise ToolingGenerationError(
            "PROVIDER_RESULT_CONTRACT_INVALID"
        )

    if not result.provider_id.strip():
        raise ToolingGenerationError(
            "PROVIDER_ID_REQUIRED"
        )

    if not result.model_id.strip():
        raise ToolingGenerationError(
            "MODEL_ID_REQUIRED"
        )

    if not isinstance(result.output_text, str):
        raise ToolingGenerationError(
            "PROVIDER_OUTPUT_NOT_TEXT"
        )

    if not result.output_text.strip():
        raise ToolingGenerationError(
            "PROVIDER_OUTPUT_EMPTY"
        )

    if "```" in result.output_text:
        raise ToolingGenerationError(
            "PROVIDER_OUTPUT_MARKDOWN_FENCE_REJECTED"
        )

    raw = result.output_text.encode("utf-8")

    if len(raw) > MAX_SOURCE_BYTES:
        raise ToolingGenerationError(
            "PROVIDER_OUTPUT_TOO_LARGE"
        )

    return result


def _assert_repo_unchanged(
    repo: Path,
    *,
    expected_head: str,
    expected_status: str,
    phase: str,
) -> tuple[str, str]:
    head = _run_git_readonly(
        repo,
        "rev-parse",
        "HEAD",
    )

    status = _run_git_readonly(
        repo,
        "status",
        "--porcelain=v1",
    )

    if head != expected_head:
        raise ToolingGenerationError(
            f"REPO_HEAD_MUTATED_DURING_{phase}"
        )

    if status != expected_status:
        raise ToolingGenerationError(
            f"REPO_STATUS_MUTATED_DURING_{phase}"
        )

    return head, status


def generate_tooling_source(
    *,
    repo_root: Path | str,
    objective: str,
    target_path: str,
    artifact_root: Path | str,
    provider: ToolingGenerationProvider,
    generation_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate one untrusted source artifact outside the repository.

    No candidate patch is created here.
    No repository mutation is authorized here.
    """

    repo = Path(repo_root).resolve()

    if not repo.exists() or not repo.is_dir():
        raise ToolingGenerationError(
            "REPO_ROOT_INVALID"
        )

    actual_top = Path(
        _run_git_readonly(
            repo,
            "rev-parse",
            "--show-toplevel",
        )
    ).resolve()

    if not _same_path(
        actual_top,
        repo,
    ):
        raise ToolingGenerationError(
            "REPO_ROOT_MUST_BE_GIT_TOPLEVEL"
        )

    head_before = _run_git_readonly(
        repo,
        "rev-parse",
        "HEAD",
    )

    status_before = _run_git_readonly(
        repo,
        "status",
        "--porcelain=v1",
    )

    if status_before:
        raise ToolingGenerationError(
            "REPO_MUST_BE_CLEAN"
        )

    objective_text = str(objective or "")

    if not objective_text.strip():
        raise ToolingGenerationError(
            "OBJECTIVE_REQUIRED"
        )

    rel = _normalize_target_path(
        target_path
    )

    target = (
        repo
        / Path(*PurePosixPath(rel).parts)
    ).resolve()

    if not _is_within(
        target,
        repo,
    ):
        raise ToolingGenerationError(
            "TARGET_OUTSIDE_REPO"
        )

    if not target.exists() or not target.is_file():
        raise ToolingGenerationError(
            "TARGET_FILE_MISSING"
        )

    _require_tracked_target(
        repo,
        rel,
    )

    artifact_base = Path(
        artifact_root
    ).resolve()

    if _is_within(
        artifact_base,
        repo,
    ):
        raise ToolingGenerationError(
            "ARTIFACT_ROOT_INSIDE_REPO_REJECTED"
        )

    source_before_bytes = target.read_bytes()

    if len(source_before_bytes) > MAX_SOURCE_BYTES:
        raise ToolingGenerationError(
            "TARGET_SOURCE_TOO_LARGE"
        )

    try:
        current_source = source_before_bytes.decode(
            "utf-8"
        )
    except UnicodeDecodeError as exc:
        raise ToolingGenerationError(
            "TARGET_SOURCE_NOT_UTF8"
        ) from exc

    target_before_sha256 = _sha256_bytes(
        source_before_bytes
    )

    objective_sha256 = _sha256_text(
        objective_text
    )

    prompt = _canonical_prompt(
        objective=objective_text,
        target_path=rel,
        base_sha=head_before,
        target_before_sha256=target_before_sha256,
        current_source=current_source,
    )

    prompt_sha256 = _sha256_text(
        prompt
    )

    gid = generation_id or (
        "toolgen-"
        + uuid.uuid4().hex[:16]
    )

    if not _GENERATION_ID_RE.fullmatch(
        gid
    ):
        raise ToolingGenerationError(
            "GENERATION_ID_INVALID"
        )

    request = ToolingGenerationRequest(
        generation_id=gid,
        objective=objective_text,
        objective_sha256=objective_sha256,
        target_path=rel,
        base_sha=head_before,
        target_before_sha256=target_before_sha256,
        prompt=prompt,
        prompt_sha256=prompt_sha256,
        current_source=current_source,
    )

    try:
        provider_result = provider.generate(
            request
        )
    except Exception as exc:
        try:
            _assert_repo_unchanged(
                repo,
                expected_head=head_before,
                expected_status=status_before,
                phase="FAILED_PROVIDER_CALL",
            )
        except ToolingGenerationError as mutation_exc:
            raise mutation_exc from exc

        raise ToolingGenerationError(
            "PROVIDER_GENERATION_FAILED:"
            + type(exc).__name__
        ) from exc

    # Provider execution is untrusted.
    # Verify repository state BEFORE accepting its returned bytes.
    _assert_repo_unchanged(
        repo,
        expected_head=head_before,
        expected_status=status_before,
        phase="PROVIDER_CALL",
    )

    provider_result = _validate_provider_result(
        provider_result
    )

    generated_bytes = (
        provider_result.output_text.encode(
            "utf-8"
        )
    )

    raw_response_sha256 = _sha256_bytes(
        generated_bytes
    )

    source_sha256 = _sha256_bytes(
        generated_bytes
    )

    source_rel = (
        PurePosixPath(gid)
        / "source"
        / PurePosixPath(rel)
    )

    source_path = (
        artifact_base
        / Path(*source_rel.parts)
    )

    receipt_path = (
        artifact_base
        / gid
        / "generation_receipt.json"
    )

    source_path.parent.mkdir(
        parents=True,
        exist_ok=False,
    )

    source_path.write_bytes(
        generated_bytes
    )

    head_after_artifact, status_after_artifact = (
        _assert_repo_unchanged(
            repo,
            expected_head=head_before,
            expected_status=status_before,
            phase="EXTERNAL_ARTIFACT_WRITE",
        )
    )

    receipt = {
        "schema": TOOLING_GENERATION_CONTRACT,
        "mode": TOOLING_GENERATION_MODE,
        "generation_id": gid,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "base_sha": head_before,
        "objective_sha256": objective_sha256,
        "target_path": rel,
        "target_before_sha256": target_before_sha256,
        "prompt_contract": TOOLING_GENERATION_PROMPT_CONTRACT,
        "prompt_sha256": prompt_sha256,
        "provider_id": provider_result.provider_id,
        "model_id": provider_result.model_id,
        "raw_response_sha256": raw_response_sha256,
        "source_sha256": source_sha256,
        "source_bytes": len(generated_bytes),
        "source_artifact": source_rel.as_posix(),
        "response_normalized": False,
        "repo_head_before": head_before,
        "repo_head_after": head_after_artifact,
        "repo_status_before": status_before,
        "repo_status_after": status_after_artifact,
        "readonly_repo_input": True,
        "artifact_only": True,
        "candidate_patch_created": False,
        "decision_authority": "KX108_ONLY",
        "generation_authority": "NONE",
        "provider_is_authority": False,
        "can_decide": False,
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "auto_apply": False,
        "auto_commit": False,
        "push": False,
        "merge": False,
        "world_action": False,
        "kx108_invoked": False,
    }

    receipt_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    receipt_path.write_text(
        json.dumps(
            receipt,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    head_final, status_final = (
        _assert_repo_unchanged(
            repo,
            expected_head=head_before,
            expected_status=status_before,
            phase="RECEIPT_WRITE",
        )
    )

    if (
        head_final
        != receipt["repo_head_after"]
        or status_final
        != receipt["repo_status_after"]
    ):
        raise ToolingGenerationError(
            "FINAL_REPO_STATE_MISMATCH"
        )

    return {
        "status": "SOURCE_ARTIFACT_GENERATED",
        "generation_id": gid,
        "provider_id": provider_result.provider_id,
        "model_id": provider_result.model_id,
        "target_path": rel,
        "base_sha": head_before,
        "objective_sha256": objective_sha256,
        "prompt_sha256": prompt_sha256,
        "source_sha256": source_sha256,
        "source_artifact_path": str(
            source_path
        ),
        "generation_receipt_path": str(
            receipt_path
        ),
        "decision_authority": "KX108_ONLY",
        "generation_authority": "NONE",
        "can_decide": False,
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "auto_apply": False,
        "auto_commit": False,
        "push": False,
        "merge": False,
        "world_action": False,
        "kx108_invoked": False,
    }