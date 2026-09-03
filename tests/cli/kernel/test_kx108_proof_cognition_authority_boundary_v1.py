from scripts.kernel.kx108_proof_cognition_authority_boundary_v1 import (
    KX108ProofCognitionAuthorityBoundary,
)


def test_cognition_becomes_advisory_context():

    result = (
        KX108ProofCognitionAuthorityBoundary()
        .evaluate(
            {
                "signal": "cg60-cognition",
            }
        )
    )

    assert (
        result[
            "cognition_authority_boundary_status"
        ]
        == "VALIDATED"
    )

    assert result["source"] == "cognitive"


def test_cognition_cannot_decide():

    result = (
        KX108ProofCognitionAuthorityBoundary()
        .evaluate(
            {
                "signal": "decision proposal",
            }
        )
    )

    assert result["checks"]["cognition_cannot_decide"] is True
    assert result["authorizes_decision"] is False


def test_cognition_cannot_act():

    result = (
        KX108ProofCognitionAuthorityBoundary()
        .evaluate(
            {
                "signal": "action proposal",
            }
        )
    )

    assert result["checks"]["no_act"] is True
    assert result["authorizes_act"] is False


def test_non_dict_cognition_rejected():

    result = (
        KX108ProofCognitionAuthorityBoundary()
        .evaluate("invalid")
    )

    assert (
        result[
            "cognition_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_cognition_authority_non_sovereign():

    status = (
        KX108ProofCognitionAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["cognition_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
