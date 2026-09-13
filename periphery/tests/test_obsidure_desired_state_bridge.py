from pathlib import Path

from periphery.agents.obsidure_desired_state_bridge import (
    compile_desired_state_to_native_plan,
)


TARGET = "periphery/desired_bridge.py"


def spec(
    *,
    source_present: bool,
):

    return {
        "request_id": "rr_desired_bridge",
        "spec_id": "BRODY_ENGINEERING_SPEC_V1",
        "objective": "semantic calibration",
        "targets": [
            {
                "path": TARGET,
                "target_state": (
                    "EXISTING"
                    if source_present
                    else "CREATE"
                ),
                "source_present": source_present,
            }
        ],
        "acceptance_criteria": [],
        "desired_state": {
            "targets": [
                {
                    "path": TARGET,
                    "module_docstring": (
                        "Semantic calibration."
                    ),
                    "imports": [
                        {
                            "module": "typing",
                            "names": ["Any"],
                        }
                    ],
                    "classes": [
                        {
                            "name": "SemanticResult",
                            "fields": [
                                {
                                    "name": "confidence",
                                    "annotation": "float",
                                    "default_expr": {
                                        "kind": "CONSTANT",
                                        "value": 0.0,
                                    },
                                }
                            ],
                        }
                    ],
                    "functions": [
                        {
                            "name": "calibrate",
                            "args": [
                                {
                                    "name": "value",
                                    "annotation": "Any",
                                }
                            ],
                            "returns": "str",
                            "body": [
                                {
                                    "kind": "RETURN",
                                    "expr": {
                                        "kind": "CONSTANT",
                                        "value": "RESOLVED",
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        },
    }


def test_missing_target_compiles_complete_native_plan():

    result = compile_desired_state_to_native_plan(
        spec(
            source_present=False
        )
    )

    assert result.status == "NATIVE_PLAN_READY"

    primitives = [
        step["primitive"]
        for step in result.native_plan["steps"]
    ]

    assert primitives == [
        "CREATE_FILE",
        "ADD_IMPORT",
        "ADD_CLASS",
        "ADD_FIELD",
        "ADD_FUNCTION",
    ]


def test_existing_target_generates_only_missing_delta(
    tmp_path: Path,
):

    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        (
            "from typing import Any\n\n"
            "class SemanticResult:\n"
            "    pass\n\n"
            "def calibrate(value: Any) -> str:\n"
            "    return 'RESOLVED'\n"
        ),
        encoding="utf-8",
    )

    result = compile_desired_state_to_native_plan(
        spec(
            source_present=True
        ),
        repo_root=tmp_path,
    )

    assert result.status == "NATIVE_PLAN_READY"

    primitives = [
        step["primitive"]
        for step in result.native_plan["steps"]
    ]

    assert primitives == [
        "ADD_FIELD",
    ]


def test_existing_target_with_desired_state_is_noop(
    tmp_path: Path,
):

    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        (
            "from typing import Any\n\n"
            "class SemanticResult:\n"
            "    confidence: float = 0.0\n\n"
            "def calibrate(value: Any) -> str:\n"
            "    return 'RESOLVED'\n"
        ),
        encoding="utf-8",
    )

    result = compile_desired_state_to_native_plan(
        spec(
            source_present=True
        ),
        repo_root=tmp_path,
    )

    assert (
        result.status
        == "NO_CHANGE_REQUIRED"
    )

    assert result.semantic_operations == []
    assert result.native_plan is None


def test_existing_source_requires_repo_root():

    result = compile_desired_state_to_native_plan(
        spec(
            source_present=True
        )
    )

    assert (
        result.status
        == "CURRENT_STATE_UNAVAILABLE"
    )

    assert result.missing_information == [
        f"REPO_ROOT_REQUIRED:{TARGET}"
    ]


def test_desired_state_cannot_expand_target_scope():

    data = spec(
        source_present=False
    )

    data["desired_state"]["targets"][0][
        "path"
    ] = "outside/not_authorized.py"

    result = compile_desired_state_to_native_plan(
        data
    )

    assert (
        result.status
        == "INVALID_DESIRED_STATE"
    )

    assert any(
        "DESIRED_TARGET_OUTSIDE_ENGINEERING_SCOPE"
        in item
        for item
        in result.missing_information
    )
