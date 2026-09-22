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
from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)
from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)
from periphery.agents.obsidure_native_semantic_compiler import (
    compile_semantic_operations,
)


TARGET = "apps/obsidia_api/method_probe.py"


def _desired_method(
    body_value: str,
) -> dict:
    return {
        "name": "calibrate",
        "args": [
            {
                "name": "self",
                "annotation": "",
            },
            {
                "name": "value",
                "annotation": "str",
            },
        ],
        "returns": "str",
        "body": [
            {
                "kind": "RETURN",
                "expr": {
                    "kind": "CONSTANT",
                    "value": body_value,
                },
            },
        ],
    }


def _desired(
    method: dict,
) -> DesiredTargetState:
    return DesiredTargetState(
        path=TARGET,
        classes=[
            {
                "name": "Calibrator",
                "methods": [method],
            },
        ],
    )


def test_code_state_observes_method_structurally():
    source = (
        "class Calibrator:\n"
        "    marker: int = 7\n\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n'
    )

    state = analyze_python_code_state(
        TARGET,
        source,
    )

    cls = state.classes["Calibrator"]

    assert "calibrate" in cls.methods
    assert "calibrate" in cls.method_states

    method = cls.method_states["calibrate"]

    assert method.name == "calibrate"
    assert method.args == [
        "self",
        "value",
    ]
    assert method.returns == "str"
    assert method.structural_fingerprint
    assert method.rewrite_safe is True


def test_identical_existing_method_is_no_change():
    source = (
        "class Calibrator:\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "RESOLVED"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired(
            _desired_method(
                "RESOLVED"
            )
        ),
    )

    assert operations == []


def test_missing_method_uses_add_method():
    source = (
        "class Calibrator:\n"
        "    marker: int = 7\n"
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired(
            _desired_method(
                "RESOLVED"
            )
        ),
    )

    assert [
        operation.kind
        for operation in operations
    ] == [
        "ADD_METHOD",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "ADD_METHOD",
    ]

    delta = deltas[0]

    assert (
        delta.parameters["class_name"]
        == "Calibrator"
    )

    assert (
        "def calibrate"
        in delta.parameters["source"]
    )


def test_different_method_uses_modify_method_and_preserves_class():
    source = (
        "class Calibrator:\n"
        "    marker: int = 7\n\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n\n'
        "    def keep(self) -> str:\n"
        '        return "KEEP"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired(
            _desired_method(
                "NEW"
            )
        ),
    )

    assert [
        operation.kind
        for operation in operations
    ] == [
        "MODIFY_METHOD",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "MODIFY_METHOD",
    ]

    delta = deltas[0]

    assert (
        delta.parameters["class_name"]
        == "Calibrator"
    )
    assert (
        delta.parameters["name"]
        == "calibrate"
    )

    plan = compile_native_deltas_to_plan(
        request_id="rr_method_probe",
        spec_id="spec_method_probe",
        objective=(
            "modify one existing class method"
        ),
        deltas=deltas,
    )

    assert [
        step.primitive
        for step in plan.steps
    ] == [
        "MODIFY_METHOD",
    ]

    execution = execute_native_plan(
        plan,
        {
            TARGET: source,
        },
    )

    assert execution.status == "PASS"

    generated = execution.generated_sources[
        TARGET
    ]

    tree = ast.parse(generated)

    cls = next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "Calibrator"
        )
    )

    fields = [
        node
        for node in cls.body
        if isinstance(
            node,
            ast.AnnAssign,
        )
    ]

    assert len(fields) == 1
    assert isinstance(
        fields[0].target,
        ast.Name,
    )
    assert fields[0].target.id == "marker"

    methods = {
        node.name: node
        for node in cls.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
    }

    assert set(methods) == {
        "calibrate",
        "keep",
    }

    calibrate = methods["calibrate"]

    assert len(calibrate.body) == 1
    assert isinstance(
        calibrate.body[0],
        ast.Return,
    )
    assert isinstance(
        calibrate.body[0].value,
        ast.Constant,
    )
    assert (
        calibrate.body[0].value.value
        == "NEW"
    )

    keep = methods["keep"]

    assert isinstance(
        keep.body[0],
        ast.Return,
    )
    assert (
        keep.body[0].value.value
        == "KEEP"
    )


def test_duplicate_existing_method_fails_closed():
    source = (
        "class Calibrator:\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "ONE"\n\n'
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "TWO"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    method = (
        current
        .classes["Calibrator"]
        .method_states["calibrate"]
    )

    assert method.rewrite_safe is False

    with pytest.raises(
        DesiredStatePlanningError,
        match=(
            "CURRENT_METHOD_REWRITE_UNSAFE:"
            "Calibrator.calibrate"
        ),
    ):
        plan_desired_state(
            current,
            _desired(
                _desired_method(
                    "NEW"
                )
            ),
        )
