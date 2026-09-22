from scripts.kernel.kx108_proof_canonical_receipt_flow_v1 import (
    KX108ProofCanonicalReceiptFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-cg33-001",
        "provider": "brody",
    }


def build_flow():

    flow = KX108ProofCanonicalReceiptFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    return flow


def run_flow():

    return build_flow().run(
        mission_id="mission-cg33",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def test_canonical_receipt_validated():

    result = run_flow()

    assert result["canonical_receipt_status"] == "VALIDATED"


def test_runtime_validation_composed():

    result = run_flow()

    assert (
        result["runtime_validation"]["runtime_validation_status"]
        == "VALIDATED"
    )


def test_receipt_validation_composed():

    result = run_flow()

    assert (
        result["receipt_validation"]["receipt_validation_status"]
        == "VALIDATED"
    )


def test_runtime_receipt_reference_closed():

    result = run_flow()

    runtime_ref = (
        result["execution"]
        ["execution"]
        ["execution"]
        ["envelope"]
        ["runtime_id"]
    )

    receipt_ref = (
        result["receipt_validation"]["result_ref"]
    )

    assert runtime_ref == receipt_ref


def test_canonical_receipt_has_no_authority():

    status = KX108ProofCanonicalReceiptFlow().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
