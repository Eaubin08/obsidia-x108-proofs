from scripts.kernel.kx108_canonical_domain_state_receipt_v1 import (
    KX108CanonicalDomainStateReceiptBuilder,
)


def aggregated_state():

    return {
        "domain_count": 3,

        "canonical_domain_state": [

            {
                "domain": "GPS",
                "state_hash": "gps-001",
            },

            {
                "domain": "VISION",
                "state_hash": "vision-001",
            },

            {
                "domain": "IMU",
                "state_hash": "imu-001",
            },
        ],
    }


def test_receipt_creation():

    receipt = (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated_state()
        )
    )

    assert (
        receipt.receipt_id
        ==
        "kx108-canonical-domain-state-receipt-v1"
    )


def test_domain_count():

    receipt = (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated_state()
        )
    )

    assert (
        receipt.domain_count
        == 3
    )


def test_domain_preservation():

    receipt = (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated_state()
        )
    )

    assert (
        len(receipt.domains)
        == 3
    )


def test_provenance():

    receipt = (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated_state()
        )
    )

    assert (
        receipt.provenance
        ==
        "multi-domain-aggregation"
    )


def test_kernel_integrity():

    status = (
        KX108CanonicalDomainStateReceiptBuilder()
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
