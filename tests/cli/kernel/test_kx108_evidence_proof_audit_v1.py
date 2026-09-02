from scripts.kernel.kx108_evidence_proof_audit_v1 import (
    KX108EvidenceProofAudit,
)


def receipt():

    return {

        "receipt_id":
            "kx108-evidence-proof-receipt-v1",

        "proof_status":
            "PROVEN",

        "evidence_id":
            "evidence-cg22-test-v1",

        "authority":
            False,

        "decision_authority":
            False,

        "kernel_mutation":
            False,

    }


def test_audit_pass():

    result = (
        KX108EvidenceProofAudit()
        .audit(receipt())
    )

    assert (
        result["audit_status"]
        ==
        "PASSED"
    )


def test_bad_receipt():

    data = receipt()

    data["proof_status"] = "UNPROVEN"

    result = (
        KX108EvidenceProofAudit()
        .audit(data)
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_evidence_required():

    data = receipt()

    data["evidence_id"] = None

    result = (
        KX108EvidenceProofAudit()
        .audit(data)
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_authority_disabled():

    result = (
        KX108EvidenceProofAudit()
        .audit(receipt())
    )

    assert (
        result["checks"]["authority_disabled"]
        is True
    )


def test_kernel_safe():

    result = (
        KX108EvidenceProofAudit()
        .audit(receipt())
    )

    assert (
        result["checks"]["kernel_safe"]
        is True
    )
