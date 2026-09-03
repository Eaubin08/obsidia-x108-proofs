from scripts.kernel.kx108_proof_verification_audit_v1 import (
    KX108ProofVerificationAudit,
)


def test_audit_pass():

    result = (
        KX108ProofVerificationAudit()
        .audit(
            {

            "verification_id":
                "kx108-proof-verification-v1",

            "verification_status":
                "VERIFIED",

            "checks_count":
                4,

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


def test_bad_status():

    result = (
        KX108ProofVerificationAudit()
        .audit({})
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_identity():

    result = (
        KX108ProofVerificationAudit()
        .audit({})
    )

    assert (
        "checks"
        in result
    )


def test_kernel():

    audit = KX108ProofVerificationAudit()

    assert audit.memory_write is False
    assert audit.kernel_mutation is False


def test_closed():

    result = (
        KX108ProofVerificationAudit()
        .audit({})
    )

    assert isinstance(result["checks"], dict)
    assert all(result["checks"].values()) is False
