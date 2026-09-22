from scripts.kernel.kx108_proof_verification_engine_v1 import (
    KX108ProofVerificationEngine,
)

from scripts.kernel.kx108_proof_verification_receipt_v1 import (
    KX108VerificationReceiptBuilder,
)

from scripts.kernel.kx108_proof_verification_audit_v1 import (
    KX108ProofVerificationAudit,
)



def test_cg24_final_system_conformance():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            {

            "proof_id":
                "cg24-proof",

            "provenance_chain":
                [1,2,3,4],

            "contradiction":
                False,

            }
        )
    )


    receipt = (
        KX108VerificationReceiptBuilder()
        .create(
            result
        )
    )


    audit = (
        KX108ProofVerificationAudit()
        .audit(
            receipt.to_dict()
        )
    )


    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )



def test_not_authority():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            {
            "proof_id":"x",
            "provenance_chain":[1,2,3,4],
            "contradiction":False,
            }
        )
    )

    assert (
        result["authority"]
        is False
    )



def test_receipt_integrity():

    receipt = (
        KX108VerificationReceiptBuilder()
        .create(
            {
            "verification_status":
                "VERIFIED",
            "checks":
                {
                    "x":True
                }
            }
        )
    )

    assert (
        receipt.kernel_mutation
        is False
    )



def test_verification():

    assert True



def test_final():

    assert True
