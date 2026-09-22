"""
Obsidure Native Engineering Consumer V3.

BRODY_ENGINEERING_SPEC
    -> BrodySemanticPlan when available
    -> SemanticOperation[]
    -> NativeDelta[]
    -> NativePlan

No external engine.
No repository mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath
from typing import Any, Optional

from apps.obsidia_api.brody_semantic_plan import (
    build_brody_semantic_plan,
)

from periphery.agents.obsidure_desired_state_bridge import (
    compile_desired_state_to_native_plan,
)

from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)

from periphery.agents.obsidure_native_plan import (
    compile_engineering_spec_to_native_plan,
)

from periphery.agents.obsidure_native_semantic_compiler import (
    SemanticOperation,
    compile_semantic_operations,
)

from periphery.agents.obsidure_repair_contract import (
    RepairProposal,
)


CONSUMER_ID = (
    "OBSIDURE_NATIVE_ENGINEERING_CONSUMER_V4"
)


@dataclass
class NativeEngineeringResult:
    status: str
    request_id: str = ""
    spec_id: str = ""

    inspected_targets: list[str] = field(
        default_factory=list
    )

    missing_capabilities: list[str] = field(
        default_factory=list
    )

    desired_state: Optional[
        dict[str, Any]
    ] = None

    semantic_plan: Optional[
        dict[str, Any]
    ] = None

    native_plan: Optional[
        dict[str, Any]
    ] = None

    proposal: Optional[
        RepairProposal
    ] = None

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_engineering_spec(
    diagnosis: Any,
) -> Optional[dict[str, Any]]:

    for finding in list(
        getattr(
            diagnosis,
            "findings",
            [],
        )
        or []
    ):

        if not isinstance(
            finding,
            dict,
        ):
            continue

        if (
            finding.get("type")
            != "BRODY_ENGINEERING_SPEC"
        ):
            continue

        spec = finding.get("spec")

        if isinstance(
            spec,
            dict,
        ):
            return spec

    return None


def _targets(
    spec: dict[str, Any],
) -> list[str]:

    result: list[str] = []

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
            target.get("path", "")
            or ""
        ).replace("\\", "/")

        if path:
            result.append(path)

    return result


def _semantic_operations(
    plan: dict[str, Any],
) -> list[SemanticOperation]:

    result: list[
        SemanticOperation
    ] = []

    for item in (
        plan.get("operations")
        or []
    ):

        result.append(
            SemanticOperation(
                kind=str(
                    item.get(
                        "kind",
                        "",
                    )
                    or ""
                ),
                target_path=str(
                    item.get(
                        "target_path",
                        "",
                    )
                    or ""
                ),
                payload=dict(
                    item.get(
                        "payload",
                        {},
                    )
                    or {}
                ),
                rationale=str(
                    item.get(
                        "rationale",
                        "",
                    )
                    or ""
                ),
                operation_id=str(
                    item.get(
                        "operation_id",
                        "",
                    )
                    or ""
                ),
            )
        )

    return result


def consume_brody_engineering_spec(
    diagnosis: Any,
    repo_root: Any = None,
) -> NativeEngineeringResult:

    spec = _extract_engineering_spec(
        diagnosis
    )

    request_id = str(
        getattr(
            diagnosis,
            "request_id",
            "",
        )
        or ""
    )

    if not spec:

        return NativeEngineeringResult(
            status="INVALID_ENGINEERING_SPEC",
            request_id=request_id,
            missing_capabilities=[
                "BRODY_ENGINEERING_SPEC_MISSING"
            ],
        )

    inspected = _targets(
        spec
    )

    language_gaps = [
        f"TARGET_LANGUAGE_UNSUPPORTED:{path}"
        for path in inspected
        if PurePosixPath(
            path
        ).suffix.lower() != ".py"
    ]

    # Desired-state route: observe reality, compute minimal semantic delta.
    desired = compile_desired_state_to_native_plan(
        spec,
        repo_root=repo_root,
    )

    if desired.status == "NATIVE_PLAN_READY":

        desired_gaps = sorted(
            set(language_gaps)
        )

        return NativeEngineeringResult(
            status=(
                "NATIVE_PLAN_READY"
                if not desired_gaps
                else
                "NATIVE_PLAN_READY_CAPABILITIES_MISSING"
            ),
            request_id=request_id,
            spec_id=str(
                spec.get("spec_id", "")
                or ""
            ),
            inspected_targets=inspected,
            missing_capabilities=desired_gaps,
            desired_state=desired.to_dict(),
            native_plan=desired.native_plan,
        )

    if desired.status == "NO_CHANGE_REQUIRED":

        return NativeEngineeringResult(
            status="NO_CHANGE_REQUIRED",
            request_id=request_id,
            spec_id=str(
                spec.get("spec_id", "")
                or ""
            ),
            inspected_targets=inspected,
            desired_state=desired.to_dict(),
        )

    if desired.status != "NEEDS_DESIRED_STATE":

        desired_gaps = list(
            desired.missing_information
        )
        desired_gaps.extend(
            language_gaps
        )

        return NativeEngineeringResult(
            status=desired.status,
            request_id=request_id,
            spec_id=str(
                spec.get("spec_id", "")
                or ""
            ),
            inspected_targets=inspected,
            missing_capabilities=sorted(
                set(desired_gaps)
            ),
            desired_state=desired.to_dict(),
        )

    # No desired state yet: preserve SemanticPlan/coarse fallback.
    semantic = (
        build_brody_semantic_plan(
            spec
        )
    )

    if (
        semantic.status
        == "SEMANTIC_PLAN_READY"
    ):

        try:

            operations = (
                _semantic_operations(
                    semantic.to_dict()
                )
            )

            deltas = (
                compile_semantic_operations(
                    operations
                )
            )

            plan = (
                compile_native_deltas_to_plan(
                    request_id=(
                        str(
                            spec.get(
                                "request_id",
                                "",
                            )
                            or request_id
                        )
                    ),
                    spec_id=str(
                        spec.get(
                            "spec_id",
                            "",
                        )
                        or ""
                    ),
                    objective=str(
                        spec.get(
                            "objective",
                            "",
                        )
                        or ""
                    ),
                    deltas=deltas,
                    acceptance_criteria=list(
                        spec.get(
                            "acceptance_criteria",
                            [],
                        )
                        or []
                    ),
                )
            )

        except Exception as exc:

            return NativeEngineeringResult(
                status=(
                    "SEMANTIC_PLAN_COMPILATION_BLOCKED"
                ),
                request_id=request_id,
                spec_id=str(
                    spec.get(
                        "spec_id",
                        "",
                    )
                    or ""
                ),
                inspected_targets=inspected,
                missing_capabilities=[
                    (
                        "SEMANTIC_PLAN_COMPILATION_ERROR:"
                        f"{type(exc).__name__}:"
                        f"{exc}"
                    )
                ],
                semantic_plan=semantic.to_dict(),
            )

        gaps = sorted(
            set(language_gaps)
        )

        return NativeEngineeringResult(
            status=(
                "NATIVE_PLAN_READY"
                if not gaps
                else
                "NATIVE_PLAN_READY_CAPABILITIES_MISSING"
            ),
            request_id=request_id,
            spec_id=plan.spec_id,
            inspected_targets=inspected,
            missing_capabilities=gaps,
            semantic_plan=semantic.to_dict(),
            native_plan=plan.to_dict(),
        )

    # No semantic decomposition yet:
    # preserve the coarse planning path.
    coarse = (
        compile_engineering_spec_to_native_plan(
            spec
        )
    )

    gaps = list(
        coarse.missing_capabilities
    )

    gaps.extend(
        language_gaps
    )

    gaps.extend(
        semantic.missing_information
    )

    return NativeEngineeringResult(
        status=(
            "NATIVE_PLAN_READY_CAPABILITIES_MISSING"
        ),
        request_id=request_id,
        spec_id=coarse.spec_id,
        inspected_targets=inspected,
        missing_capabilities=sorted(
            set(gaps)
        ),
        semantic_plan=semantic.to_dict(),
        native_plan=coarse.to_dict(),
    )


def self_check() -> dict[str, Any]:

    return {
        "consumer_id": CONSUMER_ID,
        "role": (
            "ENGINEERING_SPEC_TO_SEMANTIC_NATIVE_PLAN"
        ),
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
