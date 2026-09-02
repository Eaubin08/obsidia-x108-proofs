from scripts.kernel.kx108_recursive_state_audit_v1 import (
    KX108RecursiveStateAudit,
)


def receipt():

    return {

        "receipt_id":
            "kx108-recursive-state-receipt-v1",

        "state_count":
            3,

        "recursive_depth":
            1,

        "meta_states":
            [

                {
                    "domain": "SYSTEM"
                },

                {
                    "domain": "ENVIRONMENT"
                },

                {
                    "domain": "OPERATIONAL"
                },

            ],

        "canonical_recursive_state":
            {
                "status":
                    "validated"
            },

        "provenance":
            "recursive-state-coordination",

        "recursive_authority":
            False,

        "kernel_mutation":
            False,
    }


def test_recursive_audit_passes():

    result = (
        KX108RecursiveStateAudit()
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
        KX108RecursiveStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_state_conservation():

    result = (
        KX108RecursiveStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["state_count_valid"]
        is True
    )


def test_recursive_authority_block():

    result = (
        KX108RecursiveStateAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["recursive_authority_blocked"]
        is True
    )


def test_kernel_integrity():

    status = (
        KX108RecursiveStateAudit()
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
