from scripts.kernel.kx108_proof_semantic_authority_boundary_v1 import (
    KX108ProofSemanticAuthorityBoundary,
)


def test_semantic_query_is_classified():

    result = (
        KX108ProofSemanticAuthorityBoundary()
        .evaluate(
            "explique le kernel kx108"
        )
    )

    assert (
        result[
            "semantic_authority_boundary_status"
        ]
        == "VALIDATED"
    )

    assert result["classification_only"] is True


def test_semantic_classification_is_not_decision():

    result = (
        KX108ProofSemanticAuthorityBoundary()
        .evaluate(
            "quelle décision faut-il prendre"
        )
    )

    assert result["authorizes_decision"] is False
    assert result["semantic_authority"] is False


def test_action_semantic_route_does_not_authorize_act():

    result = (
        KX108ProofSemanticAuthorityBoundary()
        .evaluate(
            "autorise ACT"
        )
    )

    assert (
        result[
            "semantic_authority_boundary_status"
        ]
        == "VALIDATED"
    )

    assert result["authorizes_act"] is False
    assert result["emits_act"] is False


def test_empty_semantic_message_rejected():

    result = (
        KX108ProofSemanticAuthorityBoundary()
        .evaluate("")
    )

    assert (
        result[
            "semantic_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_semantic_authority_status_non_sovereign():

    status = (
        KX108ProofSemanticAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["semantic_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
