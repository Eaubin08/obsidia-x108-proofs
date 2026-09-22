from scripts.kernel.kx108_operational_loop_receipt_v1 import (
    KX108OperationalLoopReceiptBuilder,
)


def transition_result():

    return {
        "transition_status": "ACCEPTED",
        "state": "DECISION_PENDING",
    }


def test_receipt_creation():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition_result(),
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert (
        receipt.receipt_id
        == "kx108-operational-loop-receipt-v1"
    )


def test_previous_state_trace():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition_result(),
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert (
        receipt.previous_state
        == "OBSERVATION"
    )


def test_transition_trace():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition_result(),
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert (
        receipt.transition
        == "DECISION_PENDING"
    )


def test_next_state_trace():

    receipt = (
        KX108OperationalLoopReceiptBuilder()
        .create(
            transition_result(),
            "OBSERVATION",
            "DECISION_PENDING",
        )
    )

    assert (
        receipt.next_state
        == "DECISION_PENDING"
    )


def test_kernel_protection():

    status = (
        KX108OperationalLoopReceiptBuilder()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
