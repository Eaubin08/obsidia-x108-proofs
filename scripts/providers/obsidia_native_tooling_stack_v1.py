"""
R8-C3b2 — Obsidia Native Tooling Stack V1.

Canonical internal stack:

    C3a canonical prompt
        -> Brody native readonly cognition/context
        -> Obsidure native bounded engineering synthesis
        -> ObsidiaToolingGenerator
        -> complete untrusted source

No external model/provider is involved.

KX108 remains the sole decision authority.
"""

from __future__ import annotations

from typing import Any

from scripts.providers.obsidia_tooling_generator_v1 import (
    ObsidiaToolingGenerator,
)

from scripts.providers.obsidure_native_tooling_backend_v1 import (
    BACKEND_ID,
    MODEL_ID,
    ObsidureNativeToolingBackend,
)

from scripts.providers.tooling_generation_contract_v1 import (
    ToolingGenerationProviderResult,
    ToolingGenerationRequest,
)


STACK_ID = (
    "OBSIDIA_NATIVE_TOOLING_STACK_V1"
)

DECISION_AUTHORITY = "KX108_ONLY"


class ObsidiaNativeToolingStack:

    provider_id = (
        "OBSIDIA_TOOLING_GENERATOR_V1"
    )


    def __init__(
        self,
    ) -> None:

        self.backend = (
            ObsidureNativeToolingBackend()
        )

        self.generator = (
            ObsidiaToolingGenerator(
                backend=self.backend
            )
        )

        self.last_metadata: dict[
            str,
            Any,
        ] | None = None


    def generate(
        self,
        request: ToolingGenerationRequest,
    ) -> ToolingGenerationProviderResult:

        result = (
            self.generator.generate(
                request
            )
        )


        self.last_metadata = {
            "stack_id": STACK_ID,
            "producer_id": (
                result.provider_id
            ),
            "backend_id": (
                BACKEND_ID
            ),
            "model_id": (
                MODEL_ID
            ),
            "generator_metadata": (
                dict(
                    self.generator.last_metadata
                    or {}
                )
            ),
            "native": True,
            "external_model": False,
            "producer_authority": "NONE",
            "backend_authority": "NONE",
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "memory_write": False,
            "kernel_mutation": False,
            "emits_act": False,
            "world_action": False,
        }


        return result


def self_check() -> dict[str, Any]:

    return {
        "stack_id": STACK_ID,
        "producer": (
            "OBSIDIA_TOOLING_GENERATOR_V1"
        ),
        "brody_role": (
            "READONLY_COGNITION_CONTEXT"
        ),
        "obsidure_role": (
            "NATIVE_ENGINEERING_SYNTHESIS"
        ),
        "backend_id": BACKEND_ID,
        "model_id": MODEL_ID,
        "native": True,
        "external_model": False,
        "producer_authority": "NONE",
        "backend_authority": "NONE",
        "decision_authority": (
            DECISION_AUTHORITY
        ),
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
