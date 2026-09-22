import ast

from periphery.agents.obsidure_native_executor import (
    execute_native_step,
)
from periphery.agents.obsidure_native_plan import NativePlanStep


def step(primitive, parameters):
    return NativePlanStep(
        step_id="nps_test",
        primitive=primitive,
        target_path="periphery/example.py",
        rationale="test",
        parameters=parameters,
        execution_ready=True,
    )


def test_add_import():
    source = '"""module"""\n\nVALUE = 1\n'

    result = execute_native_step(
        step(
            "ADD_IMPORT",
            {"statement": "from typing import Any"},
        ),
        source,
    )

    assert result.status == "PASS"
    assert "from typing import Any" in result.generated_source
    ast.parse(result.generated_source)


def test_add_function():
    source = "VALUE = 1\n"

    result = execute_native_step(
        step(
            "ADD_FUNCTION",
            {
                "source": (
                    "def calibrate(value: str) -> str:\n"
                    "    return value\n"
                )
            },
        ),
        source,
    )

    assert result.status == "PASS"
    assert "def calibrate" in result.generated_source
    ast.parse(result.generated_source)


def test_modify_function():
    source = (
        "def calibrate(value):\n"
        "    return None\n"
    )

    result = execute_native_step(
        step(
            "MODIFY_FUNCTION",
            {
                "name": "calibrate",
                "source": (
                    "def calibrate(value):\n"
                    "    return value\n"
                ),
            },
        ),
        source,
    )

    assert result.status == "PASS"
    assert "return value" in result.generated_source
    assert "return None" not in result.generated_source
    ast.parse(result.generated_source)


def test_add_class():
    result = execute_native_step(
        step(
            "ADD_CLASS",
            {
                "source": (
                    "class SemanticResult:\n"
                    "    pass\n"
                )
            },
        ),
        "",
    )

    assert result.status == "PASS"
    assert "class SemanticResult" in result.generated_source
    ast.parse(result.generated_source)


def test_add_field():
    source = (
        "class SemanticResult:\n"
        "    value: str\n"
    )

    result = execute_native_step(
        step(
            "ADD_FIELD",
            {
                "class_name": "SemanticResult",
                "source": "confidence: float = 0.0",
            },
        ),
        source,
    )

    assert result.status == "PASS"
    assert "confidence: float = 0.0" in result.generated_source
    ast.parse(result.generated_source)


def test_duplicate_field_is_blocked():
    source = (
        "class SemanticResult:\n"
        "    confidence: float = 0.0\n"
    )

    result = execute_native_step(
        step(
            "ADD_FIELD",
            {
                "class_name": "SemanticResult",
                "source": "confidence: float = 1.0",
            },
        ),
        source,
    )

    assert result.status == "BLOCKED"
    assert result.errors
    assert "FIELD_ALREADY_PRESENT" in result.errors[0]


def test_unsupported_operation_is_blocked():
    result = execute_native_step(
        step(
            "MAGIC_REWRITE",
            {},
        ),
        "VALUE = 1\n",
    )

    assert result.status == "BLOCKED"
    assert (
        result.errors[0]
        == "NATIVE_EXECUTOR_UNSUPPORTED:MAGIC_REWRITE"
    )
