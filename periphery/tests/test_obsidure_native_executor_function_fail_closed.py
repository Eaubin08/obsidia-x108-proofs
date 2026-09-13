from periphery.agents.obsidure_native_executor import (
    execute_native_step,
)
from periphery.agents.obsidure_native_plan import (
    NativePlanStep,
)


TARGET = (
    "apps/obsidia_api/"
    "executor_function_guard_probe.py"
)


def _step(source: str) -> NativePlanStep:
    return NativePlanStep(
        step_id="nps_function_guard",
        primitive="MODIFY_FUNCTION",
        target_path=TARGET,
        rationale="executor fail-closed probe",
        parameters={
            "name": "normalize",
            "source": source,
        },
        execution_ready=True,
    )


SAFE_REPLACEMENT = (
    "def normalize(value: float) -> float:\n"
    "    return value + 1.0\n"
)


def test_modify_function_blocks_async_current():
    current = (
        "async def normalize("
        "value: float"
        ") -> float:\n"
        "    return value\n"
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "FUNCTION_TARGET_REWRITE_UNSAFE:"
        "normalize"
        in error
        for error in result.errors
    )


def test_modify_function_blocks_decorated_current():
    current = (
        "@staticmethod\n"
        "def normalize("
        "value: float"
        ") -> float:\n"
        "    return value\n"
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "FUNCTION_TARGET_REWRITE_UNSAFE:"
        "normalize"
        in error
        for error in result.errors
    )


def test_modify_function_blocks_decorated_replacement():
    current = (
        "def normalize("
        "value: float"
        ") -> float:\n"
        "    return value\n"
    )

    replacement = (
        "@staticmethod\n"
        "def normalize("
        "value: float"
        ") -> float:\n"
        "    return value + 1.0\n"
    )

    result = execute_native_step(
        _step(replacement),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "FUNCTION_REPLACEMENT_REWRITE_UNSAFE:"
        "normalize"
        in error
        for error in result.errors
    )


def test_modify_function_blocks_duplicate_target():
    current = (
        "def normalize(value: float) -> float:\n"
        "    return value\n\n"
        "def normalize(value: float) -> float:\n"
        "    return value + 2.0\n"
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_DEFINITION_COUNT:"
        "normalize:2"
        in error
        for error in result.errors
    )


def test_modify_function_blocks_missing_target():
    current = (
        "def other(value: float) -> float:\n"
        "    return value\n"
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_DEFINITION_COUNT:"
        "normalize:0"
        in error
        for error in result.errors
    )
