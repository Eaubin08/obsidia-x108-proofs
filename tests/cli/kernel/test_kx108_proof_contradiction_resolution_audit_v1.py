from scripts.kernel.kx108_proof_contradiction_resolution_audit_v1 import (
    KX108ProofContradictionResolutionAudit,
)


def test_audit():

    result = (
        KX108ProofContradictionResolutionAudit()
        .audit(
            {

            "resolution_id":
                "kx108-proof-contradiction-resolution-v1",

            "resolution_status":
                "RESOLVED",

            "propagation_blocked":
                True,

            "authority":
                False,

            "kernel_mutation":
                False,

            }
        )
    )


    assert (
        result["audit_status"]
        ==
        "PASSED"
    )


def test_fail():

    result = (
        KX108ProofContradictionResolutionAudit()
        .audit({})
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_checks():

    result = (
        KX108ProofContradictionResolutionAudit()
        .audit({})
    )

    assert (
        "checks"
        in result
    )


def test_safe():

    result = (
        KX108ProofContradictionResolutionAudit()
        .audit({})
    )

    assert "authority_disabled" in result["checks"]
    assert result["checks"]["authority_disabled"] is False


def test_closed():

    result = (
        KX108ProofContradictionResolutionAudit()
        .audit({})
    )

    assert isinstance(result["checks"], dict)
    assert all(result["checks"].values()) is False
