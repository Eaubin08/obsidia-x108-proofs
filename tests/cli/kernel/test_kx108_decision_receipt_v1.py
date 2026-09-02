from scripts.kernel.kx108_decision_receipt_v1 import (
    KX108DecisionReceiptBuilder,
)


def envelope():

    return {
        "authority_status": "AUTHORIZED_CANDIDATE",
        "decision_status": "KX108_DECISION_READY",
    }


def test_receipt_creation():

    receipt = KX108DecisionReceiptBuilder().create(
        envelope()
    )

    assert (
        receipt.receipt_id
        == "kx108-decision-receipt-v1"
    )


def test_authority_trace():

    receipt = KX108DecisionReceiptBuilder().create(
        envelope()
    )

    assert (
        receipt.authority_status
        == "AUTHORIZED_CANDIDATE"
    )


def test_decision_trace():

    receipt = KX108DecisionReceiptBuilder().create(
        envelope()
    )

    assert (
        receipt.decision_status
        == "KX108_DECISION_READY"
    )


def test_source_envelope():

    receipt = KX108DecisionReceiptBuilder().create(
        envelope()
    )

    assert (
        receipt.source_envelope
        == "KX108_DECISION_ENVELOPE"
    )


def test_kernel_boundary():

    status = KX108DecisionReceiptBuilder().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
