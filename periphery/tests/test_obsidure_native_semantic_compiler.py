import ast

from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)
from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)
from periphery.agents.obsidure_native_semantic_compiler import (
    SemanticOperation,
    compile_semantic_operations,
)


TARGET = "periphery/generated_semantic_v2.py"


def test_semantic_ir_builds_python_without_raw_source_from_brody():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": (
                    "Bounded semantic calibration module."
                ),
            },
        ),

        SemanticOperation(
            kind="IMPORT_FROM",
            target_path=TARGET,
            payload={
                "module": "typing",
                "names": [
                    "Any",
                ],
            },
        ),

        SemanticOperation(
            kind="ADD_CLASS",
            target_path=TARGET,
            payload={
                "name": "SemanticResult",
            },
        ),

        SemanticOperation(
            kind="ADD_FIELD",
            target_path=TARGET,
            payload={
                "class_name": "SemanticResult",
                "name": "confidence",
                "annotation": "float",
                "default_expr": {
                    "kind": "CONSTANT",
                    "value": 0.0,
                },
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
                "name": "calibrate",
                "args": [
                    {
                        "name": "value",
                        "annotation": "Any",
                    },
                ],
                "returns": "SemanticResult",
                "return_expr": {
                    "kind": "CALL",
                    "func": "SemanticResult",
                    "args": [],
                },
            },
        ),
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "CREATE_FILE",
        "ADD_IMPORT",
        "ADD_CLASS",
        "ADD_FIELD",
        "ADD_FUNCTION",
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_semantic_ir",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective=(
            "build semantic calibration module"
        ),
        deltas=deltas,
    )

    result = execute_native_plan(
        plan,
        {},
    )

    assert result.status == "PASS"

    generated = result.generated_sources[
        TARGET
    ]

    assert (
        "from typing import Any"
        in generated
    )

    assert (
        "class SemanticResult"
        in generated
    )

    assert (
        "confidence: float = 0.0"
        in generated
    )

    assert (
        "def calibrate(value: Any) -> SemanticResult"
        in generated
    )

    assert (
        "return SemanticResult()"
        in generated
    )

    ast.parse(generated)


def test_semantic_function_can_return_input_name():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": "identity",
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
                "name": "identity",
                "args": [
                    {
                        "name": "value",
                        "annotation": "str",
                    },
                ],
                "returns": "str",
                "return_expr": {
                    "kind": "NAME",
                    "id": "value",
                },
            },
        ),
    ]

    deltas = compile_semantic_operations(
        operations
    )

    plan = compile_native_deltas_to_plan(
        request_id="rr_identity",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="identity",
        deltas=deltas,
    )

    result = execute_native_plan(
        plan,
        {},
    )

    assert result.status == "PASS"

    generated = result.generated_sources[
        TARGET
    ]

    assert "return value" in generated

    ast.parse(generated)
