from scripts.kernel.kx108_proof_canonical_authority_boundary_v1 import (
    KX108ProofCanonicalAuthorityBoundary,
)


def test_passed_audit_reaches_canonical_kx108_authority():

    result = (
        KX108ProofCanonicalAuthorityBoundary()
        .validate(
            {
                "audit_status": "PASSED",
            }
        )
    )

    assert (
        result["canonical_authority_status"]
        == "VALIDATED"
    )

    assert (
        result["decision_envelope"]["source_authority"]
        == "KX108"
    )


def test_authority_is_candidate_only_not_decision_payload():

    result = (
        KX108ProofCanonicalAuthorityBoundary()
        .validate(
            {
                "audit_status": "PASSED",
            }
        )
    )

    assert (
        result["authority_result"]["decision"]
        is None
    )

    assert (
        result["authority_result"]["decision_status"]
        == "KX108_DECISION_READY"
    )


def test_failed_audit_rejected():

    result = (
        KX108ProofCanonicalAuthorityBoundary()
        .validate(
            {
                "audit_status": "FAILED",
            }
        )
    )

    assert (
        result["canonical_authority_status"]
        == "REJECTED"
    )


def test_canonical_authority_never_emits_act():

    result = (
        KX108ProofCanonicalAuthorityBoundary()
        .validate(
            {
                "audit_status": "PASSED",
            }
        )
    )

    assert result["checks"]["no_act"] is True
    assert result["emits_act"] is False


def test_canonical_authority_boundary_status():

    status = (
        KX108ProofCanonicalAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
