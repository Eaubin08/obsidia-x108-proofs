import ast

from periphery.agents.obsidure_native_plan import (
    NativePlan,
    NativePlanStep,
)
from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)


TARGET = "periphery/example.py"


def test_multiple_native_operations_compose_sequentially():

    s1 = NativePlanStep(
        step_id="s1",
        primitive="ADD_IMPORT",
        target_path=TARGET,
        rationale="typing dependency",
        parameters={
            "statement": "from typing import Any",
        },
        execution_ready=True,
    )

    s2 = NativePlanStep(
        step_id="s2",
        primitive="ADD_FUNCTION",
        target_path=TARGET,
        rationale="add calibration function",
        parameters={
            "source": (
                "def calibrate(value: Any) -> Any:\n"
                "    return value\n"
            ),
        },
        depends_on=("s1",),
        execution_ready=True,
    )

    s3 = NativePlanStep(
        step_id="s3",
        primitive="ADD_CLASS",
        target_path=TARGET,
        rationale="add result class",
        parameters={
            "source": (
                "class SemanticResult:\n"
                "    value: Any\n"
            ),
        },
        depends_on=("s2",),
        execution_ready=True,
    )

    s4 = NativePlanStep(
        step_id="s4",
        primitive="ADD_FIELD",
        target_path=TARGET,
        rationale="extend result",
        parameters={
            "class_name": "SemanticResult",
            "source": "confidence: float = 0.0",
        },
        depends_on=("s3",),
        execution_ready=True,
    )

    plan = NativePlan(
        request_id="rr_program",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="compose semantic calibration structures",
        steps=[s1, s2, s3, s4],
    )

    result = execute_native_plan(
        plan,
        {
            TARGET: "VALUE = 1\n",
        },
    )

    assert result.status == "PASS"
    assert result.completed_steps == [
        "s1",
        "s2",
        "s3",
        "s4",
    ]

    generated = result.generated_sources[TARGET]

    assert "from typing import Any" in generated
    assert "def calibrate" in generated
    assert "class SemanticResult" in generated
    assert "confidence: float = 0.0" in generated

    ast.parse(generated)


def test_second_operation_receives_first_operation_output():

    s1 = NativePlanStep(
        step_id="s1",
        primitive="ADD_FUNCTION",
        target_path=TARGET,
        rationale="initial function",
        parameters={
            "source": (
                "def calibrate(value):\n"
                "    return None\n"
            ),
        },
        execution_ready=True,
    )

    s2 = NativePlanStep(
        step_id="s2",
        primitive="MODIFY_FUNCTION",
        target_path=TARGET,
        rationale="evolve function",
        parameters={
            "name": "calibrate",
            "source": (
                "def calibrate(value):\n"
                "    return value\n"
            ),
        },
        depends_on=("s1",),
        execution_ready=True,
    )

    plan = NativePlan(
        request_id="rr_feedback",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="compose and evolve",
        steps=[s1, s2],
    )

    result = execute_native_plan(
        plan,
        {
            TARGET: "VALUE = 1\n",
        },
    )

    assert result.status == "PASS"

    generated = result.generated_sources[TARGET]

    assert "return value" in generated
    assert "return None" not in generated


def test_dependency_failure_blocks_execution():

    step = NativePlanStep(
        step_id="s2",
        primitive="ADD_FUNCTION",
        target_path=TARGET,
        rationale="invalid dependency",
        parameters={
            "source": (
                "def f():\n"
                "    return 1\n"
            ),
        },
        depends_on=("missing_step",),
        execution_ready=True,
    )

    plan = NativePlan(
        request_id="rr_dependency",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="dependency test",
        steps=[step],
    )

    result = execute_native_plan(
        plan,
        {
            TARGET: "VALUE = 1\n",
        },
    )

    assert result.status == "BLOCKED"
    assert result.blocked_step == "s2"
    assert (
        result.errors[0]
        == "STEP_DEPENDENCY_UNSATISFIED:missing_step"
    )


def test_high_level_modify_file_requires_decomposition():

    step = NativePlanStep(
        step_id="s1",
        primitive="MODIFY_FILE",
        target_path=TARGET,
        rationale="high-level operation",
    )

    plan = NativePlan(
        request_id="rr_decompose",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="modify target",
        steps=[step],
    )

    result = execute_native_plan(
        plan,
        {
            TARGET: "VALUE = 1\n",
        },
    )

    assert result.status == "NEEDS_DECOMPOSITION"
    assert (
        result.errors[0]
        == "HIGH_LEVEL_PRIMITIVE_REQUIRES_DECOMPOSITION:MODIFY_FILE"
    )


def test_verify_tests_is_not_fake_pass():

    step = NativePlanStep(
        step_id="verify",
        primitive="VERIFY_TESTS",
        target_path="<acceptance>",
        rationale="verify",
    )

    plan = NativePlan(
        request_id="rr_verify",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="verify",
        steps=[step],
    )

    result = execute_native_plan(
        plan,
        {},
    )

    assert result.status == "AWAITING_VERIFICATION"
    assert result.errors == [
        "VERIFY_TESTS_EXECUTOR_NOT_CONNECTED"
    ]
