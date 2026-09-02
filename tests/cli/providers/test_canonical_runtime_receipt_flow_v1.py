from scripts.providers.canonical_runtime_receipt_flow_v1 import (
    CanonicalRuntimeReceiptFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-receipt-001",
        "provider": "brody",
    }


def test_receipt_flow_execution():

    flow = CanonicalRuntimeReceiptFlow()

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

    assert output["receipt"]["provider_id"] == "brody"


def test_receipt_binding():

    flow = CanonicalRuntimeReceiptFlow()

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

    assert (
        output["receipt"]["result_ref"]
        == output["execution"]["execution"]["envelope"]["runtime_id"]
    )


def test_envelope_preserved():

    flow = CanonicalRuntimeReceiptFlow()

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

    assert output["execution"]["flow_status"] == "COMPLETED"


def test_authority_boundary():

    status = CanonicalRuntimeReceiptFlow().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_route():

    flow = CanonicalRuntimeReceiptFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    assert "brody" in flow.flow.orchestrator.router.routes
