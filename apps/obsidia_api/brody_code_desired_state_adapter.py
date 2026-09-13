"""
Brody Code Desired-State Adapter V1.

EngineeringSpec
    -> existing Brody/OS_TRAD cognition
    -> learned CodeConcept
    -> DesiredState

This adapter never generates Python source.
Unknown concepts remain unknown.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import copy
from typing import Any

from apps.obsidia_api.brody_code_concept_engine import (
    match_code_concept,
)

from apps.obsidia_api.brody_code_concepts_v1 import (
    DEFAULT_CODE_CONCEPTS,
)

from apps.obsidia_api.brody_code_intent_adapter import (
    build_brody_code_intent_packet,
)


ADAPTER_ID = (
    "BRODY_CODE_DESIRED_STATE_ADAPTER_V1"
)


@dataclass
class LearnedDesiredStateResult:
    status: str

    engineering_spec: dict[str, Any]

    code_intent: dict[str, Any] = field(
        default_factory=dict
    )

    concept_match: dict[str, Any] = field(
        default_factory=dict
    )

    unknowns: list[str] = field(
        default_factory=list
    )

    can_generate_source: bool = False
    can_decide: bool = False
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _target_paths(
    spec: dict[str, Any],
) -> list[str]:

    paths: list[str] = []

    for target in (
        spec.get("targets")
        or []
    ):

        if not isinstance(
            target,
            dict,
        ):
            continue

        path = str(
            target.get(
                "path",
                "",
            )
            or ""
        ).replace("\\", "/").strip()

        if path:
            paths.append(path)

    return paths


def derive_learned_desired_state(
    engineering_spec: dict[str, Any],
) -> LearnedDesiredStateResult:

    if not isinstance(
        engineering_spec,
        dict,
    ):
        raise ValueError(
            "ENGINEERING_SPEC_NOT_OBJECT"
        )

    enriched = copy.deepcopy(
        engineering_spec
    )

    objective = str(
        enriched.get(
            "objective",
            "",
        )
        or ""
    )

    packet = (
        build_brody_code_intent_packet(
            objective,
            target_paths=_target_paths(
                enriched
            ),
        )
    )

    match = match_code_concept(
        packet,
        DEFAULT_CODE_CONCEPTS,
    )

    # Always keep the readonly cognition trace.
    enriched["code_cognition"] = {
        "adapter_id": ADAPTER_ID,
        "intent": packet.to_dict(),
        "concept": match.to_dict(),
    }

    if (
        match.status
        == "CODE_CONCEPT_RESOLVED"
        and match.desired_state
        is not None
    ):

        enriched["desired_state"] = (
            copy.deepcopy(
                match.desired_state
            )
        )

        return LearnedDesiredStateResult(
            status=(
                "DESIRED_STATE_DERIVED"
            ),
            engineering_spec=enriched,
            code_intent=packet.to_dict(),
            concept_match=match.to_dict(),
        )

    return LearnedDesiredStateResult(
        status=match.status,
        engineering_spec=enriched,
        code_intent=packet.to_dict(),
        concept_match=match.to_dict(),
        unknowns=list(
            match.unknowns
        ),
    )


def self_check() -> dict[str, Any]:

    return {
        "adapter_id": ADAPTER_ID,
        "role": (
            "ENGINEERING_SPEC_TO_LEARNED_DESIRED_STATE"
        ),
        "uses_existing_brody_cognition": True,
        "uses_learned_code_concepts": True,
        "unknown_concepts_are_not_invented": True,
        "raw_python_generation": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
