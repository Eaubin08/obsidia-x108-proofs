from scripts.kernel.kx108_context_calibration_receipt_v1 import (
    KX108ContextCalibrationReceiptBuilder,
)


def context():

    return {
        "context_id": "ctx-001",
    }


def calibration():

    return {
        "status": "APPLIED",
    }


def test_receipt_creation():

    receipt = (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            context(),
            calibration(),
        )
    )

    assert (
        receipt.receipt_id
        == "kx108-context-calibration-receipt-v1"
    )


def test_context_binding():

    receipt = (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            context(),
            calibration(),
        )
    )

    assert (
        receipt.context_id
        == "ctx-001"
    )


def test_calibration_target():

    receipt = (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            context(),
            calibration(),
        )
    )

    assert (
        receipt.calibration_target
        == "PERIPHERY"
    )


def test_kernel_protection():

    receipt = (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            context(),
            calibration(),
        )
    )

    assert (
        receipt.kernel_mutation
        is False
    )


def test_system_integrity():

    status = (
        KX108ContextCalibrationReceiptBuilder()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
