"""
Obsidure Native Program Executor V1.

Executes an already-decomposed NativePlan sequentially in memory.

Each successful step feeds its generated source into the next step.
Nothing is written to the repository.

This layer does NOT invent operations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from periphery.agents.obsidure_native_executor import (
    execute_native_step,
)
from periphery.agents.obsidure_native_plan import (
    NativePlan,
)


PROGRAM_EXECUTOR_ID = "OBSIDURE_NATIVE_PROGRAM_EXECUTOR_V1"


@dataclass
class NativeProgramResult:
    status: str

    completed_steps: list[str] = field(default_factory=list)
    blocked_step: str = ""

    generated_sources: dict[str, str] = field(default_factory=dict)
    step_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False
    repository_write: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def execute_native_plan(
    plan: NativePlan,
    sources: dict[str, str],
) -> NativeProgramResult:

    working_sources = {
        str(path).replace("\\", "/"): str(source)
        for path, source in sources.items()
    }

    completed: set[str] = set()
    step_results: list[dict[str, Any]] = []

    for step in plan.steps:

        missing_dependencies = [
            dependency
            for dependency in step.depends_on
            if dependency not in completed
        ]

        if missing_dependencies:
            return NativeProgramResult(
                status="BLOCKED",
                completed_steps=list(completed),
                blocked_step=step.step_id,
                generated_sources=working_sources,
                step_results=step_results,
                errors=[
                    "STEP_DEPENDENCY_UNSATISFIED:"
                    + ",".join(missing_dependencies)
                ],
            )

        # Verification is deliberately not faked here.
        # pytest/compile execution belongs to the verification rail.
        if step.primitive == "VERIFY_TESTS":
            return NativeProgramResult(
                status="AWAITING_VERIFICATION",
                completed_steps=list(completed),
                blocked_step=step.step_id,
                generated_sources=working_sources,
                step_results=step_results,
                errors=[
                    "VERIFY_TESTS_EXECUTOR_NOT_CONNECTED"
                ],
            )

        # High-level planning primitives must first be decomposed.
        if step.primitive in {
            "MODIFY_FILE",
        }:
            return NativeProgramResult(
                status="NEEDS_DECOMPOSITION",
                completed_steps=list(completed),
                blocked_step=step.step_id,
                generated_sources=working_sources,
                step_results=step_results,
                errors=[
                    f"HIGH_LEVEL_PRIMITIVE_REQUIRES_DECOMPOSITION:{step.primitive}"
                ],
            )

        target = step.target_path.replace("\\", "/")

        if step.primitive == "CREATE_FILE":
            current_source = working_sources.get(
                target,
                "",
            )

        elif target not in working_sources:
            return NativeProgramResult(
                status="BLOCKED",
                completed_steps=list(completed),
                blocked_step=step.step_id,
                generated_sources=working_sources,
                step_results=step_results,
                errors=[
                    f"TARGET_SOURCE_MISSING:{target}"
                ],
            )

        else:
            current_source = working_sources[target]

        result = execute_native_step(
            step,
            current_source,
        )

        step_results.append(
            result.to_dict()
        )

        if result.status != "PASS":
            return NativeProgramResult(
                status="BLOCKED",
                completed_steps=list(completed),
                blocked_step=step.step_id,
                generated_sources=working_sources,
                step_results=step_results,
                errors=list(result.errors),
            )

        working_sources[target] = result.generated_source

        completed.add(step.step_id)

    return NativeProgramResult(
        status="PASS",
        completed_steps=[
            step.step_id
            for step in plan.steps
        ],
        generated_sources=working_sources,
        step_results=step_results,
    )


def self_check() -> dict[str, Any]:
    return {
        "executor_id": PROGRAM_EXECUTOR_ID,
        "role": "SEQUENTIAL_NATIVE_PLAN_EXECUTION",
        "decision_authority": "KX108_ONLY",
        "repository_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
