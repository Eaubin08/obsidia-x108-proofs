"""
Obsidure Native Plan V1.

Compiles a BrodyEngineeringSpec into a bounded, explicit engineering plan.

This layer describes WHAT native operations must occur.
It does not synthesize arbitrary source and does not mutate the repository.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from typing import Any


PLAN_ID = "OBSIDURE_NATIVE_PLAN_V1"


# Vocabulary deliberately broader than the current solve engine.
# Having a primitive in this registry does NOT mean its executor exists yet.
PRIMITIVES: dict[str, dict[str, Any]] = {
    "READ_SOURCE": {
        "kind": "READ",
        "execution_ready": True,
    },
    "CREATE_FILE": {
        "kind": "STRUCTURAL_WRITE",
        "execution_ready": True,
    },
    "MODIFY_FILE": {
        "kind": "STRUCTURAL_WRITE",
        "execution_ready": False,
    },
    "ADD_IMPORT": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "REMOVE_IMPORT": {
        "kind": "AST_EDIT",
        "execution_ready": False,
    },
    "ADD_FUNCTION": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_FUNCTION": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "ADD_METHOD": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_METHOD": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "ADD_CLASS": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_CLASS": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "ADD_FIELD": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_FIELD": {
        "kind": "AST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_SIGNATURE": {
        "kind": "AST_EDIT",
        "execution_ready": False,
    },
    "ADD_CALL": {
        "kind": "AST_EDIT",
        "execution_ready": False,
    },
    "ADD_BRANCH": {
        "kind": "AST_EDIT",
        "execution_ready": False,
    },
    "ADD_TEST": {
        "kind": "TEST_EDIT",
        "execution_ready": True,
    },
    "MODIFY_TEST": {
        "kind": "TEST_EDIT",
        "execution_ready": False,
    },
    "WIRE_COMPONENT": {
        "kind": "INTEGRATION_EDIT",
        "execution_ready": False,
    },
    "VERIFY_TESTS": {
        "kind": "VERIFICATION",
        "execution_ready": True,
    },
}


@dataclass(frozen=True)
class NativePlanStep:
    step_id: str
    primitive: str
    target_path: str
    rationale: str
    parameters: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    execution_ready: bool = False


@dataclass
class NativePlan:
    request_id: str
    spec_id: str
    objective: str
    steps: list[NativePlanStep] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)
    plan_id: str = PLAN_ID

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _step_id(
    primitive: str,
    target: str,
    index: int,
) -> str:
    raw = f"{index}:{primitive}:{target}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    return f"nps_{digest}"


def compile_engineering_spec_to_native_plan(
    spec: dict[str, Any],
) -> NativePlan:
    if not isinstance(spec, dict):
        raise ValueError("ENGINEERING_SPEC_NOT_OBJECT")

    request_id = str(spec.get("request_id", "") or "")
    spec_id = str(spec.get("spec_id", "") or "")
    objective = str(spec.get("objective", "") or "")

    raw_targets = spec.get("targets") or []
    acceptance = [
        str(v)
        for v in (spec.get("acceptance_criteria") or [])
        if str(v).strip()
    ]

    steps: list[NativePlanStep] = []
    missing: list[str] = []

    previous_step: str | None = None

    for index, raw_target in enumerate(raw_targets, start=1):
        if not isinstance(raw_target, dict):
            missing.append("INVALID_TARGET_DESCRIPTOR")
            continue

        path = str(raw_target.get("path", "") or "").replace("\\", "/")
        state = str(raw_target.get("target_state", "") or "").upper()

        if not path:
            missing.append("TARGET_PATH_MISSING")
            continue

        if state == "CREATE":
            primitive = "CREATE_FILE"
            rationale = "Engineering target does not exist and must be created."
            missing.append(f"FILE_CONTENT_SYNTHESIS_MISSING:{path}")

        elif state == "EXISTING":
            primitive = "MODIFY_FILE"
            rationale = "Existing engineering target requires a bounded modification."
            missing.append(f"SEMANTIC_EDIT_DECOMPOSITION_MISSING:{path}")

        else:
            missing.append(f"TARGET_STATE_UNSUPPORTED:{path}:{state}")
            continue

        meta = PRIMITIVES[primitive]
        sid = _step_id(primitive, path, index)

        steps.append(
            NativePlanStep(
                step_id=sid,
                primitive=primitive,
                target_path=path,
                rationale=rationale,
                depends_on=(previous_step,) if previous_step else (),
                execution_ready=bool(meta["execution_ready"]),
            )
        )

        previous_step = sid

    if acceptance:
        sid = _step_id("VERIFY_TESTS", "<acceptance>", len(steps) + 1)

        steps.append(
            NativePlanStep(
                step_id=sid,
                primitive="VERIFY_TESTS",
                target_path="<acceptance>",
                rationale="Verify declared acceptance criteria after candidate generation.",
                depends_on=(previous_step,) if previous_step else (),
                execution_ready=True,
            )
        )

    if not steps:
        missing.append("NO_NATIVE_PLAN_STEPS")

    return NativePlan(
        request_id=request_id,
        spec_id=spec_id,
        objective=objective,
        steps=steps,
        acceptance_criteria=acceptance,
        missing_capabilities=sorted(set(missing)),
    )


def self_check() -> dict[str, Any]:
    return {
        "plan_id": PLAN_ID,
        "primitive_count": len(PRIMITIVES),
        "primitives": sorted(PRIMITIVES),
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
    }
