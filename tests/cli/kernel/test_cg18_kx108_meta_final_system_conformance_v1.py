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


def test_complete_meta_pipeline():

    result = meta_state()

    assert (
        result["coordination_status"]
        ==
        "COMPLETED"
    )

    audit = (
        KX108MetaDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )


def test_meta_groups_preserved():

    data = receipt()

    assert (
        data["aggregate_count"]
        ==
        3
    )

    assert (
        len(data["aggregates"])
        ==
        3
    )


def test_canonical_meta_state_exists():

    data = receipt()

    assert (
        data["canonical_meta_state"]
        is not None
    )


def test_authority_separation():

    data = receipt()

    assert (
        data["decision_authority"]
        is False
    )

    audit = (
        KX108MetaDomainAudit()
        .audit(
            data
        )
    )

    assert (
        audit["checks"]["decision_authority_blocked"]
        is True
    )


def test_final_kernel_integrity():

    coordination = (
        KX108MetaDomainCoordinationBoundary()
        .status()
    )

    audit = (
        KX108MetaDomainAudit()
        .status()
    )

    assert (
        coordination["memory_write"]
        is False
    )

    assert (
        coordination["kernel_mutation"]
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
