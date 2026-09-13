import ast

import pytest

from periphery.agents.obsidure_native_decomposer import (
    NativeDelta,
    NativeDecompositionError,
    compile_native_deltas_to_plan,
)
from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)


TARGET = "periphery/generated_semantic.py"


def test_delta_compiler_builds_executable_program():

    deltas = [
        NativeDelta(
            primitive="CREATE_FILE",
            target_path=TARGET,
            parameters={
                "source": (
                    '"""Generated peripheral module."""\n'
                    "\n"
                    "VALUE = 1\n"
                )
            },
        ),
        NativeDelta(
            primitive="ADD_IMPORT",
            target_path=TARGET,
            parameters={
                "statement": (
                    "from typing import Any"
                )
            },
        ),
        NativeDelta(
            primitive="ADD_CLASS",
            target_path=TARGET,
            parameters={
                "source": (
                    "class SemanticResult:\n"
                    "    value: Any\n"
                )
            },
        ),
        NativeDelta(
            primitive="ADD_FIELD",
            target_path=TARGET,
            parameters={
                "class_name": "SemanticResult",
                "source": (
                    "confidence: float = 0.0"
                ),
            },
        ),
        NativeDelta(
            primitive="ADD_FUNCTION",
            target_path=TARGET,
            parameters={
                "source": (
                    "def calibrate(value: Any) -> "
                    "SemanticResult:\n"
                    "    return SemanticResult()\n"
                ),
            },
        ),
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_delta",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="build semantic peripheral",
        deltas=deltas,
    )

    assert [
        step.primitive
        for step in plan.steps
    ] == [
        "CREATE_FILE",
        "ADD_IMPORT",
        "ADD_CLASS",
        "ADD_FIELD",
        "ADD_FUNCTION",
    ]

    result = execute_native_plan(
        plan,
        {},
    )

    assert result.status == "PASS"

    generated = result.generated_sources[TARGET]

    assert "from typing import Any" in generated
    assert "class SemanticResult" in generated
    assert "confidence: float = 0.0" in generated
    assert "def calibrate" in generated

    ast.parse(generated)


def test_delta_dependencies_are_generated():

    deltas = [
        NativeDelta(
            primitive="CREATE_FILE",
            target_path=TARGET,
            parameters={
                "source": "VALUE = 1\n",
            },
        ),
        NativeDelta(
            primitive="ADD_FUNCTION",
            target_path=TARGET,
            parameters={
                "source": (
                    "def f():\n"
                    "    return VALUE\n"
                )
            },
        ),
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_dependencies",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="dependency chain",
        deltas=deltas,
    )

    assert plan.steps[0].depends_on == ()
    assert plan.steps[1].depends_on == (
        plan.steps[0].step_id,
    )


def test_unknown_primitive_is_rejected():

    with pytest.raises(
        NativeDecompositionError,
        match="DELTA_PRIMITIVE_UNKNOWN",
    ):
        compile_native_deltas_to_plan(
            request_id="rr_invalid",
            spec_id="BRODY_ENGINEERING_SPEC_V1",
            objective="invalid",
            deltas=[
                NativeDelta(
                    primitive="MAGIC_CODE",
                    target_path=TARGET,
                )
            ],
        )


def test_missing_parameters_are_rejected():

    with pytest.raises(
        NativeDecompositionError,
        match="DELTA_PARAMETER_REQUIRED",
    ):
        compile_native_deltas_to_plan(
            request_id="rr_invalid_params",
            spec_id="BRODY_ENGINEERING_SPEC_V1",
            objective="invalid",
            deltas=[
                NativeDelta(
                    primitive="MODIFY_FUNCTION",
                    target_path=TARGET,
                    parameters={
                        "name": "f",
                    },
                )
            ],
        )
