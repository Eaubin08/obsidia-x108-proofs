from scripts.kernel.kx108_domain_adaptation_boundary_v1 import (
    KX108DomainAdaptationBoundary,
)

from scripts.kernel.kx108_domain_state_receipt_v1 import (
    KX108DomainStateReceiptBuilder,
)

from scripts.kernel.kx108_domain_state_audit_v1 import (
    KX108DomainStateAudit,
)


def domain_state():

    return {
        "domain": "GPS",
        "state_hash": "gps-state-global-001",
        "confidence": 0.97,
        "provenance": "gnss-adapter",
    }


def build_receipt():

    return (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
        .to_dict()
    )


def test_full_domain_chain():

    boundary = (
        KX108DomainAdaptationBoundary()
    )

    result = (
        boundary.accept_domain_state(
            domain_state()
        )
    )

    assert (
        result["domain_status"]
        == "ACCEPTED"
    )

    receipt = build_receipt()

    audit = (
        KX108DomainStateAudit()
        .audit(
            receipt
        )
    )

    assert (
        audit["audit_status"]
        == "PASSED"
    )


def test_domain_boundary_binding():

    result = (
        KX108DomainAdaptationBoundary()
        .translate_domain(
            domain_state()
        )
    )

    assert (
        result["translation_status"]
        == "COMPLETED"
    )


def test_receipt_domain_integrity():

    receipt = build_receipt()

    assert (
        receipt["domain"]
        == "GPS"
    )

    assert (
        receipt["state_hash"]
        == "gps-state-global-001"
    )


def test_audit_confidence_and_provenance():

    result = (
        KX108DomainStateAudit()
        .audit(
            build_receipt()
        )
    )

    assert (
        result["checks"]["confidence_valid"]
        is True
    )

    assert (
        result["checks"]["provenance_present"]
        is True
    )


def test_final_kernel_integrity():

    boundary = (
        KX108DomainAdaptationBoundary()
        .status()
    )

    audit = (
        KX108DomainStateAudit()
        .status()
    )

    assert (
        boundary["memory_write"]
        is False
    )

    assert (
        boundary["kernel_mutation"]
        is False
    )

    assert (
        audit["kernel_mutation"]
        is False
    )
