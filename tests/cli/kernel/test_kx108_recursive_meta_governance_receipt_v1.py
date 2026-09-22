from scripts.kernel.kx108_recursive_meta_governance_receipt_v1 import (
    KX108RecursiveMetaGovernanceReceiptBuilder,
)


def governance_state():

    return {

        "canonical_governance_state":
            {

                "states":

                    [

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

                    ],

                "conflicts":
                    [],

            }
    }


def test_receipt_creation():

    receipt = (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
    )

    assert (
        receipt.receipt_id
        ==
        "kx108-recursive-meta-governance-receipt-v1"
    )


def test_governance_state_count():

    receipt = (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
    )

    assert (
        receipt.governance_state_count
        ==
        3
    )


def test_conflict_preservation():

    receipt = (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
    )

    assert (
        receipt.conflicts
        ==
        []
    )


def test_authority_isolation():

    receipt = (
        KX108RecursiveMetaGovernanceReceiptBuilder()
        .create(
            governance_state()
        )
    )

    assert (
        receipt.governance_authority
        is False
    )

    assert (
        receipt.decision_authority
        is False
    )


def test_kernel_integrity():

    status = (
        KX108RecursiveMetaGovernanceReceiptBuilder()
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
