from scripts.kernel.kx108_evidence_receipt_v1 import (
    KX108EvidenceReceiptBuilder,
)


def test_receipt_creation():

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
        receipt.receipt_id
        ==
        "kx108-evidence-proof-receipt-v1"
    )


def test_evidence_binding():

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


def test_provenance():

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
        receipt.provenance
        ==
        "kx108-evidence-proof"
    )


def test_authority_isolation():

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

    assert receipt.authority is False


def test_kernel_integrity():

    status = (
        KX108EvidenceReceiptBuilder()
        .status()
    )

    assert status["kernel_mutation"] is False
