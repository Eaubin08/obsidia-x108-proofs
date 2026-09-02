from scripts.kernel.kx108_evidence_proof_boundary_v1 import (
    KX108EvidenceProofBoundary,
)

from scripts.kernel.kx108_evidence_receipt_v1 import (
    KX108EvidenceReceiptBuilder,
)

from scripts.kernel.kx108_evidence_proof_audit_v1 import (
    KX108EvidenceProofAudit,
)



def test_cg22_final_system_conformance():

    validation = {
        "validation_status":
            "VALIDATED"
    }

    evidence = {
        "evidence_id":
            "evidence-cg22-test-v1"
    }


    proof = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            validation,
            evidence,
        )
    )


    receipt = (
        KX108EvidenceReceiptBuilder()
        .create(
            proof,
            evidence,
        )
    )


    audit = (
        KX108EvidenceProofAudit()
        .audit(
            receipt.to_dict()
        )
    )


    assert (
        proof["proof_status"]
        ==
        "PROVEN"
    )

    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )



def test_decision_separation():

    receipt = (
        KX108EvidenceReceiptBuilder()
        .create(
            {
                "proof_status":
                    "PROVEN"
            },
            {
                "evidence_id":
                    "evidence-cg22-test-v1"
            },
        )
    )

    assert (
        receipt.decision_authority
        is False
    )



def test_evidence_identity():

    receipt = (
        KX108EvidenceReceiptBuilder()
        .create(
            {
                "proof_status":
                    "PROVEN"
            },
            {
                "evidence_id":
                    "evidence-cg22-test-v1"
            },
        )
    )

    assert (
        receipt.evidence_id
        ==
        "evidence-cg22-test-v1"
    )



def test_proof_is_not_authority():

    proof = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            {
                "validation_status":
                    "VALIDATED"
            },
            {
                "evidence_id":
                    "evidence-cg22-test-v1"
            },
        )
    )

    assert (
        proof["authority"]
        is False
    )



def test_kernel_final_integrity():

    assert (
        KX108EvidenceProofBoundary()
        .status()["kernel_mutation"]
        is False
    )
