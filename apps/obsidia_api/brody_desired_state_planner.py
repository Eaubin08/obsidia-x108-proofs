"""
Brody Desired State Planner V1.

CurrentCodeState + DesiredCodeState -> SemanticOperation[].

Brody reasons about desired structures.
Obsidure remains responsible for Python generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps.obsidia_api.brody_code_state import (
    PythonCodeState,
)

from periphery.agents.obsidure_native_semantic_compiler import (
    NativeSemanticCompileError,
    SemanticOperation,
    field_payload_fingerprint,
    function_payload_fingerprint,
)


PLANNER_ID = "BRODY_DESIRED_STATE_PLANNER_V1"


class DesiredStatePlanningError(RuntimeError):
    pass


@dataclass
class DesiredTargetState:
    path: str
    module_docstring: str = ""
    imports: list[dict[str, Any]] = field(default_factory=list)
    classes: list[dict[str, Any]] = field(default_factory=list)
    functions: list[dict[str, Any]] = field(default_factory=list)


def plan_desired_state(
    current: PythonCodeState,
    desired: DesiredTargetState,
) -> list[SemanticOperation]:

    target = desired.path.replace("\\", "/")

    if target != current.path:
        raise DesiredStatePlanningError(
            "CURRENT_DESIRED_PATH_MISMATCH"
        )

    if not current.parse_ok:
        raise DesiredStatePlanningError(
            "CURRENT_SOURCE_NOT_PARSEABLE"
        )

    operations: list[SemanticOperation] = []

    # Missing module.
    if not current.source_present:
        operations.append(
            SemanticOperation(
                kind="CREATE_MODULE",
                target_path=target,
                payload={
                    "docstring": (
                        desired.module_docstring
                        or "Generated bounded module."
                    )
                },
                rationale=(
                    "Desired target does not exist."
                ),
            )
        )

    # Imports.
    current_imports = set(
        current.imports
    )

    for item in desired.imports:

        if not isinstance(item, dict):
            raise DesiredStatePlanningError(
                "DESIRED_IMPORT_NOT_OBJECT"
            )

        module = str(
            item.get("module", "")
            or ""
        ).strip()

        names = item.get("names") or []

        if not module or not isinstance(
            names,
            list,
        ) or not names:
            raise DesiredStatePlanningError(
                "DESIRED_IMPORT_INVALID"
            )

        statement = (
            f"from {module} import "
            + ", ".join(
                str(name)
                for name in names
            )
        )

        if statement not in current_imports:
            operations.append(
                SemanticOperation(
                    kind="IMPORT_FROM",
                    target_path=target,
                    payload={
                        "module": module,
                        "names": list(names),
                    },
                    rationale=(
                        "Desired import missing."
                    ),
                )
            )

    # Classes + fields.
    for cls in desired.classes:

        if not isinstance(cls, dict):
            raise DesiredStatePlanningError(
                "DESIRED_CLASS_NOT_OBJECT"
            )

        name = str(
            cls.get("name", "")
            or ""
        ).strip()

        if not name:
            raise DesiredStatePlanningError(
                "DESIRED_CLASS_NAME_REQUIRED"
            )

        current_class = (
            current.classes.get(name)
        )

        if current_class is None:

            operations.append(
                SemanticOperation(
                    kind="ADD_CLASS",
                    target_path=target,
                    payload={
                        "name": name,
                        "bases": list(
                            cls.get("bases")
                            or []
                        ),
                    },
                    rationale=(
                        f"Desired class missing: {name}"
                    ),
                )
            )

            existing_fields: set[str] = set()
            current_field_states = {}

            existing_methods: set[str] = set()
            current_method_states = {}

        else:
            existing_fields = set(
                current_class.fields
            )
            current_field_states = dict(
                current_class.field_states
            )

            existing_methods = set(
                current_class.methods
            )
            current_method_states = dict(
                current_class.method_states
            )

        for field_spec in (
            cls.get("fields")
            or []
        ):

            if not isinstance(
                field_spec,
                dict,
            ):
                raise DesiredStatePlanningError(
                    "DESIRED_FIELD_NOT_OBJECT"
                )

            field_name = str(
                field_spec.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not field_name:
                raise DesiredStatePlanningError(
                    "DESIRED_FIELD_NAME_REQUIRED"
                )

            payload = dict(
                field_spec
            )

            payload["class_name"] = name

            if field_name not in existing_fields:
                operations.append(
                    SemanticOperation(
                        kind="ADD_FIELD",
                        target_path=target,
                        payload=payload,
                        rationale=(
                            f"Desired field missing: "
                            f"{name}.{field_name}"
                        ),
                    )
                )
                continue

            current_field = (
                current_field_states.get(
                    field_name
                )
            )

            if current_field is None:
                raise DesiredStatePlanningError(
                    "CURRENT_FIELD_STATE_MISSING:"
                    f"{name}.{field_name}"
                )

            # Desired field specifications are constraints,
            # not necessarily complete replacement objects.
            #
            # If no default_expr is specified, an existing
            # compatible default must be preserved rather
            # than interpreted as an unwanted difference.
            desired_annotation = str(
                field_spec.get(
                    "annotation",
                    "",
                )
                or ""
            ).strip()

            if (
                "default_expr" not in field_spec
                and current_field.annotation
                == desired_annotation
            ):
                continue

            try:
                desired_fingerprint = (
                    field_payload_fingerprint(
                        payload
                    )
                )

            except NativeSemanticCompileError as exc:
                raise DesiredStatePlanningError(
                    "DESIRED_FIELD_NOT_COMPILABLE:"
                    f"{name}.{field_name}:{exc}"
                ) from exc

            if (
                current_field.structural_fingerprint
                == desired_fingerprint
            ):
                continue

            if not current_field.rewrite_safe:
                raise DesiredStatePlanningError(
                    "CURRENT_FIELD_REWRITE_UNSAFE:"
                    f"{name}.{field_name}"
                )

            operations.append(
                SemanticOperation(
                    kind="MODIFY_FIELD",
                    target_path=target,
                    payload=payload,
                    rationale=(
                        "Desired field differs "
                        f"structurally: "
                        f"{name}.{field_name}"
                    ),
                )
            )


        # Class methods.
        for method_spec in (
            cls.get("methods")
            or []
        ):

            if not isinstance(
                method_spec,
                dict,
            ):
                raise DesiredStatePlanningError(
                    "DESIRED_METHOD_NOT_OBJECT"
                )

            method_name = str(
                method_spec.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not method_name:
                raise DesiredStatePlanningError(
                    "DESIRED_METHOD_NAME_REQUIRED"
                )

            payload = dict(
                method_spec
            )

            payload["class_name"] = name

            if method_name not in existing_methods:
                operations.append(
                    SemanticOperation(
                        kind="ADD_METHOD",
                        target_path=target,
                        payload=payload,
                        rationale=(
                            "Desired method missing: "
                            f"{name}.{method_name}"
                        ),
                    )
                )
                continue

            current_method = (
                current_method_states.get(
                    method_name
                )
            )

            if current_method is None:
                raise DesiredStatePlanningError(
                    "CURRENT_METHOD_STATE_MISSING:"
                    f"{name}.{method_name}"
                )

            try:
                desired_fingerprint = (
                    function_payload_fingerprint(
                        payload
                    )
                )

            except NativeSemanticCompileError as exc:
                raise DesiredStatePlanningError(
                    "DESIRED_METHOD_NOT_COMPILABLE:"
                    f"{name}.{method_name}:{exc}"
                ) from exc

            if (
                current_method.structural_fingerprint
                == desired_fingerprint
            ):
                continue

            if not current_method.rewrite_safe:
                raise DesiredStatePlanningError(
                    "CURRENT_METHOD_REWRITE_UNSAFE:"
                    f"{name}.{method_name}"
                )

            operations.append(
                SemanticOperation(
                    kind="MODIFY_METHOD",
                    target_path=target,
                    payload=payload,
                    rationale=(
                        "Desired method differs "
                        "structurally: "
                        f"{name}.{method_name}"
                    ),
                )
            )

    # Functions.
    for fn in desired.functions:

        if not isinstance(fn, dict):
            raise DesiredStatePlanningError(
                "DESIRED_FUNCTION_NOT_OBJECT"
            )

        name = str(
            fn.get("name", "")
            or ""
        ).strip()

        if not name:
            raise DesiredStatePlanningError(
                "DESIRED_FUNCTION_NAME_REQUIRED"
            )

        current_function = (
            current.functions.get(name)
        )

        if current_function is None:

            operations.append(
                SemanticOperation(
                    kind="ADD_FUNCTION",
                    target_path=target,
                    payload=dict(fn),
                    rationale=(
                        f"Desired function missing: {name}"
                    ),
                )
            )

            continue

        try:
            desired_fingerprint = (
                function_payload_fingerprint(
                    dict(fn)
                )
            )

        except NativeSemanticCompileError as exc:
            raise DesiredStatePlanningError(
                "DESIRED_FUNCTION_NOT_COMPILABLE:"
                f"{name}:{exc}"
            ) from exc

        if (
            current_function.structural_fingerprint
            == desired_fingerprint
        ):
            continue

        # Never rewrite a function whose current
        # structure cannot be round-tripped through
        # the bounded semantic compiler.
        if not current_function.rewrite_safe:
            raise DesiredStatePlanningError(
                "CURRENT_FUNCTION_REWRITE_UNSAFE:"
                f"{name}"
            )

        operations.append(
            SemanticOperation(
                kind="MODIFY_FUNCTION",
                target_path=target,
                payload=dict(fn),
                rationale=(
                    "Desired function differs "
                    f"structurally: {name}"
                ),
            )
        )

    return operations


def self_check() -> dict[str, Any]:
    return {
        "planner_id": PLANNER_ID,
        "role": (
            "CURRENT_STATE_TO_DESIRED_STATE_DIFF"
        ),
        "raw_python_generation": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
    }
