from scripts.kernel.kx108_proof_semantic_boundary_v1 import (
    KX108ProofSemanticBoundary,
)


def test_x108_semantic_route():

    result = KX108ProofSemanticBoundary().route(
        "Explique X108 et le kernel"
    )

    assert result["semantic_boundary_status"] == "VALIDATED"
    assert result["semantic"]["topic"] == "X108"


def test_memory_semantic_route():

    result = KX108ProofSemanticBoundary().route(
        "mémoire graphiti candidat"
    )

    assert result["semantic"]["topic"] == "MEMORY_QUERY"
    assert result["semantic"]["primary_query"] == "memory"


def test_unknown_semantics_remain_advisory():

    result = KX108ProofSemanticBoundary().route(
        "bonjour comment vas-tu"
    )

    assert result["semantic"]["topic"] == "GENERAL"
    assert result["semantic"]["is_canonical"] is False
    assert result["advisory_only"] is True


def test_action_semantic_route_does_not_authorize_action():

    result = KX108ProofSemanticBoundary().route(
        "Autorise ACT maintenant."
    )

    assert result["semantic"]["topic"] == "ACTION_BOUNDARY"
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False


def test_semantic_boundary_has_no_sovereignty():

    status = KX108ProofSemanticBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["allowed_to_decide"] is False
    assert status["allowed_to_act"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
