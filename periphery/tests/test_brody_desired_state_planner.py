import ast

from apps.obsidia_api.brody_code_state import (
    analyze_python_code_state,
)

from apps.obsidia_api.brody_desired_state_planner import (
    DesiredTargetState,
    plan_desired_state,
)

from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)

from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)

from periphery.agents.obsidure_native_semantic_compiler import (
    compile_semantic_operations,
)


TARGET = "periphery/generated_desired.py"


def test_missing_module_is_built_from_desired_state():

    current = analyze_python_code_state(
        TARGET,
        None,
    )

    desired = DesiredTargetState(
        path=TARGET,
        module_docstring=(
            "Bounded semantic calibration."
        ),
        imports=[
            {
                "module": "typing",
                "names": ["Any"],
            }
        ],
        classes=[
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
        functions=[
            {
                "name": "calibrate",
                "args": [
                    {
                        "name": "value",
                        "annotation": "Any",
                    },
                    {
                        "name": "known",
                        "annotation": "bool",
                    },
                ],
                "returns": "str",
                "body": [
                    {
                        "kind": "IF",
                        "test": {
                            "kind": "NAME",
                            "id": "known",
                        },
                        "body": [
                            {
                                "kind": "RETURN",
                                "expr": {
                                    "kind": "CONSTANT",
                                    "value": "RESOLVED",
                                },
                            }
                        ],
                    },
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "CONSTANT",
                            "value": "UNKNOWN",
                        },
                    },
                ],
            }
        ],
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert [
        op.kind
        for op in operations
    ] == [
        "CREATE_MODULE",
        "IMPORT_FROM",
        "ADD_CLASS",
        "ADD_FIELD",
        "ADD_FUNCTION",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    plan = compile_native_deltas_to_plan(
        request_id="rr_desired",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="desired-state build",
        deltas=deltas,
    )

    result = execute_native_plan(
        plan,
        {},
    )

    assert result.status == "PASS"

    source = result.generated_sources[
        TARGET
    ]

    assert "from typing import Any" in source
    assert "class SemanticResult" in source
    assert "confidence: float = 0.0" in source
    assert "def calibrate" in source
    assert "if known:" in source

    ast.parse(source)


def test_existing_state_avoids_duplicate_operations():

    source = (
        "from typing import Any\n\n"
        "class SemanticResult:\n"
        "    confidence: float = 0.0\n\n"
        "def calibrate(value: Any) -> str:\n"
        "    return 'RESOLVED'\n"
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    desired = DesiredTargetState(
        path=TARGET,
        imports=[
            {
                "module": "typing",
                "names": ["Any"],
            }
        ],
        classes=[
            {
                "name": "SemanticResult",
                "fields": [
                    {
                        "name": "confidence",
                        "annotation": "float",
                    }
                ],
            }
        ],
        functions=[
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
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert operations == []


def test_partial_existing_state_only_generates_delta():

    source = (
        "class SemanticResult:\n"
        "    pass\n"
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    desired = DesiredTargetState(
        path=TARGET,
        classes=[
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
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert len(operations) == 1
    assert operations[0].kind == "ADD_FIELD"
    assert (
        operations[0].payload["name"]
        == "confidence"
    )
