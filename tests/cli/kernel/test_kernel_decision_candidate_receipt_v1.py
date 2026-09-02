from scripts.kernel.kernel_decision_candidate_receipt_v1 import (
    KernelDecisionCandidateReceipt,
)


def candidate():

    return {
        "source_provider": "brody",
        "runtime_ref": "runtime-001",
        "decision_status": "CANDIDATE_ONLY",
    }


def test_candidate_receipt_creation():

    receipt = KernelDecisionCandidateReceipt().create(
        candidate()
    )

    assert receipt.receipt_id == "candidate-receipt-v1"


def test_provider_trace():

    receipt = KernelDecisionCandidateReceipt().create(
        candidate()
    )

    assert receipt.source_provider == "brody"


def test_runtime_trace():

    receipt = KernelDecisionCandidateReceipt().create(
        candidate()
    )

    assert receipt.runtime_ref == "runtime-001"


def test_candidate_only():

    receipt = KernelDecisionCandidateReceipt().create(
        candidate()
    )

    assert receipt.candidate_status == "CANDIDATE_ONLY"


def test_kernel_boundary():

    status = KernelDecisionCandidateReceipt().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
