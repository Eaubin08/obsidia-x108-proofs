from scripts.providers.brody_runtime_flow_adapter_v1 import (
    BrodyRuntimeFlowAdapter,
)


def test_flow_execution():

    adapter = BrodyRuntimeFlowAdapter()

    result = adapter.execute_flow(
        mission_id="mission-001",
        capability="analysis",
        payload={
            "text":"hello"
        },
    )

    assert result["provider_id"] == "brody"
    assert result["result"]["processed"] is True


def test_payload_forwarding():

    adapter = BrodyRuntimeFlowAdapter()

    result = adapter.execute_flow(
        mission_id="mission-001",
        capability="analysis",
        payload={
            "value":42
        },
    )

    assert result["result"]["input"]["value"] == 42


def test_authority_boundary():

    adapter = BrodyRuntimeFlowAdapter()

    status = adapter.status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_identity():

    adapter = BrodyRuntimeFlowAdapter()

    assert adapter.provider_id == "brody"


def test_no_decision_output():

    adapter = BrodyRuntimeFlowAdapter()

    result = adapter.execute_flow(
        mission_id="mission-001",
        capability="analysis",
        payload={}
    )

    assert "decision" not in result
