"""
R8-C3b4 — Obsidia Native Solve Stack V1.

Canonical internal solve stack:

    Brody native structural cognition
        ->
    Obsidure native bounded strategy solver
        ->
    ObsidiaToolingGenerator
        ->
    C3a

Obsidia remains the canonical visible producer.

The solver remains a non-authoritative backend.
"""

from __future__ import annotations

from typing import Any

from scripts.providers.obsidia_tooling_generator_v1 import (
    ObsidiaToolingGenerator,
)

from scripts.providers.obsidure_native_solve_engine_v1 import (
    BACKEND_ID,
    MODEL_ID,
    ObsidureNativeSolveEngine,
)

from scripts.providers.tooling_generation_contract_v1 import (
    ToolingGenerationProviderResult,
    ToolingGenerationRequest,
)


STACK_ID = (
    "OBSIDIA_NATIVE_SOLVE_STACK_V1"
)


class ObsidiaNativeSolveStack:

    provider_id = (
        "OBSIDIA_TOOLING_GENERATOR_V1"
    )


    def __init__(
        self,
    ) -> None:

        self.backend = (
            ObsidureNativeSolveEngine()
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


        generator_metadata = dict(
            self.generator.last_metadata
            or {}
        )


        self.last_metadata = {
            "stack_id": STACK_ID,
            "provider_id": (
                result.provider_id
            ),
            "backend_id": (
                BACKEND_ID
            ),
            "model_id": (
                MODEL_ID
            ),
            "generator_metadata": (
                generator_metadata
            ),
            "solve_attempts": list(
                self.backend.last_attempts
            ),
            "native": True,
            "external_model": False,
            "producer_authority": (
                "NONE"
            ),
            "backend_authority": (
                "NONE"
            ),
            "decision_authority": (
                "KX108_ONLY"
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
            "READONLY_STRUCTURAL_COGNITION"
        ),
        "obsidure_role": (
            "BOUNDED_NATIVE_SOLVE_ENGINE"
        ),
        "strategy_fallback": True,
        "native": True,
        "external_model": False,
        "producer_authority": (
            "NONE"
        ),
        "backend_authority": (
            "NONE"
        ),
        "decision_authority": (
            "KX108_ONLY"
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
