from scripts.kernel.kx108_recursive_meta_governance_audit_v1 import (
    KX108RecursiveMetaGovernanceAudit,
)


def receipt():

    return {

        "receipt_id":
            "kx108-recursive-meta-governance-receipt-v1",

        "governance_state_count":
            3,

        "recursive_meta_states":

            [

                {
                    "layer":
                        "META_SYSTEM"
                },

                {
                    "layer":
                        "META_ENVIRONMENT"
                },

                {
                    "layer":
                        "META_OPERATIONAL"
                },

            ],

        "canonical_governance_state":

            {
                "states":
                    [],
                "conflicts":
                    [],
            },


        "conflicts":
            [],


        "provenance":
            "recursive-meta-governance",


        "governance_authority":
            False,


        "decision_authority":
            False,


        "kernel_mutation":
            False,

    }



def test_governance_audit_passes():

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



def test_receipt_identity():

    result = (
        KX108RecursiveMetaGovernanceAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["receipt_identity_valid"]
        is True
    )



def test_states_preserved():

    result = (
        KX108RecursiveMetaGovernanceAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["states_preserved"]
        is True
    )



def test_authority_disabled():

    result = (
        KX108RecursiveMetaGovernanceAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["governance_authority_disabled"]
        is True
    )

    assert (
        result["checks"]["decision_authority_disabled"]
        is True
    )



def test_kernel_integrity():

    status = (
        KX108RecursiveMetaGovernanceAudit()
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
