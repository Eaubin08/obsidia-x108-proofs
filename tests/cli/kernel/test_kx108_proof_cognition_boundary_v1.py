from scripts.kernel.kx108_proof_cognition_boundary_v1 import (
    KX108ProofCognitionBoundary,
)


def test_cognition_becomes_context():

    result = KX108ProofCognitionBoundary().build(
        {
            "signal": "candidate cognition",
        }
    )

    assert result["cognition_boundary_status"] == "VALIDATED"
    assert result["context"]["source"] == "cognitive"


def test_cognition_is_advisory_only():

    result = KX108ProofCognitionBoundary().build(
        {
            "signal": "advisory",
        }
    )

    assert result["checks"]["advisory_only"] is True
    assert result["checks"]["readonly"] is True


def test_cognition_cannot_decide_or_act():

    result = KX108ProofCognitionBoundary().build(
        {
            "signal": "candidate",
        }
    )

    assert result["checks"]["no_decision"] is True
    assert result["checks"]["no_act"] is True


def test_invalid_cognition_rejected():

    result = KX108ProofCognitionBoundary().build(
        "not-a-dict"
    )

    assert result["cognition_boundary_status"] == "REJECTED"


def test_cognition_boundary_has_no_authority():

    status = KX108ProofCognitionBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
