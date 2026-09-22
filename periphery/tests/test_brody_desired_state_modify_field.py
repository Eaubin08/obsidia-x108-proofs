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


TARGET = "apps/obsidia_api/field_probe.py"


def _desired_field(
    *,
    default: float = 1.0,
):
    return DesiredTargetState(
        path=TARGET,
        classes=[
            {
                "name": "Config",
                "fields": [
                    {
                        "name": "confidence",
                        "annotation": "float",
                        "default_expr": {
                            "kind": "CONSTANT",
                            "value": default,
                        },
                    },
                ],
            },
        ],
    )


def test_code_state_observes_field_structurally():
    source = (
        "class Config:\n"
        "    confidence: float = 0.0\n"
        "\n"
        "    def keep(self):\n"
        '        return "KEEP"\n'
    )

    state = analyze_python_code_state(
        TARGET,
        source,
    )

    cls = state.classes["Config"]
    field = cls.field_states["confidence"]

    assert cls.fields == ["confidence"]
    assert "keep" in cls.methods

    assert field.name == "confidence"
    assert field.annotation == "float"
    assert field.structural_fingerprint
    assert field.rewrite_safe is True


def test_identical_existing_field_is_no_change():
    source = (
        "class Config:\n"
        "    confidence: float = 1.0\n"
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired_field(default=1.0),
    )

    assert operations == []


def test_missing_field_uses_add_field():
    source = (
        "class Config:\n"
        "    def keep(self):\n"
        '        return "KEEP"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired_field(default=1.0),
    )

    assert len(operations) == 1
    assert operations[0].kind == "ADD_FIELD"

    deltas = compile_semantic_operations(
        operations
    )

    assert len(deltas) == 1
    assert deltas[0].primitive == "ADD_FIELD"


def test_different_field_uses_modify_field_and_preserves_methods():
    source = (
        "class Config:\n"
        "    confidence: float = 0.0\n"
        "\n"
        "    def keep(self):\n"
        '        return "KEEP"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    operations = plan_desired_state(
        current,
        _desired_field(default=1.0),
    )

    assert len(operations) == 1

    operation = operations[0]

    assert operation.kind == "MODIFY_FIELD"
    assert operation.payload["class_name"] == "Config"
    assert operation.payload["name"] == "confidence"

    deltas = compile_semantic_operations(
        operations
    )

    assert len(deltas) == 1

    delta = deltas[0]

    assert delta.primitive == "MODIFY_FIELD"
    assert delta.parameters["class_name"] == "Config"
    assert delta.parameters["name"] == "confidence"
    assert "confidence: float = 1.0" in (
        delta.parameters["source"]
    )

    plan = compile_native_deltas_to_plan(
        request_id="rr_modify_field_probe",
        spec_id="spec_modify_field_probe",
        objective=(
            "modify one existing class field "
            "without rebuilding the class"
        ),
        deltas=deltas,
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].primitive == "MODIFY_FIELD"

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

    assert "confidence: float = 1.0" in generated
    assert "confidence: float = 0.0" not in generated

    assert "def keep(self):" in generated
    assert 'return "KEEP"' in generated

    tree = ast.parse(generated)

    cls = next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.ClassDef)
            and node.name == "Config"
        )
    )

    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "keep"
        for node in cls.body
    )


def test_multi_target_existing_field_fails_closed():
    source = (
        "class Config:\n"
        "    confidence = other = 0.0\n"
        "\n"
        "    def keep(self):\n"
        '        return "KEEP"\n'
    )

    current = analyze_python_code_state(
        TARGET,
        source,
    )

    field = (
        current
        .classes["Config"]
        .field_states["confidence"]
    )

    assert field.rewrite_safe is False

    with pytest.raises(
        DesiredStatePlanningError,
        match=(
            "CURRENT_FIELD_REWRITE_UNSAFE:"
            "Config.confidence"
        ),
    ):
        plan_desired_state(
            current,
            _desired_field(default=1.0),
        )
