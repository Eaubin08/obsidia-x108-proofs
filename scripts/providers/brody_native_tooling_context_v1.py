"""
R8-C3b2 — Brody Native Tooling Context V1.

Native readonly cognition/context organ for Obsidia self-build.

Brody does NOT generate authority and does NOT mutate source.

Input:
    canonical C3a tooling-generation prompt.

Output:
    immutable structural context packet.

Brody role:
    cognition/context/intent structure only.

Authority:
    BRODY_AUTHORITY = NONE
    DECISION_AUTHORITY = KX108_ONLY
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from typing import Any


BRODY_NATIVE_CONTEXT_ID = (
    "BRODY_NATIVE_TOOLING_CONTEXT_V1"
)

BRODY_AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"


class BrodyNativeContextError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True
)
class BrodyNativeToolingContext:

    context_id: str

    objective: str
    target_path: str

    current_source: str

    base_sha: str
    target_before_sha256: str

    prompt_sha256: str

    intent: str
    risk_flags: tuple[str, ...]

    readonly: bool = True
    can_decide: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False
    world_action: bool = False


def _classify_intent(
    objective: str,
) -> str:

    upper = objective.upper()

    if "NATIVE_EDIT_JSON" in upper:
        return "NATIVE_TOOLING_EDIT"

    if any(
        x in upper
        for x in (
            "AUDIT",
            "CHECK",
            "VERIFY",
            "VERIFIE",
            "VÉRIFIE",
        )
    ):
        return "AUDIT"

    return "TOOLING_OBJECTIVE"


def _risk_flags(
    objective: str,
    target_path: str,
) -> tuple[str, ...]:

    text = (
        objective
        + "\n"
        + target_path
    ).lower()

    flags: list[str] = []

    checks = {
        "KERNEL_REFERENCE": (
            "kernel"
        ),
        "PROOF_REFERENCE": (
            "proofs/"
        ),
        "MEMORY_REFERENCE": (
            "memory_write"
        ),
        "ACT_REFERENCE": (
            "emits_act"
        ),
        "GIT_REFERENCE": (
            "git "
        ),
        "DEPLOY_REFERENCE": (
            "deploy"
        ),
    }

    for name, marker in checks.items():

        if marker in text:
            flags.append(
                name
            )

    return tuple(
        flags
    )


def build_brody_native_tooling_context(
    prompt: str,
) -> BrodyNativeToolingContext:

    if not isinstance(
        prompt,
        str,
    ) or not prompt:

        raise BrodyNativeContextError(
            "BRODY_PROMPT_REQUIRED"
        )

    try:
        payload = json.loads(
            prompt
        )

    except Exception as exc:

        raise BrodyNativeContextError(
            "BRODY_PROMPT_JSON_INVALID"
        ) from exc


    if not isinstance(
        payload,
        dict,
    ):
        raise BrodyNativeContextError(
            "BRODY_PROMPT_NOT_OBJECT"
        )


    objective = payload.get(
        "objective"
    )

    target_path = payload.get(
        "target_path"
    )

    current_source = payload.get(
        "current_source"
    )

    base_sha = payload.get(
        "base_sha"
    )

    target_before_sha256 = payload.get(
        "target_before_sha256"
    )


    if not isinstance(
        objective,
        str,
    ) or not objective.strip():

        raise BrodyNativeContextError(
            "BRODY_OBJECTIVE_REQUIRED"
        )


    if not isinstance(
        target_path,
        str,
    ) or not target_path.strip():

        raise BrodyNativeContextError(
            "BRODY_TARGET_REQUIRED"
        )


    if not isinstance(
        current_source,
        str,
    ):
        raise BrodyNativeContextError(
            "BRODY_SOURCE_REQUIRED"
        )


    if not isinstance(
        base_sha,
        str,
    ) or not base_sha:

        raise BrodyNativeContextError(
            "BRODY_BASE_SHA_REQUIRED"
        )


    if not isinstance(
        target_before_sha256,
        str,
    ) or not target_before_sha256:

        raise BrodyNativeContextError(
            "BRODY_TARGET_HASH_REQUIRED"
        )


    prompt_sha = hashlib.sha256(
        prompt.encode(
            "utf-8"
        )
    ).hexdigest()


    return BrodyNativeToolingContext(
        context_id=(
            BRODY_NATIVE_CONTEXT_ID
        ),
        objective=objective,
        target_path=target_path,
        current_source=current_source,
        base_sha=base_sha,
        target_before_sha256=(
            target_before_sha256
        ),
        prompt_sha256=prompt_sha,
        intent=_classify_intent(
            objective
        ),
        risk_flags=_risk_flags(
            objective,
            target_path,
        ),
    )


def self_check() -> dict[str, Any]:

    return {
        "context_id": (
            BRODY_NATIVE_CONTEXT_ID
        ),
        "role": (
            "READONLY_COGNITION_CONTEXT"
        ),
        "brody_authority": (
            BRODY_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "filesystem_write": False,
        "network": False,
        "repo_mutation": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "can_decide": False,
        "world_action": False,
    }
