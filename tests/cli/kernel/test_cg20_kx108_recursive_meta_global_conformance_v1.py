from scripts.kernel.kx108_recursive_meta_governance_boundary_v1 import (
    KX108RecursiveMetaGovernanceBoundary,
)

from scripts.kernel.kx108_recursive_meta_governance_receipt_v1 import (
    KX108RecursiveMetaGovernanceReceiptBuilder,
)

from scripts.kernel.kx108_recursive_meta_governance_audit_v1 import (
    KX108RecursiveMetaGovernanceAudit,
)


def recursive_meta_states():

    return [

        {
            "layer":
                "META_SYSTEM",

            "state":
                "validated",
        },

        {
            "layer":
                "META_ENVIRONMENT",

            "state":
                "validated",
        },

        {
            "layer":
                "META_OPERATIONAL",

            "state":
                "validated",
        },

    ]


def governance_state():

    return (
        KX108RecursiveMetaGovernanceBoundary()
        .govern(
            recursive_meta_states()
        )
    )


def governance_receipt():

    return (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
        .to_dict()
    )


def test_global_governance_pipeline():

    state = governance_state()

    assert (
        state["governance_status"]
        ==
        "COMPLETED"
    )

    receipt = governance_receipt()

    audit = (
        KX108RecursiveMetaGovernanceAudit()
        .audit(
            receipt
        )
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )


def test_meta_states_preserved():

    receipt = governance_receipt()

    assert (
        receipt["governance_state_count"]
        ==
        3
    )

    assert (
        len(
            receipt["recursive_meta_states"]
        )
        ==
        3
    )


def test_canonical_governance_state():

    receipt = governance_receipt()

    assert (
        receipt["canonical_governance_state"]
        is not None
    )


def test_governance_decision_isolation():

    receipt = governance_receipt()

    assert (
        receipt["governance_authority"]
        is False
    )

    assert (
        receipt["decision_authority"]
        is False
    )


def test_final_kernel_protection():

    boundary_status = (
        KX108RecursiveMetaGovernanceBoundary()
        .status()
    )

    audit_status = (
        KX108RecursiveMetaGovernanceAudit()
        .status()
    )

    assert (
        boundary_status["memory_write"]
        is False
    )

    assert (
        boundary_status["kernel_mutation"]
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
