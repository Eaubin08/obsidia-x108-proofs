"""
Obsidure Desired State Bridge V1.

EngineeringSpec
    -> BrodyDesiredState
    -> read-only current source observation
    -> semantic delta
    -> NativePlan

No repository mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from apps.obsidia_api.brody_code_state import (
    analyze_python_code_state,
)

from apps.obsidia_api.brody_desired_state_contract import (
    build_brody_desired_state,
)

from apps.obsidia_api.brody_desired_state_planner import (
    DesiredTargetState,
    plan_desired_state,
)

from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)

from periphery.agents.obsidure_native_semantic_compiler import (
    compile_semantic_operations,
)


BRIDGE_ID = "OBSIDURE_DESIRED_STATE_BRIDGE_V1"


@dataclass
class DesiredStateBridgeResult:
    status: str
    request_id: str = ""
    spec_id: str = ""

    semantic_operations: list[
        dict[str, Any]
    ] = field(default_factory=list)

    native_plan: dict[
        str,
        Any,
    ] | None = None

    missing_information: list[
        str
    ] = field(default_factory=list)

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    repository_write: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _target_descriptor(
    spec: dict[str, Any],
    path: str,
) -> dict[str, Any] | None:

    for target in (
        spec.get("targets")
        or []
    ):

        if not isinstance(
            target,
            dict,
        ):
            continue

        candidate = str(
            target.get(
                "path",
                "",
            )
            or ""
        ).replace("\\", "/")

        if candidate == path:
            return target

    return None


def compile_desired_state_to_native_plan(
    engineering_spec: dict[str, Any],
    *,
    repo_root: Path | str | None = None,
) -> DesiredStateBridgeResult:

    desired_bundle = (
        build_brody_desired_state(
            engineering_spec
        )
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

    if (
        desired_bundle.status
        != "DESIRED_STATE_READY"
    ):

        return DesiredStateBridgeResult(
            status=desired_bundle.status,
            request_id=request_id,
            spec_id=spec_id,
            missing_information=list(
                desired_bundle.missing_information
            ),
        )

    root = (
        Path(repo_root)
        if repo_root is not None
        else None
    )

    operations = []

    for desired_target in (
        desired_bundle.targets
    ):

        path = str(
            desired_target["path"]
        ).replace("\\", "/")

        descriptor = _target_descriptor(
            engineering_spec,
            path,
        )

        if descriptor is None:

            return DesiredStateBridgeResult(
                status="INVALID_DESIRED_STATE",
                request_id=request_id,
                spec_id=spec_id,
                missing_information=[
                    f"ENGINEERING_TARGET_NOT_FOUND:{path}"
                ],
            )

        source_present = bool(
            descriptor.get(
                "source_present",
                False,
            )
        )

        source: str | None = None

        if source_present:

            if root is None:

                return DesiredStateBridgeResult(
                    status="CURRENT_STATE_UNAVAILABLE",
                    request_id=request_id,
                    spec_id=spec_id,
                    missing_information=[
                        f"REPO_ROOT_REQUIRED:{path}"
                    ],
                )

            absolute = (
                root
                / Path(path)
            )

            if not absolute.is_file():

                return DesiredStateBridgeResult(
                    status="CURRENT_STATE_UNAVAILABLE",
                    request_id=request_id,
                    spec_id=spec_id,
                    missing_information=[
                        f"CURRENT_SOURCE_MISSING:{path}"
                    ],
                )

            try:
                source = absolute.read_text(
                    encoding="utf-8"
                )

            except Exception as exc:

                return DesiredStateBridgeResult(
                    status="CURRENT_STATE_UNAVAILABLE",
                    request_id=request_id,
                    spec_id=spec_id,
                    missing_information=[
                        (
                            f"CURRENT_SOURCE_READ_FAILED:"
                            f"{path}:"
                            f"{type(exc).__name__}"
                        )
                    ],
                )

        current = analyze_python_code_state(
            path,
            source,
        )

        if not current.parse_ok:

            return DesiredStateBridgeResult(
                status="CURRENT_STATE_INVALID",
                request_id=request_id,
                spec_id=spec_id,
                missing_information=[
                    (
                        f"CURRENT_SOURCE_SYNTAX_ERROR:"
                        f"{path}:"
                        f"{current.syntax_error}"
                    )
                ],
            )

        desired = DesiredTargetState(
            path=path,
            module_docstring=str(
                desired_target.get(
                    "module_docstring",
                    "",
                )
                or ""
            ),
            imports=list(
                desired_target.get(
                    "imports",
                    [],
                )
                or []
            ),
            classes=list(
                desired_target.get(
                    "classes",
                    [],
                )
                or []
            ),
            functions=list(
                desired_target.get(
                    "functions",
                    [],
                )
                or []
            ),
        )

        operations.extend(
            plan_desired_state(
                current,
                desired,
            )
        )

    if not operations:

        return DesiredStateBridgeResult(
            status="NO_CHANGE_REQUIRED",
            request_id=request_id,
            spec_id=spec_id,
        )

    try:

        deltas = (
            compile_semantic_operations(
                operations
            )
        )

        native_plan = (
            compile_native_deltas_to_plan(
                request_id=request_id,
                spec_id=spec_id,
                objective=str(
                    engineering_spec.get(
                        "objective",
                        "",
                    )
                    or ""
                ),
                deltas=deltas,
                acceptance_criteria=list(
                    engineering_spec.get(
                        "acceptance_criteria",
                        [],
                    )
                    or []
                ),
            )
        )

    except Exception as exc:

        return DesiredStateBridgeResult(
            status="NATIVE_PLAN_COMPILATION_BLOCKED",
            request_id=request_id,
            spec_id=spec_id,
            semantic_operations=[
                asdict(operation)
                for operation
                in operations
            ],
            missing_information=[
                (
                    f"NATIVE_PLAN_COMPILATION_ERROR:"
                    f"{type(exc).__name__}:"
                    f"{exc}"
                )
            ],
        )

    return DesiredStateBridgeResult(
        status="NATIVE_PLAN_READY",
        request_id=request_id,
        spec_id=spec_id,
        semantic_operations=[
            asdict(operation)
            for operation
            in operations
        ],
        native_plan=native_plan.to_dict(),
    )


def self_check() -> dict[str, Any]:

    return {
        "bridge_id": BRIDGE_ID,
        "role": "DESIRED_STATE_TO_NATIVE_PLAN",
        "repository_write": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "external_engine_called": False,
    }
