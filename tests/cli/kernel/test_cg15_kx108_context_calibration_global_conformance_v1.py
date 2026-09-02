from scripts.kernel.kx108_adaptive_context_boundary_v1 import (
    KX108AdaptiveContextBoundary,
)

from scripts.kernel.kx108_context_calibration_receipt_v1 import (
    KX108ContextCalibrationReceiptBuilder,
)

from scripts.kernel.kx108_context_calibration_audit_v1 import (
    KX108ContextCalibrationAudit,
)


def build_context():

    return {
        "context_id": "ctx-global-001",
        "domain": "operational",
    }


def build_calibration():

    return {
        "status": "APPLIED",
        "parameter": "context_weight",
    }


def build_receipt():

    return (
        KX108ContextCalibrationReceiptBuilder()
        .create(
            build_context(),
            build_calibration(),
        )
        .to_dict()
    )


def test_full_cg15_calibration_chain():

    boundary = KX108AdaptiveContextBoundary()

    context_result = (
        boundary.accept_context(
            build_context()
        )
    )

    assert (
        context_result["context_status"]
        == "ACCEPTED"
    )


    receipt = build_receipt()


    audit = (
        KX108ContextCalibrationAudit()
        .audit(receipt)
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_boundary_to_receipt_binding():

    receipt = build_receipt()

    assert (
        receipt["context_id"]
        == "ctx-global-001"
    )


def test_calibration_target_is_periphery():

    receipt = build_receipt()

    assert (
        receipt["calibration_target"]
        == "PERIPHERY"
    )


def test_audit_validates_kernel_protection():

    result = (
        KX108ContextCalibrationAudit()
        .audit(
            build_receipt()
        )
    )

    assert (
        result["checks"]["kernel_protected"]
        is True
    )


def test_final_cg15_integrity():

    boundary_status = (
        KX108AdaptiveContextBoundary()
        .status()
    )

    audit_status = (
        KX108ContextCalibrationAudit()
        .status()
    )

    assert (
        boundary_status["memory_write"]
        is False
    )

    assert (
        boundary_status["kernel_mutation"]
        is False
    )

    assert (
        audit_status["kernel_mutation"]
        is False
    )
