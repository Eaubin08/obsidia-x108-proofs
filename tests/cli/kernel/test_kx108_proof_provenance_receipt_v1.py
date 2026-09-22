from scripts.kernel.kx108_proof_provenance_receipt_v1 import (
    KX108ProofProvenanceReceiptBuilder,
)


def test_receipt_creation():

    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create(
            {
                "chain_status":
                    "VALID",

                "provenance_chain":
                    [
                        1,2,3,4
                    ]
            }
        )
    )

    assert (
        receipt.chain_id
        ==
        "kx108-proof-provenance-chain-v1"
    )


def test_depth():

    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create(
            {
                "chain_status":
                    "VALID",

                "provenance_chain":
                    [
                        1,2,3,4
                    ]
            }
        )
    )

    assert (
        receipt.provenance_depth
        ==
        4
    )


def test_authority():

    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create({})
    )

    assert receipt.authority is False


def test_kernel():

    assert (
        KX108ProofProvenanceReceiptBuilder()
        .status()["kernel_mutation"]
        is False
    )


def test_decision():

    receipt = (
        KX108ProofProvenanceReceiptBuilder()
        .create({})
    )

    assert receipt.decision_authority is False
