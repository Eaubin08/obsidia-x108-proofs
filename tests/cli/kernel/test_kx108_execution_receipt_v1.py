from scripts.kernel.kx108_execution_receipt_v1 import (
    KX108ExecutionReceiptBuilder,
)


def execution_result():

    return {
        "execution_status": "EXECUTION_AUTHORIZED",
    }


def test_receipt_creation():

    receipt = KX108ExecutionReceiptBuilder().create(
        execution_result()
    )

    assert (
        receipt.receipt_id
        == "kx108-execution-receipt-v1"
    )


def test_execution_status_trace():

    receipt = KX108ExecutionReceiptBuilder().create(
        execution_result()
    )

    assert (
        receipt.execution_status
        == "EXECUTION_AUTHORIZED"
    )


def test_source_boundary():

    receipt = KX108ExecutionReceiptBuilder().create(
        execution_result()
    )

    assert (
        receipt.source_boundary
        == "KX108_EXECUTION_BOUNDARY"
    )


def test_no_act():

    receipt = KX108ExecutionReceiptBuilder().create(
        execution_result()
    )

    assert receipt.act is False


def test_kernel_boundary():

    status = KX108ExecutionReceiptBuilder().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
