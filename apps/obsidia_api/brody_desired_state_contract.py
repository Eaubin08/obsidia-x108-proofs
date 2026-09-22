"""
Brody Desired State Contract V1.

Defines the structured desired program state produced by Brody.

Brody expresses structures and behavior semantics.
Raw Python source, patches and diffs are forbidden.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any


CONTRACT_ID = "BRODY_DESIRED_STATE_V1"

_FORBIDDEN_KEYS = {
    "source",
    "full_content",
    "patch",
    "diff",
    "unified_diff",
}


@dataclass
class BrodyDesiredStateBundle:
    status: str
    request_id: str = ""
    spec_id: str = ""
    targets: list[dict[str, Any]] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)

    contract_id: str = CONTRACT_ID

    can_generate_source: bool = False
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _forbidden_fields(
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
                _forbidden_fields(
                    child,
                    child_path,
                )
            )

    elif isinstance(value, list):

        for index, child in enumerate(value):

            violations.extend(
                _forbidden_fields(
                    child,
                    f"{path}[{index}]",
                )
            )

    return violations


def _extract_marker(
    objective: str,
) -> dict[str, Any] | None:

    marker = "DESIRED_STATE_JSON="

    index = objective.rfind(marker)

    if index < 0:
        return None

    raw = objective[
        index + len(marker):
    ].strip()

    if not raw:
        raise ValueError(
            "DESIRED_STATE_JSON_EMPTY"
        )

    try:
        result = json.loads(raw)

    except Exception as exc:
        raise ValueError(
            "DESIRED_STATE_JSON_INVALID"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "DESIRED_STATE_NOT_OBJECT"
        )

    return result


def build_brody_desired_state(
    engineering_spec: dict[str, Any],
) -> BrodyDesiredStateBundle:

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

    desired = engineering_spec.get(
        "desired_state"
    )

    if desired is None:

        desired = _extract_marker(
            str(
                engineering_spec.get(
                    "objective",
                    "",
                )
                or ""
            )
        )

    if desired is None:

        return BrodyDesiredStateBundle(
            status="NEEDS_DESIRED_STATE",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "BRODY_DESIRED_STATE_NOT_PRODUCED"
            ],
        )

    if not isinstance(desired, dict):

        return BrodyDesiredStateBundle(
            status="INVALID_DESIRED_STATE",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "DESIRED_STATE_NOT_OBJECT"
            ],
        )

    violations = _forbidden_fields(
        desired
    )

    if violations:

        return BrodyDesiredStateBundle(
            status="INVALID_DESIRED_STATE",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=violations,
        )

    targets = desired.get(
        "targets"
    )

    if not isinstance(
        targets,
        list,
    ) or not targets:

        return BrodyDesiredStateBundle(
            status="INVALID_DESIRED_STATE",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=[
                "DESIRED_TARGETS_REQUIRED"
            ],
        )

    allowed_paths = {
        str(
            target.get(
                "path",
                "",
            )
            or ""
        ).replace("\\", "/")
        for target in (
            engineering_spec.get(
                "targets",
                [],
            )
            or []
        )
        if isinstance(target, dict)
    }

    normalized: list[
        dict[str, Any]
    ] = []

    errors: list[str] = []

    for index, target in enumerate(
        targets
    ):

        if not isinstance(
            target,
            dict,
        ):
            errors.append(
                f"DESIRED_TARGET_NOT_OBJECT:{index}"
            )
            continue

        path = str(
            target.get(
                "path",
                "",
            )
            or ""
        ).replace("\\", "/").strip()

        if not path:

            errors.append(
                f"DESIRED_TARGET_PATH_REQUIRED:{index}"
            )
            continue

        if path not in allowed_paths:

            errors.append(
                f"DESIRED_TARGET_OUTSIDE_ENGINEERING_SCOPE:{path}"
            )
            continue

        normalized.append({
            "path": path,
            "module_docstring": str(
                target.get(
                    "module_docstring",
                    "",
                )
                or ""
            ),
            "imports": list(
                target.get(
                    "imports",
                    [],
                )
                or []
            ),
            "classes": list(
                target.get(
                    "classes",
                    [],
                )
                or []
            ),
            "functions": list(
                target.get(
                    "functions",
                    [],
                )
                or []
            ),
        })

    if errors:

        return BrodyDesiredStateBundle(
            status="INVALID_DESIRED_STATE",
            request_id=request_id,
            spec_id=spec_id,
            missing_information=errors,
        )

    return BrodyDesiredStateBundle(
        status="DESIRED_STATE_READY",
        request_id=request_id,
        spec_id=spec_id,
        targets=normalized,
    )


def self_check() -> dict[str, Any]:

    return {
        "contract_id": CONTRACT_ID,
        "raw_source_forbidden": True,
        "can_generate_source": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
    }
