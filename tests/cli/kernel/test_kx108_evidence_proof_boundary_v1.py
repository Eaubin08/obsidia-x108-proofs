from scripts.kernel.kx108_evidence_proof_boundary_v1 import (
    KX108EvidenceProofBoundary,
)


def validation():

    return {
        "validation_status":
            "VALIDATED"
    }


def evidence():

    return {
        "evidence_id":
            "evidence-cg22-test-v1"
    }


def test_valid_evidence():

    result = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            validation(),
            evidence(),
        )
    )

    assert (
        result["proof_status"]
        ==
        "PROVEN"
    )


def test_missing_evidence():

    result = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            validation(),
            {},
        )
    )

    assert (
        result["proof_status"]
        ==
        "UNPROVEN"
    )


def test_invalid_validation():

    result = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            {},
            evidence(),
        )
    )

    assert (
        result["proof_status"]
        ==
        "UNPROVEN"
    )


def test_authority_disabled():

    result = (
        KX108EvidenceProofBoundary()
        .attach_evidence(
            validation(),
            evidence(),
        )
    )

    assert result["authority"] is False


def test_kernel_integrity():

    status = (
        KX108EvidenceProofBoundary()
        .status()
    )

    assert status["kernel_mutation"] is False
