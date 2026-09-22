from scripts.providers.canonical_runtime_receipt_flow_v1 import (
    CanonicalRuntimeReceiptFlow,
)


def brody_provider(**kwargs):

    return {
        "runtime_id": "brody-final-runtime",
        "provider": "brody",
    }


def obsidure_provider(**kwargs):

    return {
        "runtime_id": "obsidure-final-runtime",
        "provider": "obsidure",
    }


def test_final_brody_chain():

    flow = CanonicalRuntimeReceiptFlow()

    flow.register_provider(
        "brody",
        brody_provider,
    )

    output = flow.run(
        mission_id="final-brody-001",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    envelope = output["execution"]["execution"]["envelope"]
    receipt = output["receipt"]

    assert envelope["status"] == "SEALED"
    assert receipt["provider_id"] == "brody"
    assert receipt["result_ref"] == envelope["runtime_id"]


def test_final_obsidure_chain():

    flow = CanonicalRuntimeReceiptFlow()

    flow.register_provider(
        "obsidure",
        obsidure_provider,
    )

    output = flow.run(
        mission_id="final-obsidure-001",
        provider_id="obsidure",
        capability="proof",
        payload={},
    )

    envelope = output["execution"]["execution"]["envelope"]
    receipt = output["receipt"]

    assert envelope["status"] == "SEALED"
    assert receipt["provider_id"] == "obsidure"
    assert receipt["result_ref"] == envelope["runtime_id"]


def test_final_provider_isolation():

    flow = CanonicalRuntimeReceiptFlow()

    flow.register_provider(
        "brody",
        brody_provider,
    )

    flow.register_provider(
        "obsidure",
        obsidure_provider,
    )

    assert len(flow.flow.orchestrator.router.routes) == 2


def test_final_governance_invariants():

    status = CanonicalRuntimeReceiptFlow().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_final_trace_integrity():

    flow = CanonicalRuntimeReceiptFlow()

    flow.register_provider(
        "brody",
        brody_provider,
    )

    output = flow.run(
        mission_id="final-trace-001",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    session = output["execution"]["execution"]["session"]
    envelope = output["execution"]["execution"]["envelope"]
    receipt = output["receipt"]

    assert session["mission_id"] == "final-trace-001"
    assert envelope["mission_id"] == session["mission_id"]
    assert receipt["invocation_id"] == session["mission_id"]
