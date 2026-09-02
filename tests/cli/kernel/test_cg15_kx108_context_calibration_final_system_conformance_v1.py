from scripts.kernel.kx108_adaptive_context_boundary_v1 import (
    KX108AdaptiveContextBoundary,
)

from scripts.kernel.kx108_context_calibration_receipt_v1 import (
    KX108ContextCalibrationReceiptBuilder,
)

from scripts.kernel.kx108_context_calibration_audit_v1 import (
    KX108ContextCalibrationAudit,
)


def context():

    return {
        "context_id": "ctx-final-001",
        "domain": "adaptive",
    }


def calibration():

    return {
        "status": "APPLIED",
        "parameter": "domain_context",
    }


def receipt():

    return (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            context(),
            calibration(),
        )
        .to_dict()
    )


def test_full_cg15_chain():

    boundary = (
        KX108AdaptiveContextBoundary()
    )

    result = boundary.accept_context(
        context()
    )

    assert (
        result["context_status"]
        == "ACCEPTED"
    )


    audit = (
        KX108ContextCalibrationAudit()
        .audit(
            receipt()
        )
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_receipt_binding():

    data = receipt()

    assert (
        data["context_id"]
        == "ctx-final-001"
    )


def test_periphery_only():

    data = receipt()

    assert (
        data["calibration_target"]
        == "PERIPHERY"
    )


def test_audit_kernel_protection():

    result = (
        KX108ContextCalibrationAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["kernel_protected"]
        is True
    )


def test_final_integrity():

    boundary = (
        KX108AdaptiveContextBoundary()
        .status()
    )

    audit = (
        KX108ContextCalibrationAudit()
        .status()
    )

    assert boundary["memory_write"] is False
    assert boundary["kernel_mutation"] is False

    assert audit["memory_write"] is False
    assert audit["kernel_mutation"] is False
