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
        "state_hash": "domain-final-state-001",
        "confidence": 0.98,
        "provenance": "gnss-adapter",
    }


def receipt():

    return (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
        .to_dict()
    )


def test_final_domain_chain():

    boundary = (
        KX108DomainAdaptationBoundary()
    )

    accepted = (
        boundary.accept_domain_state(
            domain_state()
        )
    )

    assert (
        accepted["domain_status"]
        == "ACCEPTED"
    )

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


def test_domain_translation():

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


def test_receipt_integrity():

    data = receipt()

    assert data["domain"] == "GPS"
    assert data["state_hash"] == "domain-final-state-001"


def test_audit_integrity():

    result = (
        KX108DomainStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["kernel_protected"]
        is True
    )


def test_kernel_final_protection():

    boundary_status = (
        KX108DomainAdaptationBoundary()
        .status()
    )

    audit_status = (
        KX108DomainStateAudit()
        .status()
    )

    assert boundary_status["memory_write"] is False
    assert boundary_status["kernel_mutation"] is False

    assert audit_status["memory_write"] is False
    assert audit_status["kernel_mutation"] is False
