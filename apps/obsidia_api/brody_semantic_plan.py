"""
Brody Semantic Engineering Plan V1.

Transforms an explicit structured semantic plan into a validated contract
that Obsidure can compile.

Brody specifies semantics, never Python source.

Transitional input:
    SEMANTIC_PLAN_JSON={...}

This marker will later be produced by Brody cognition directly rather than
being supplied manually.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any


SEMANTIC_PLAN_ID = "BRODY_SEMANTIC_PLAN_V1"

_ALLOWED_OPERATIONS = {
    "CREATE_MODULE",
    "IMPORT_FROM",
    "ADD_CLASS",
    "ADD_FIELD",
    "ADD_FUNCTION",
    "MODIFY_FUNCTION",
}

_FORBIDDEN_KEYS = {
    "source",
    "full_content",
    "patch",
    "diff",
    "unified_diff",
}


@dataclass
class BrodySemanticPlan:
    status: str
    request_id: str = ""
    spec_id: str = ""
    operations: list[dict[str, Any]] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    plan_id: str = SEMANTIC_PLAN_ID

    can_generate_source: bool = False
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _contains_forbidden_source(
    value: Any,
    path: str = "",
) -> list[str]:

    violations: list[str] = []

    if isinstance(value, dict):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
                if path
                else str(key)
            )

            if str(key).lower() in _FORBIDDEN_KEYS:
                violations.append(
                    f"RAW_SOURCE_FIELD_FORBIDDEN:{child_path}"
                )

            violations.extend(
                _contains_forbidden_source(
                    child,
                    child_path,
                )
            )

    elif isinstance(value, list):

        for index, child in enumerate(value):
            violations.extend(
                _contains_forbidden_source(
                    child,
                    f"{path}[{index}]",
                )
            )

    return violations


def _extract_explicit_plan(
    objective: str,
) -> dict[str, Any] | None:

    marker = "SEMANTIC_PLAN_JSON="

    index = objective.rfind(marker)

    if index < 0:
        return None

    raw = objective[
        index + len(marker):
    ].strip()

    if not raw:
        raise ValueError(
            "SEMANTIC_PLAN_JSON_EMPTY"
        )

    try:
        data = json.loads(raw)

    except Exception as exc:
        raise ValueError(
            "SEMANTIC_PLAN_JSON_INVALID"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "SEMANTIC_PLAN_NOT_OBJECT"
        )

    return data


def build_brody_semantic_plan(
    engineering_spec: dict[str, Any],
) -> BrodySemanticPlan:

    if not isinstance(
        engineering_spec,
        dict,
    ):
        raise ValueError(
            "ENGINEERING_SPEC_NOT_OBJECT"
        )

    request_id = str(
        engineering_spec.get(
            "request_id",
            "",
        )
        or ""
    )

    spec_id = str(
        engineering_spec.get(
            "spec_id",
            "",
        )
        or ""
    )

    objective = str(
        engineering_spec.get(
            "objective",
            "",
        )
        or ""
    )

    explicit = engineering_spec.get(
        "semantic_plan"
    )

    if explicit is None:
        explicit = _extract_explicit_plan(
            objective
        )

    if explicit is None:
        return BrodySemanticPlan(
            status="NEEDS_SEMANTIC_DECOMPOSITION",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "SEMANTIC_PLAN_NOT_YET_PRODUCED_BY_BRODY"
            ],
        )

    if not isinstance(explicit, dict):
        return BrodySemanticPlan(
            status="INVALID_SEMANTIC_PLAN",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "SEMANTIC_PLAN_NOT_OBJECT"
            ],
        )

    violations = _contains_forbidden_source(
        explicit
    )

    if violations:
        return BrodySemanticPlan(
            status="INVALID_SEMANTIC_PLAN",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=violations,
        )

    operations = explicit.get(
        "operations"
    )

    if not isinstance(
        operations,
        list,
    ) or not operations:

        return BrodySemanticPlan(
            status="INVALID_SEMANTIC_PLAN",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "SEMANTIC_OPERATIONS_REQUIRED"
            ],
        )

    normalized: list[
        dict[str, Any]
    ] = []

    errors: list[str] = []

    for index, operation in enumerate(
        operations
    ):

        if not isinstance(
            operation,
            dict,
        ):
            errors.append(
                f"SEMANTIC_OPERATION_NOT_OBJECT:{index}"
            )
            continue

        kind = str(
            operation.get(
                "kind",
                "",
            )
            or ""
        ).upper()

        target_path = str(
            operation.get(
                "target_path",
                "",
            )
            or ""
        ).replace("\\", "/").strip()

        payload = operation.get(
            "payload"
        )

        if kind not in _ALLOWED_OPERATIONS:
            errors.append(
                f"SEMANTIC_OPERATION_UNSUPPORTED:{index}:{kind}"
            )
            continue

        if not target_path:
            errors.append(
                f"SEMANTIC_TARGET_REQUIRED:{index}"
            )
            continue

        if payload is None:
            payload = {}

        if not isinstance(
            payload,
            dict,
        ):
            errors.append(
                f"SEMANTIC_PAYLOAD_NOT_OBJECT:{index}"
            )
            continue

        normalized.append({
            "kind": kind,
            "target_path": target_path,
            "payload": payload,
            "rationale": str(
                operation.get(
                    "rationale",
                    "",
                )
                or ""
            ),
            "operation_id": str(
                operation.get(
                    "operation_id",
                    "",
                )
                or ""
            ),
        })

    if errors:

        return BrodySemanticPlan(
            status="INVALID_SEMANTIC_PLAN",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=errors,
        )

    return BrodySemanticPlan(
        status="SEMANTIC_PLAN_READY",
        request_id=request_id,
        spec_id=spec_id,
        operations=normalized,
    )


def self_check() -> dict[str, Any]:

    return {
        "plan_id": SEMANTIC_PLAN_ID,
        "allowed_operations": sorted(
            _ALLOWED_OPERATIONS
        ),
        "raw_source_forbidden": True,
        "can_generate_source": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
    }
