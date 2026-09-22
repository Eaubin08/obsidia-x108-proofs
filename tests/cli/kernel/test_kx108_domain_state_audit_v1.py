from scripts.kernel.kx108_domain_state_audit_v1 import (
    KX108DomainStateAudit,
)


def receipt():

    return {
        "receipt_id":
            "kx108-domain-state-receipt-v1",

        "domain":
            "GPS",

        "state_hash":
            "gps-state-001",

        "confidence":
            0.95,

        "provenance":
            "gnss-adapter",

        "kernel_mutation":
            False,
    }


def test_domain_audit_passes():

    result = (
        KX108DomainStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["audit_status"]
        == "PASSED"
    )


def test_receipt_validation():

    result = (
        KX108DomainStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_domain_binding():

    result = (
        KX108DomainStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["domain_present"]
        is True
    )


def test_provenance_binding():

    result = (
        KX108DomainStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["provenance_present"]
        is True
    )


def test_kernel_integrity():

    status = (
        KX108DomainStateAudit()
        .status()
    )

    assert (
        status["memory_write"]
        is False
    )

    assert (
        status["kernel_mutation"]
        is False
    )
