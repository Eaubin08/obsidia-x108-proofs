from periphery.agents.obsidure_native_executor import (
    execute_native_step,
)
from periphery.agents.obsidure_native_plan import (
    NativePlanStep,
)


TARGET = (
    "apps/obsidia_api/"
    "executor_method_guard_probe.py"
)


def _step(
    source: str,
) -> NativePlanStep:
    return NativePlanStep(
        step_id="nps_method_guard",
        primitive="MODIFY_METHOD",
        target_path=TARGET,
        rationale="executor fail-closed probe",
        parameters={
            "class_name": "Calibrator",
            "name": "calibrate",
            "source": source,
        },
        execution_ready=True,
    )


SAFE_REPLACEMENT = (
    "def calibrate("
    "self, value: str"
    ") -> str:\n"
    '    return "NEW"\n'
)


def test_modify_method_blocks_async_current_method():
    current = (
        "class Calibrator:\n"
        "    async def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n'
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "METHOD_TARGET_REWRITE_UNSAFE:"
        "Calibrator.calibrate"
        in error
        for error in result.errors
    )


def test_modify_method_blocks_decorated_current_method():
    current = (
        "class Calibrator:\n"
        "    @staticmethod\n"
        "    def calibrate("
        "value: str"
        ") -> str:\n"
        '        return "OLD"\n'
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "METHOD_TARGET_REWRITE_UNSAFE:"
        "Calibrator.calibrate"
        in error
        for error in result.errors
    )


def test_modify_method_blocks_decorated_replacement():
    current = (
        "class Calibrator:\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n'
    )

    replacement = (
        "@staticmethod\n"
        "def calibrate("
        "value: str"
        ") -> str:\n"
        '    return "NEW"\n'
    )

    result = execute_native_step(
        _step(replacement),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "METHOD_REPLACEMENT_REWRITE_UNSAFE:"
        "Calibrator.calibrate"
        in error
        for error in result.errors
    )


def test_modify_method_blocks_duplicate_method():
    current = (
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

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_METHOD_COUNT:"
        "Calibrator.calibrate:2"
        in error
        for error in result.errors
    )


def test_modify_method_blocks_missing_class():
    current = (
        "class Other:\n"
        "    def calibrate("
        "self, value: str"
        ") -> str:\n"
        '        return "OLD"\n'
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_CLASS_COUNT:"
        "Calibrator:0"
        in error
        for error in result.errors
    )


def test_modify_method_blocks_missing_method():
    current = (
        "class Calibrator:\n"
        "    def other(self) -> str:\n"
        '        return "OLD"\n'
    )

    result = execute_native_step(
        _step(SAFE_REPLACEMENT),
        current,
    )

    assert result.status == "BLOCKED"
    assert any(
        "TARGET_METHOD_COUNT:"
        "Calibrator.calibrate:0"
        in error
        for error in result.errors
    )
