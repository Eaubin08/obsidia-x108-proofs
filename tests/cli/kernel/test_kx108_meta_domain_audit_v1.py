from scripts.kernel.kx108_meta_domain_audit_v1 import (
    KX108MetaDomainAudit,
)


def receipt():

    return {

        "receipt_id":
            "kx108-canonical-meta-state-receipt-v1",

        "aggregate_count":
            3,

        "aggregates":
            [
                {
                    "group": "NAVIGATION"
                },
                {
                    "group": "PERCEPTION"
                },
                {
                    "group": "PHYSICAL"
                },
            ],

        "canonical_meta_state":
            {
                "status":
                    "coordinated"
            },

        "provenance":
            "meta-domain-coordination",

        "decision_authority":
            False,

        "kernel_mutation":
            False,
    }


def test_meta_audit_passes():

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


def test_receipt_validation():

    result = (
        KX108MetaDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_aggregate_validation():

    result = (
        KX108MetaDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["aggregates_present"]
        is True
    )


def test_authority_protection():

    result = (
        KX108MetaDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["decision_authority_blocked"]
        is True
    )


def test_kernel_integrity():

    status = (
        KX108MetaDomainAudit()
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
