from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-flow-001",
        "provider": "brody",
    }


def test_flow_execution():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    output = flow.run(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["flow_status"] == "COMPLETED"


def test_flow_envelope():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    output = flow.run(
        mission_id="mission-002",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["execution"]["envelope"]["status"] == "SEALED"


def test_runtime_trace():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    output = flow.run(
        mission_id="mission-003",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert (
        output["execution"]["envelope"]["runtime_id"]
        == "runtime-flow-001"
    )


def test_authority_boundary():

    status = CanonicalExecutionFlow().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_binding():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    assert "brody" in flow.orchestrator.router.routes
