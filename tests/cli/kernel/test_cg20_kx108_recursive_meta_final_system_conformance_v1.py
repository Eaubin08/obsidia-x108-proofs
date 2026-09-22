from scripts.kernel.kx108_recursive_meta_governance_boundary_v1 import (
    KX108RecursiveMetaGovernanceBoundary,
)

from scripts.kernel.kx108_recursive_meta_governance_receipt_v1 import (
    KX108RecursiveMetaGovernanceReceiptBuilder,
)

from scripts.kernel.kx108_recursive_meta_governance_audit_v1 import (
    KX108RecursiveMetaGovernanceAudit,
)


def meta_states():

    return [

        {
            "layer": "META_SYSTEM",
            "state": "validated",
        },

        {
            "layer": "META_ENVIRONMENT",
            "state": "validated",
        },

        {
            "layer": "META_OPERATIONAL",
            "state": "validated",
        },

    ]


def governance_state():

    return (
        KX108RecursiveMetaGovernanceBoundary()
        .govern(
            meta_states()
        )
    )


def receipt():

    return (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
        .to_dict()
    )


def test_final_meta_governance_pipeline():

    state = governance_state()

    assert (
        state["governance_status"]
        ==
        "COMPLETED"
    )

    result = (
        KX108RecursiveMetaGovernanceAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["audit_status"]
        ==
        "PASSED"
    )


def test_meta_states_conservation():

    data = receipt()

    assert (
        data["governance_state_count"]
        ==
        3
    )

    assert (
        len(
            data["recursive_meta_states"]
        )
        ==
        3
    )


def test_canonical_governance_integrity():

    data = receipt()

    assert (
        data["canonical_governance_state"]
        is not None
    )

    assert (
        data["provenance"]
        ==
        "recursive-meta-governance"
    )


def test_authority_separation_final():

    data = receipt()

    assert (
        data["governance_authority"]
        is False
    )

    assert (
        data["decision_authority"]
        is False
    )


def test_kernel_protection_final():

    boundary = (
        KX108RecursiveMetaGovernanceBoundary()
        .status()
    )

    audit = (
        KX108RecursiveMetaGovernanceAudit()
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
        audit["memory_write"]
        is False
    )

    assert (
        audit["kernel_mutation"]
        is False
    )
