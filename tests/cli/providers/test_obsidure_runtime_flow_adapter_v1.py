from scripts.providers.obsidure_runtime_flow_adapter_v1 import (
    ObsidureRuntimeFlowAdapter,
)


def test_flow_execution():

    adapter = ObsidureRuntimeFlowAdapter()

    result = adapter.execute_flow(
        mission_id="mission-001",
        capability="proof",
        proof_target="theorem",
        payload={}
    )

    assert result["provider_id"] == "obsidure"
    assert result["verified"] is True


def test_proof_forwarding():

    adapter = ObsidureRuntimeFlowAdapter()

    result = adapter.execute_flow(
        mission_id="mission-001",
        capability="proof",
        proof_target="lemma",
        payload={}
    )

    assert result["proof"]["target"] == "lemma"


def test_authority_boundary():

    status = ObsidureRuntimeFlowAdapter().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_identity():

    assert ObsidureRuntimeFlowAdapter().provider_id == "obsidure"


def test_no_decision():

    result = ObsidureRuntimeFlowAdapter().execute_flow(
        mission_id="mission-001",
        capability="proof",
        proof_target="theorem",
        payload={}
    )

    assert "decision" not in result
