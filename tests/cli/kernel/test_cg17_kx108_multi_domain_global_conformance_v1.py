from scripts.kernel.kx108_multi_domain_aggregation_boundary_v1 import (
    KX108MultiDomainAggregationBoundary,
)

from scripts.kernel.kx108_canonical_domain_state_receipt_v1 import (
    KX108CanonicalDomainStateReceiptBuilder,
)

from scripts.kernel.kx108_multi_domain_audit_v1 import (
    KX108MultiDomainAudit,
)


def domain_states():

    return [

        {
            "domain": "GPS",
            "state_hash": "gps-global-001",
        },

        {
            "domain": "VISION",
            "state_hash": "vision-global-001",
        },

        {
            "domain": "IMU",
            "state_hash": "imu-global-001",
        },
    ]


def aggregated_state():

    return (
        KX108MultiDomainAggregationBoundary()
        .aggregate(
            domain_states()
        )
    )


def canonical_receipt():

    return (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated_state()
        )
        .to_dict()
    )


def test_full_multi_domain_chain():

    aggregate = aggregated_state()

    assert (
        aggregate["aggregation_status"]
        ==
        "COMPLETED"
    )

    receipt = canonical_receipt()

    audit = (
        KX108MultiDomainAudit()
        .audit(
            receipt
        )
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )


def test_multi_domain_count():

    receipt = canonical_receipt()

    assert (
        receipt["domain_count"]
        ==
        3
    )


def test_canonical_state_generation():

    receipt = canonical_receipt()

    assert (
        receipt["canonical_state"]
        is not None
    )


def test_multi_domain_audit_integrity():

    result = (
        KX108MultiDomainAudit()
        .audit(
            canonical_receipt()
        )
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )

    assert (
        result["checks"]["provenance_valid"]
        is True
    )


def test_final_kernel_protection():

    aggregation_status = (
        KX108MultiDomainAggregationBoundary()
        .status()
    )

    audit_status = (
        KX108MultiDomainAudit()
        .status()
    )

    assert (
        aggregation_status["memory_write"]
        is False
    )

    assert (
        aggregation_status["kernel_mutation"]
        is False
    )

    assert (
        audit_status["memory_write"]
        is False
    )

    assert (
        audit_status["kernel_mutation"]
        is False
    )
