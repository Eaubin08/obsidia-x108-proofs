from scripts.kernel.kx108_multi_domain_aggregation_boundary_v1 import (
    KX108MultiDomainAggregationBoundary,
)


def domains():

    return [
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
    ]


def test_domain_acceptance():

    result = (
        KX108MultiDomainAggregationBoundary()
        .accept_domain_states(
            domains()
        )
    )

    assert (
        result["domains_status"]
        == "ACCEPTED"
    )


def test_domain_count():

    result = (
        KX108MultiDomainAggregationBoundary()
        .aggregate(
            domains()
        )
    )

    assert (
        result["domain_count"]
        == 3
    )


def test_aggregation_completion():

    result = (
        KX108MultiDomainAggregationBoundary()
        .aggregate(
            domains()
        )
    )

    assert (
        result["aggregation_status"]
        == "COMPLETED"
    )


def test_kernel_protection():

    result = (
        KX108MultiDomainAggregationBoundary()
        .aggregate(
            domains()
        )
    )

    assert (
        result["kernel_mutation"]
        is False
    )


def test_final_integrity():

    status = (
        KX108MultiDomainAggregationBoundary()
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
