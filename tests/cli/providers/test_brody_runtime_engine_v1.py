from scripts.providers.brody_runtime_contract_v1 import (
    BrodyRuntimeRequest,
)

from scripts.providers.brody_runtime_engine_v1 import (
    BrodyRuntimeEngine,
)


def build_request():

    return BrodyRuntimeRequest(
        mission_id="mission-001",
        capability="analysis",
        payload={
            "text":"hello"
        },
    )


def test_engine_execution():

    engine = BrodyRuntimeEngine()

    result = engine.execute(
        build_request()
    )

    assert result.provider_id == "brody"
    assert result.result["processed"] is True


def test_result_contains_input():

    engine = BrodyRuntimeEngine()

    result = engine.execute(
        build_request()
    )

    assert result.result["input"]["text"] == "hello"


def test_runtime_invariants():

    engine = BrodyRuntimeEngine()

    status = engine.status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_runtime_name():

    engine = BrodyRuntimeEngine()

    assert engine.runtime_name == "brody-runtime-v1"


def test_no_decision_output():

    engine = BrodyRuntimeEngine()

    result = engine.execute(
        build_request()
    )

    assert "decision" not in result.to_dict()
