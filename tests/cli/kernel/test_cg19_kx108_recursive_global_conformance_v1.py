from scripts.kernel.kx108_recursive_state_coordination_boundary_v1 import (
    KX108RecursiveStateCoordinationBoundary,
)

from scripts.kernel.kx108_recursive_state_receipt_v1 import (
    KX108RecursiveStateReceiptBuilder,
)

from scripts.kernel.kx108_recursive_state_audit_v1 import (
    KX108RecursiveStateAudit,
)


def meta_states():

    return [

        {
            "domain": "SYSTEM",
            "state": "validated",
        },

        {
            "domain": "ENVIRONMENT",
            "state": "validated",
        },

        {
            "domain": "OPERATIONAL",
            "state": "validated",
        },

    ]


def recursive_state():

    return (
        KX108RecursiveStateCoordinationBoundary()
        .coordinate(
            meta_states()
        )
    )


def receipt():

    return (
        KX108RecursiveStateReceiptBuilder()
        .create(
            recursive_state()
        )
        .to_dict()
    )


def test_complete_recursive_pipeline():

    state = recursive_state()

    assert (
        state["coordination_status"]
        ==
        "COMPLETED"
    )

    audit = (
        KX108RecursiveStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )


def test_recursive_states_preserved():

    data = receipt()

    assert (
        data["state_count"]
        ==
        3
    )

    assert (
        len(data["meta_states"])
        ==
        3
    )


def test_recursive_state_generated():

    data = receipt()

    assert (
        data["canonical_recursive_state"]
        is not None
    )


def test_recursive_authority_isolated():

    data = receipt()

    assert (
        data["recursive_authority"]
        is False
    )

    result = (
        KX108RecursiveStateAudit()
        .audit(
            data
        )
    )

    assert (
        result["checks"]["recursive_authority_blocked"]
        is True
    )


def test_final_kernel_integrity():

    coordination = (
        KX108RecursiveStateCoordinationBoundary()
        .status()
    )

    audit = (
        KX108RecursiveStateAudit()
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
