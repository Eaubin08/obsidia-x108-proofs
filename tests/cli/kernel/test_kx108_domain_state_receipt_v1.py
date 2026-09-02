from scripts.kernel.kx108_domain_state_receipt_v1 import (
    KX108DomainStateReceiptBuilder,
)


def domain_state():

    return {
        "domain": "GPS",
        "state_hash": "gps-state-001",
        "confidence": 0.95,
        "provenance": "gnss-adapter",
    }


def test_receipt_creation():

    receipt = (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
    )

    assert (
        receipt.receipt_id
        == "kx108-domain-state-receipt-v1"
    )


def test_domain_binding():

    receipt = (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
    )

    assert (
        receipt.domain
        == "GPS"
    )


def test_confidence_tracking():

    receipt = (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
    )

    assert (
        receipt.confidence
        == 0.95
    )


def test_provenance_tracking():

    receipt = (
        KX108DomainStateReceiptBuilder()
        .create(
            domain_state()
        )
    )

    assert (
        receipt.provenance
        == "gnss-adapter"
    )


def test_kernel_integrity():

    status = (
        KX108DomainStateReceiptBuilder()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
