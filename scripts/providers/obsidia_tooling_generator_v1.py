"""
R8-C3b — Obsidia Tooling Generator V1.

Canonical GENERATION SURFACE owned by Obsidia.

Obsidia owns:
    objective/context boundary,
    generation request,
    producer identity,
    provenance,
    candidate handoff.

A backend owns only token/text generation.

Backends are interchangeable organs:
    LOCAL_MODEL
    ANTHROPIC
    OPENAI
    GEMINI
    CLAUDE_CLI
    BRODY_NATIVE
    OBSIDURE_NATIVE
    other bounded engines

The backend is NOT decision authority.

Canonical chain:

    ToolingGenerationRequest
        -> OBSIDIA_TOOLING_GENERATOR_V1
        -> selected token backend
        -> complete untrusted source
        -> C3a artifact/receipt
        -> C2 candidate.patch
        -> Build
        -> tests/gates
        -> KX108

Authority remains:

    producer_authority = NONE
    backend_authority = NONE
    decision_authority = KX108_ONLY
    world_action = false
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

from scripts.providers.tooling_generation_contract_v1 import (
    ToolingGenerationProviderResult,
    ToolingGenerationRequest,
)


PRODUCER_ID = (
    "OBSIDIA_TOOLING_GENERATOR_V1"
)

PRODUCER_AUTHORITY = "NONE"
BACKEND_AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"


@dataclass(
    frozen=True
)
class ToolingBackendResult:
    """
    Raw non-authoritative result from one token engine.
    """

    backend_id: str
    model_id: str
    output_text: str

    metadata: Mapping[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


@runtime_checkable
class ToolingGenerationBackend(
    Protocol
):
    """
    Token-generation organ only.

    It receives the canonical prompt, not a repo mutation surface.
    """

    backend_id: str

    def generate_text(
        self,
        prompt: str,
    ) -> ToolingBackendResult:
        ...


class ObsidiaToolingGeneratorError(
    RuntimeError
):
    pass


class ObsidiaToolingGenerator:
    """
    Canonical Obsidia tooling-generation producer.

    The backend is an interchangeable engine.

    This producer does not:
        read/write repo itself,
        apply patches,
        stage,
        commit,
        push,
        merge,
        mutate memory/kernel,
        invoke KX108,
        emit ACT,
        perform WorldAction.
    """

    provider_id = PRODUCER_ID

    def __init__(
        self,
        *,
        backend: ToolingGenerationBackend,
    ) -> None:

        if not isinstance(
            backend,
            ToolingGenerationBackend,
        ):
            raise ObsidiaToolingGeneratorError(
                "BACKEND_CONTRACT_INVALID"
            )

        backend_id = str(
            getattr(
                backend,
                "backend_id",
                "",
            )
            or ""
        ).strip()

        if not backend_id:
            raise ObsidiaToolingGeneratorError(
                "BACKEND_ID_REQUIRED"
            )

        self.backend = backend
        self.backend_id = backend_id

        self.last_metadata: dict[
            str,
            Any,
        ] | None = None


    def generate(
        self,
        request: ToolingGenerationRequest,
    ) -> ToolingGenerationProviderResult:

        try:
            result = (
                self.backend
                .generate_text(
                    request.prompt
                )
            )

        except Exception as exc:

            raise ObsidiaToolingGeneratorError(
                "BACKEND_GENERATION_FAILED:"
                + type(exc).__name__
            ) from exc


        if not isinstance(
            result,
            ToolingBackendResult,
        ):
            raise ObsidiaToolingGeneratorError(
                "BACKEND_RESULT_INVALID"
            )


        backend_id = str(
            result.backend_id
            or ""
        ).strip()

        model_id = str(
            result.model_id
            or ""
        ).strip()


        if not backend_id:
            raise ObsidiaToolingGeneratorError(
                "BACKEND_RESULT_ID_REQUIRED"
            )


        if backend_id != self.backend_id:
            raise ObsidiaToolingGeneratorError(
                "BACKEND_ID_MISMATCH"
            )


        if not model_id:
            raise ObsidiaToolingGeneratorError(
                "BACKEND_MODEL_ID_REQUIRED"
            )


        if not isinstance(
            result.output_text,
            str,
        ):
            raise ObsidiaToolingGeneratorError(
                "BACKEND_OUTPUT_NOT_TEXT"
            )


        if not result.output_text.strip():
            raise ObsidiaToolingGeneratorError(
                "BACKEND_OUTPUT_EMPTY"
            )


        self.last_metadata = {
            "producer_id": PRODUCER_ID,
            "producer_authority": (
                PRODUCER_AUTHORITY
            ),
            "backend_id": backend_id,
            "backend_model_id": model_id,
            "backend_authority": (
                BACKEND_AUTHORITY
            ),
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "objective_sha256": (
                request.objective_sha256
            ),
            "prompt_sha256": (
                request.prompt_sha256
            ),
            "target_path": (
                request.target_path
            ),
            "base_sha": (
                request.base_sha
            ),
            "backend_metadata": dict(
                result.metadata
            ),
            "can_decide": False,
            "repo_mutation": False,
            "memory_write": False,
            "kernel_mutation": False,
            "emits_act": False,
            "auto_apply": False,
            "auto_commit": False,
            "push": False,
            "merge": False,
            "kx108_invoked": False,
            "world_action": False,
        }


        # C3a receipt sees Obsidia as the generation producer.
        #
        # The actual backend/model remains bound in model_id and in
        # last_metadata.
        return ToolingGenerationProviderResult(
            provider_id=PRODUCER_ID,
            model_id=(
                backend_id
                + "/"
                + model_id
            ),
            output_text=(
                result.output_text
            ),
        )


def self_check() -> dict[str, Any]:

    return {
        "producer_id": PRODUCER_ID,
        "producer_authority": (
            PRODUCER_AUTHORITY
        ),
        "backend_authority": (
            BACKEND_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "backend_policy": (
            "INTERCHANGEABLE"
        ),
        "supported_backend_classes": [
            "LOCAL_MODEL",
            "REMOTE_MODEL",
            "CLI_MODEL",
            "BRODY_NATIVE",
            "OBSIDURE_NATIVE",
        ],
        "repo_mutation": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "auto_apply": False,
        "auto_commit": False,
        "push": False,
        "merge": False,
        "kx108_invoked": False,
        "world_action": False,
    }
