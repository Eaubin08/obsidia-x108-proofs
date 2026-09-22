import ast

import pytest

from apps.obsidia_api.brody_code_state import (
    analyze_python_code_state,
)
from apps.obsidia_api.brody_desired_state_planner import (
    DesiredStatePlanningError,
    DesiredTargetState,
    plan_desired_state,
)
from periphery.agents.obsidure_native_semantic_compiler import (
    compile_semantic_operations,
)


TARGET = "apps/obsidia_api/example.py"


def desired_function(
    value: str = "NEW",
):
    return {
        "name": "calibrate",
        "args": [
            {
                "name": "term",
                "annotation": "str",
            }
        ],
        "returns": "str",
        "body": [
            {
                "kind": "RETURN",
                "expr": {
                    "kind": "CONSTANT",
                    "value": value,
                },
            }
        ],
    }


def test_code_state_observes_structural_function():
    current = analyze_python_code_state(
        TARGET,
        (
            "def calibrate(term: str) -> str:\n"
            "    return 'OLD'\n"
        ),
    )

    fn = current.functions["calibrate"]

    assert fn.args == ["term"]
    assert fn.arg_specs == [
        {
            "name": "term",
            "annotation": "str",
        }
    ]
    assert fn.structural_fingerprint
    assert fn.rewrite_safe is True


def test_existing_different_function_emits_modify():
    current = analyze_python_code_state(
        TARGET,
        (
            "def calibrate(term: str) -> str:\n"
            "    return 'OLD'\n"
        ),
    )

    desired = DesiredTargetState(
        path=TARGET,
        functions=[
            desired_function("NEW"),
        ],
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert len(operations) == 1

    op = operations[0]

    assert op.kind == "MODIFY_FUNCTION"
    assert op.payload["name"] == "calibrate"

    deltas = compile_semantic_operations(
        operations
    )

    assert len(deltas) == 1
    assert deltas[0].primitive == (
        "MODIFY_FUNCTION"
    )
    assert (
        deltas[0].parameters["name"]
        == "calibrate"
    )

    generated = (
        deltas[0].parameters["source"]
    )

    ast.parse(generated)

    assert "NEW" in generated
    assert "OLD" not in generated


def test_identical_function_emits_no_operation():
    current = analyze_python_code_state(
        TARGET,
        (
            "def calibrate(term: str) -> str:\n"
            "    return 'NEW'\n"
        ),
    )

    desired = DesiredTargetState(
        path=TARGET,
        functions=[
            desired_function("NEW"),
        ],
    )

    assert (
        plan_desired_state(
            current,
            desired,
        )
        == []
    )


def test_unsafe_existing_function_is_fail_closed():
    current = analyze_python_code_state(
        TARGET,
        (
            "@decorator\n"
            "def calibrate(term: str) -> str:\n"
            "    return 'OLD'\n"
        ),
    )

    assert (
        current.functions[
            "calibrate"
        ].rewrite_safe
        is False
    )

    desired = DesiredTargetState(
        path=TARGET,
        functions=[
            desired_function("NEW"),
        ],
    )

    with pytest.raises(
        DesiredStatePlanningError,
        match=(
            "CURRENT_FUNCTION_REWRITE_UNSAFE:"
            "calibrate"
        ),
    ):
        plan_desired_state(
            current,
            desired,
        )
