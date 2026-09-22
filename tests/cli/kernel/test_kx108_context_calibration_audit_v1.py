from scripts.kernel.kx108_context_calibration_audit_v1 import (
    KX108ContextCalibrationAudit,
)


def receipt():

    return {
        "receipt_id":
            "kx108-context-calibration-receipt-v1",
        "context_id":
            "ctx-001",
        "calibration_target":
            "PERIPHERY",
        "calibration_status":
            "APPLIED",
        "kernel_mutation":
            False,
    }


def test_calibration_audit_passes():

    result = (
        KX108ContextCalibrationAudit()
        .audit(receipt())
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_receipt_validation():

    result = (
        KX108ContextCalibrationAudit()
        .audit(receipt())
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_periphery_binding():

    result = (
        KX108ContextCalibrationAudit()
        .audit(receipt())
    )

    assert (
        result["checks"]["periphery_target"]
        is True
    )


def test_kernel_protection():

    result = (
        KX108ContextCalibrationAudit()
        .audit(receipt())
    )

    assert (
        result["checks"]["kernel_protected"]
        is True
    )


def test_system_integrity():

    status = (
        KX108ContextCalibrationAudit()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
