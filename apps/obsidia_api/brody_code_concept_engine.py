"""
Brody Code Concept Engine V1.

Educational semantic layer for native code cognition.

A CodeConcept teaches Brody how a known semantic capability maps to a
structured DesiredState.

No Python source is stored or generated here.

Learning model:
    existing Brody cognition
        -> CodeIntentPacket
        -> learned CodeConcept
        -> DesiredState

New concepts can be added progressively without changing Obsidure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import copy
import re
from typing import Any, Iterable

from apps.obsidia_api.brody_code_intent_adapter import (
    BrodyCodeIntentPacket,
)


ENGINE_ID = "BRODY_CODE_CONCEPT_ENGINE_V1"


@dataclass(frozen=True)
class CodeConcept:
    concept_id: str

    required_terms: tuple[str, ...] = ()
    any_terms: tuple[str, ...] = ()

    allowed_intents: tuple[str, ...] = ()

    desired_state_template: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CodeConceptMatch:
    status: str
    concept_id: str = ""
    score: float = 0.0

    matched_terms: list[str] = field(
        default_factory=list
    )

    desired_state: dict[str, Any] | None = None

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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize(
    value: str,
) -> str:

    value = str(
        value
        or ""
    ).lower()

    value = re.sub(
        r"[_\-/]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _semantic_haystack(
    packet: BrodyCodeIntentPacket,
) -> str:

    return _normalize(
        " ".join([
            packet.request_text,
            packet.intent_type,
            packet.semantic_topic,
            packet.semantic_query,
        ])
    )


def _replace_placeholders(
    value: Any,
    targets: list[str],
) -> Any:

    if isinstance(value, str):

        result = value

        for index, target in enumerate(
            targets
        ):
            result = result.replace(
                f"$TARGET{index}",
                target,
            )

        return result

    if isinstance(value, list):

        return [
            _replace_placeholders(
                item,
                targets,
            )
            for item in value
        ]

    if isinstance(value, dict):

        return {
            key: _replace_placeholders(
                child,
                targets,
            )
            for key, child
            in value.items()
        }

    return value


def match_code_concept(
    packet: BrodyCodeIntentPacket,
    concepts: Iterable[CodeConcept],
) -> CodeConceptMatch:

    haystack = _semantic_haystack(
        packet
    )

    best: CodeConcept | None = None
    best_score = 0.0
    best_terms: list[str] = []

    for concept in concepts:

        if (
            concept.allowed_intents
            and packet.intent_type
            not in concept.allowed_intents
        ):
            continue

        required = [
            _normalize(term)
            for term in concept.required_terms
            if _normalize(term)
        ]

        optional = [
            _normalize(term)
            for term in concept.any_terms
            if _normalize(term)
        ]

        if any(
            term not in haystack
            for term in required
        ):
            continue

        matched_optional = [
            term
            for term in optional
            if term in haystack
        ]

        if (
            optional
            and not matched_optional
        ):
            continue

        matched = (
            required
            + matched_optional
        )

        denominator = max(
            1,
            len(required)
            + len(optional),
        )

        score = min(
            1.0,
            len(matched)
            / denominator,
        )

        if score > best_score:
            best = concept
            best_score = score
            best_terms = matched

    if best is None:

        return CodeConceptMatch(
            status="UNKNOWN_CODE_CONCEPT",
            unknowns=[
                "BRODY_CODE_CONCEPT_NOT_EDUCATED"
            ],
        )

    if not packet.target_paths:

        return CodeConceptMatch(
            status="NEEDS_CONTEXT",
            concept_id=best.concept_id,
            score=best_score,
            matched_terms=best_terms,
            unknowns=[
                "CODE_TARGET_UNKNOWN"
            ],
        )

    desired = _replace_placeholders(
        copy.deepcopy(
            best.desired_state_template
        ),
        packet.target_paths,
    )

    return CodeConceptMatch(
        status="CODE_CONCEPT_RESOLVED",
        concept_id=best.concept_id,
        score=best_score,
        matched_terms=best_terms,
        desired_state=desired,
    )


def self_check() -> dict[str, Any]:
    return {
        "engine_id": ENGINE_ID,
        "role": "PROGRESSIVE_CODE_SEMANTIC_EDUCATION",
        "raw_python_generation": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
    }
