from scripts.kernel.kx108_meta_domain_coordination_boundary_v1 import (
    KX108MetaDomainCoordinationBoundary,
)

from scripts.kernel.kx108_canonical_meta_state_receipt_v1 import (
    KX108CanonicalMetaStateReceiptBuilder,
)

from scripts.kernel.kx108_meta_domain_audit_v1 import (
    KX108MetaDomainAudit,
)


def aggregates():

    return [

        {
            "group": "NAVIGATION",
            "state": "validated",
        },

        {
            "group": "PERCEPTION",
            "state": "validated",
        },

        {
            "group": "PHYSICAL",
            "state": "validated",
        },

    ]


def meta_state():

    return (
        KX108MetaDomainCoordinationBoundary()
        .coordinate(
            aggregates()
        )
    )


def receipt():

    return (
        KX108CanonicalMetaStateReceiptBuilder()
        .create(
            meta_state()
        )
        .to_dict()
    )


def test_complete_meta_chain():

    coordinated = meta_state()

    assert (
        coordinated["coordination_status"]
        ==
        "COMPLETED"
    )

    result = (
        KX108MetaDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["audit_status"]
        ==
        "PASSED"
    )


def test_meta_aggregate_count():

    data = receipt()

    assert (
        data["aggregate_count"]
        ==
        3
    )


def test_canonical_meta_state_exists():

    data = receipt()

    assert (
        data["canonical_meta_state"]
        is not None
    )


def test_meta_authority_protection():

    data = receipt()

    assert (
        data["decision_authority"]
        is False
    )

    result = (
        KX108MetaDomainAudit()
        .audit(
            data
        )
    )

    assert (
        result["checks"]["decision_authority_blocked"]
        is True
    )


def test_final_kernel_integrity():

    coordination_status = (
        KX108MetaDomainCoordinationBoundary()
        .status()
    )

    audit_status = (
        KX108MetaDomainAudit()
        .status()
    )

    assert (
        coordination_status["memory_write"]
        is False
    )

    assert (
        coordination_status["kernel_mutation"]
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
