from scripts.kernel.kx108_act_receipt_v1 import (
    KX108ACTReceiptBuilder,
)


def act_result():

    return {
        "act_status": "ACT_BLOCKED",
        "act": False,
    }


def test_receipt_creation():

    receipt = KX108ACTReceiptBuilder().create(
        act_result()
    )

    assert (
        receipt.receipt_id
        == "kx108-act-receipt-v1"
    )


def test_act_status_trace():

    receipt = KX108ACTReceiptBuilder().create(
        act_result()
    )

    assert (
        receipt.act_status
        == "ACT_BLOCKED"
    )


def test_source_boundary():

    receipt = KX108ACTReceiptBuilder().create(
        act_result()
    )

    assert (
        receipt.source_boundary
        == "KX108_ACT_BOUNDARY"
    )


def test_no_act_default():

    receipt = KX108ACTReceiptBuilder().create(
        act_result()
    )

    assert receipt.act is False


def test_kernel_boundary():

    status = KX108ACTReceiptBuilder().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
