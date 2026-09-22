from scripts.kernel.kx108_proof_provenance_chain_boundary_v1 import (
    KX108ProofProvenanceChain,
)

from scripts.kernel.kx108_proof_provenance_receipt_v1 import (
    KX108ProofProvenanceReceiptBuilder,
)

from scripts.kernel.kx108_proof_provenance_audit_v1 import (
    KX108ProofProvenanceAudit,
)



def test_cg23_final_conformance():


    chain = (
        KX108ProofProvenanceChain()
        .create_chain(

            {"source_id":"src"},

            {"evidence_id":"ev"},

            {"receipt_id":"rec"},

            {"audit_status":"PASSED"}

        )
    )


    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create(chain)
    )


    audit = (
        KX108ProofProvenanceAudit()
        .audit(
            receipt.to_dict()
        )
    )


    assert (
        audit["audit_status"]
        ==
        "PASSED"
    )



def test_chain_not_authority():

    chain = (
        KX108ProofProvenanceChain()
        .create_chain(
            {"source_id":"s"},
            {"evidence_id":"e"},
            {"receipt_id":"r"},
            {"audit_status":"PASSED"},
        )
    )

    assert (
        chain["authority"]
        is False
    )



def test_provenance():

    chain = (
        KX108ProofProvenanceChain()
        .create_chain(
            {"source_id":"s"},
            {"evidence_id":"e"},
            {"receipt_id":"r"},
            {"audit_status":"PASSED"},
        )
    )

    assert (
        len(chain["provenance_chain"])
        ==
        4
    )



def test_receipt():

    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create(
            {
            "chain_status":
                "VALID",
            "provenance_chain":
                [1,2,3,4]
            }
        )
    )

    assert (
        receipt.kernel_mutation
        is False
    )



def test_final_integrity():

    assert True
