from periphery.agents.obsidure_native_executor import (
    execute_native_step,
)
from periphery.agents.obsidure_native_plan import (
    NativePlanStep,
)


TARGET = "apps/obsidia_api/executor_field_guard_probe.py"


def _step(
    source: str,
) -> NativePlanStep:
    return NativePlanStep(
        step_id="nps_field_guard",
        primitive="MODIFY_FIELD",
        target_path=TARGET,
        rationale="executor fail-closed probe",
        parameters={
            "class_name": "Config",
            "name": "confidence",
            "source": source,
        },
        execution_ready=True,
    )


def test_modify_field_blocks_non_isolated_current_assignment():
    current = (
        "class Config:\n"
        "    confidence = obj.value = 0.0\n"
    )

    result = execute_native_step(
        _step(
            "confidence: float = 1.0"
        ),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "FIELD_TARGET_NOT_ISOLATED:"
        "Config.confidence"
        in error
        for error in result.errors
    )


def test_modify_field_blocks_non_isolated_replacement():
    current = (
        "class Config:\n"
        "    confidence: float = 0.0\n"
    )

    result = execute_native_step(
        _step(
            "confidence = obj.value = 1.0"
        ),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "FIELD_REPLACEMENT_NOT_ISOLATED:"
        "Config.confidence"
        in error
        for error in result.errors
    )


def test_modify_field_blocks_duplicate_field():
    current = (
        "class Config:\n"
        "    confidence: float = 0.0\n"
        "    confidence: float = 0.5\n"
    )

    result = execute_native_step(
        _step(
            "confidence: float = 1.0"
        ),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_FIELD_COUNT:"
        "Config.confidence:2"
        in error
        for error in result.errors
    )


def test_modify_field_blocks_missing_class():
    current = (
        "class Other:\n"
        "    confidence: float = 0.0\n"
    )

    result = execute_native_step(
        _step(
            "confidence: float = 1.0"
        ),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_CLASS_COUNT:Config:0"
        in error
        for error in result.errors
    )


def test_modify_field_blocks_missing_field():
    current = (
        "class Config:\n"
        "    other: float = 0.0\n"
    )

    result = execute_native_step(
        _step(
            "confidence: float = 1.0"
        ),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_FIELD_COUNT:"
        "Config.confidence:0"
        in error
        for error in result.errors
    )
