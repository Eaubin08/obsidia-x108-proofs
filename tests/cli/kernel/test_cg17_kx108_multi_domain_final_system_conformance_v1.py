from scripts.kernel.kx108_multi_domain_aggregation_boundary_v1 import (
    KX108MultiDomainAggregationBoundary,
)

from scripts.kernel.kx108_canonical_domain_state_receipt_v1 import (
    KX108CanonicalDomainStateReceiptBuilder,
)

from scripts.kernel.kx108_multi_domain_audit_v1 import (
    KX108MultiDomainAudit,
)


def domains():

    return [
        {
            "domain": "GPS",
            "state_hash": "gps-final-001",
        },
        {
            "domain": "VISION",
            "state_hash": "vision-final-001",
        },
        {
            "domain": "IMU",
            "state_hash": "imu-final-001",
        },
    ]


def aggregated():

    return (
        KX108MultiDomainAggregationBoundary()
        .aggregate(
            domains()
        )
    )


def receipt():

    return (
        KX108CanonicalDomainStateReceiptBuilder()
        .create(
            aggregated()
        )
        .to_dict()
    )


def test_complete_multi_domain_chain():

    result = aggregated()

    assert (
        result["aggregation_status"]
        ==
        "COMPLETED"
    )

    audit = (
        KX108MultiDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )


def test_domain_sources_preserved():

    data = receipt()

    assert (
        data["domain_count"]
        ==
        3
    )

    assert (
        len(data["domains"])
        ==
        3
    )


def test_canonical_state_exists():

    data = receipt()

    assert (
        data["canonical_state"]
        is not None
    )


def test_audit_proof():

    result = (
        KX108MultiDomainAudit()
        .audit(
            receipt()
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


def test_kernel_final_integrity():

    aggregation = (
        KX108MultiDomainAggregationBoundary()
        .status()
    )

    audit = (
        KX108MultiDomainAudit()
        .status()
    )

    assert (
        aggregation["memory_write"]
        is False
    )

    assert (
        aggregation["kernel_mutation"]
        is False
    )

    assert (
        audit["memory_write"]
        is False
    )

    assert (
        audit["kernel_mutation"]
        is False
    )
