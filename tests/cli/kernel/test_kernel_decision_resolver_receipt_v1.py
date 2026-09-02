from scripts.kernel.kernel_decision_resolver_receipt_v1 import (
    KernelDecisionResolverReceipt,
)


def resolver_result():

    return {
        "resolver_status": "RESOLUTION_READY",
        "decision_status": "CANDIDATE_ONLY",
    }


def test_receipt_creation():

    receipt = KernelDecisionResolverReceipt().create(
        resolver_result()
    )

    assert receipt.receipt_id == "resolver-receipt-v1"


def test_resolver_trace():

    receipt = KernelDecisionResolverReceipt().create(
        resolver_result()
    )

    assert (
        receipt.resolver_status
        == "RESOLUTION_READY"
    )


def test_candidate_status():

    receipt = KernelDecisionResolverReceipt().create(
        resolver_result()
    )

    assert (
        receipt.decision_status
        == "CANDIDATE_ONLY"
    )


def test_gate_trace():

    receipt = KernelDecisionResolverReceipt().create(
        resolver_result()
    )

    assert (
        receipt.source_gate
        == "OPEN_FOR_DECISION"
    )


def test_kernel_boundary():

    status = KernelDecisionResolverReceipt().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
