"""
Obsidure Native Decomposer V1.

Compiles explicit semantic engineering deltas into executable NativePlanSteps.

A NativeDelta describes a precise requested source transformation.
This module never infers source code from free natural language.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any

from periphery.agents.obsidure_native_plan import (
    NativePlan,
    NativePlanStep,
    PRIMITIVES,
)


DECOMPOSER_ID = "OBSIDURE_NATIVE_DECOMPOSER_V1"


class NativeDecompositionError(RuntimeError):
    pass


@dataclass(frozen=True)
class NativeDelta:
    primitive: str
    target_path: str
    parameters: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    delta_id: str = ""


_REQUIRED_PARAMETERS: dict[str, tuple[str, ...]] = {
    "CREATE_FILE": (
        "source",
    ),
    "ADD_IMPORT": (
        "statement",
    ),
    "ADD_FUNCTION": (
        "source",
    ),
    "ADD_TEST": (
        "source",
    ),
    "ADD_CLASS": (
        "source",
    ),
    "MODIFY_FUNCTION": (
        "name",
        "source",
    ),
    "ADD_METHOD": (
        "class_name",
        "source",
    ),
    "MODIFY_METHOD": (
        "class_name",
        "name",
        "source",
    ),
    "MODIFY_CLASS": (
        "name",
        "source",
    ),
    "ADD_FIELD": (
        "class_name",
        "source",
    ),
    "MODIFY_FIELD": (
        "class_name",
        "name",
        "source",
    ),
}


def _step_id(
    request_id: str,
    index: int,
    delta: NativeDelta,
) -> str:

    raw = (
        f"{request_id}:"
        f"{index}:"
        f"{delta.primitive}:"
        f"{delta.target_path}:"
        f"{delta.delta_id}"
    )

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:12]

    return f"ndp_{digest}"


def _validate_delta(
    delta: NativeDelta,
) -> None:

    primitive = str(
        delta.primitive
        or ""
    ).strip()

    target = str(
        delta.target_path
        or ""
    ).replace("\\", "/").strip()

    if primitive not in PRIMITIVES:
        raise NativeDecompositionError(
            f"DELTA_PRIMITIVE_UNKNOWN:{primitive}"
        )

    if not PRIMITIVES[primitive].get(
        "execution_ready",
        False,
    ):
        raise NativeDecompositionError(
            f"DELTA_PRIMITIVE_NOT_EXECUTABLE:{primitive}"
        )

    if not target:
        raise NativeDecompositionError(
            "DELTA_TARGET_REQUIRED"
        )

    required = _REQUIRED_PARAMETERS.get(
        primitive,
        (),
    )

    for key in required:
        value = delta.parameters.get(key)

        if value is None:
            raise NativeDecompositionError(
                f"DELTA_PARAMETER_REQUIRED:{primitive}:{key}"
            )

        if isinstance(value, str) and not value.strip():
            raise NativeDecompositionError(
                f"DELTA_PARAMETER_EMPTY:{primitive}:{key}"
            )


def compile_native_deltas_to_plan(
    *,
    request_id: str,
    spec_id: str,
    objective: str,
    deltas: list[NativeDelta],
    acceptance_criteria: list[str] | None = None,
) -> NativePlan:

    if not deltas:
        raise NativeDecompositionError(
            "NATIVE_DELTAS_REQUIRED"
        )

    steps: list[NativePlanStep] = []

    previous_step: str | None = None

    for index, delta in enumerate(
        deltas,
        start=1,
    ):
        _validate_delta(delta)

        sid = _step_id(
            request_id,
            index,
            delta,
        )

        step = NativePlanStep(
            step_id=sid,
            primitive=delta.primitive,
            target_path=delta.target_path.replace(
                "\\",
                "/",
            ),
            rationale=(
                delta.rationale
                or f"Native delta {delta.primitive}"
            ),
            parameters=dict(delta.parameters),
            depends_on=(
                (previous_step,)
                if previous_step
                else ()
            ),
            execution_ready=True,
        )

        steps.append(step)
        previous_step = sid

    acceptance = [
        str(value)
        for value in (
            acceptance_criteria
            or []
        )
        if str(value).strip()
    ]

    if acceptance:

        raw = (
            f"{request_id}:verify:"
            f"{previous_step or ''}"
        )

        verify_id = (
            "ndp_"
            + hashlib.sha256(
                raw.encode("utf-8")
            ).hexdigest()[:12]
        )

        steps.append(
            NativePlanStep(
                step_id=verify_id,
                primitive="VERIFY_TESTS",
                target_path="<acceptance>",
                rationale=(
                    "Verify declared acceptance criteria."
                ),
                parameters={
                    "criteria": acceptance,
                },
                depends_on=(
                    (previous_step,)
                    if previous_step
                    else ()
                ),
                execution_ready=True,
            )
        )

    return NativePlan(
        request_id=request_id,
        spec_id=spec_id,
        objective=objective,
        steps=steps,
        acceptance_criteria=acceptance,
        missing_capabilities=[],
    )


def self_check() -> dict[str, Any]:
    return {
        "decomposer_id": DECOMPOSER_ID,
        "accepted_primitives": sorted(
            _REQUIRED_PARAMETERS
        ),
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
