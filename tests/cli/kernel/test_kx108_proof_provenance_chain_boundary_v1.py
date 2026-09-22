from scripts.kernel.kx108_proof_provenance_chain_boundary_v1 import (
    KX108ProofProvenanceChain,
)


def chain():

    return (
        KX108ProofProvenanceChain()
        .create_chain(

            {
                "source_id":
                    "source-cg23-v1"
            },

            {
                "evidence_id":
                    "evidence-cg23-v1"
            },

            {
                "receipt_id":
                    "receipt-cg23-v1"
            },

            {
                "audit_status":
                    "PASSED"
            },

        )
    )


def test_chain_valid():

    assert (
        chain()["chain_status"]
        ==
        "VALID"
    )


def test_chain_depth():

    assert (
        len(chain()["provenance_chain"])
        ==
        4
    )


def test_authority_disabled():

    assert (
        chain()["authority"]
        is False
    )


def test_decision_disabled():

    assert (
        chain()["decision_authority"]
        is False
    )


def test_kernel_safe():

    assert (
        chain()["kernel_mutation"]
        is False
    )
