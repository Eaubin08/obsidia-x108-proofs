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


TARGET = "apps/obsidia_api/multistep_probe.py"


def test_add_import_then_modify_function_in_one_plan():
    source = (
        "def calibrate(value: Any) -> str:\n"
        '    return "OLD"\n'
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
            },
        ],
        functions=[
            {
                "name": "calibrate",
                "args": [
                    {
                        "name": "value",
                        "annotation": "Any",
                    },
                ],
                "returns": "str",
                "body": [
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "CONSTANT",
                            "value": "NEW",
                        },
                    },
                ],
            },
        ],
    )

    operations = plan_desired_state(
        current,
        desired,
    )

    assert [
        operation.kind
        for operation in operations
    ] == [
        "IMPORT_FROM",
        "MODIFY_FUNCTION",
    ]

    deltas = compile_semantic_operations(
        operations
    )

    assert [
        delta.primitive
        for delta in deltas
    ] == [
        "ADD_IMPORT",
        "MODIFY_FUNCTION",
    ]

    plan = compile_native_deltas_to_plan(
        request_id="rr_multistep_probe",
        spec_id="spec_multistep_probe",
        objective=(
            "add required import and modify "
            "existing function"
        ),
        deltas=deltas,
    )

    assert [
        step.primitive
        for step in plan.steps
    ] == [
        "ADD_IMPORT",
        "MODIFY_FUNCTION",
    ]

    assert plan.steps[0].depends_on == ()
    assert plan.steps[1].depends_on == (
        plan.steps[0].step_id,
    )

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

    assert "from typing import Any" in generated

    tree = ast.parse(generated)

    function = next(
        node
        for node in tree.body
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "calibrate"
        )
    )

    assert len(function.body) == 1
    assert isinstance(function.body[0], ast.Return)
    assert isinstance(
        function.body[0].value,
        ast.Constant,
    )
    assert function.body[0].value.value == "NEW"

    # Both transformations must coexist in the
    # same final candidate source.
    assert generated.index(
        "from typing import Any"
    ) < generated.index(
        "def calibrate"
    )
