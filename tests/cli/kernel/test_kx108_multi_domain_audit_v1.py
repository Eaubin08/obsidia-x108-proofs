from scripts.kernel.kx108_multi_domain_audit_v1 import (
    KX108MultiDomainAudit,
)


def receipt():

    return {

        "receipt_id":
            "kx108-canonical-domain-state-receipt-v1",

        "domain_count":
            3,

        "domains":
            [
                {
                    "domain": "GPS"
                },
                {
                    "domain": "VISION"
                },
                {
                    "domain": "IMU"
                },
            ],

        "canonical_state":
            {
                "status":
                    "aggregated"
            },

        "provenance":
            "multi-domain-aggregation",

        "kernel_mutation":
            False,
    }


def test_audit_passes():

    result = (
        KX108MultiDomainAudit()
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
        KX108MultiDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["receipt_valid"]
        is True
    )


def test_domain_validation():

    result = (
        KX108MultiDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["domains_present"]
        is True
    )


def test_provenance_validation():

    result = (
        KX108MultiDomainAudit()
        .audit(
            receipt()
        )
    )

    assert (
        result["checks"]["provenance_valid"]
        is True
    )


def test_kernel_integrity():

    status = (
        KX108MultiDomainAudit()
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
