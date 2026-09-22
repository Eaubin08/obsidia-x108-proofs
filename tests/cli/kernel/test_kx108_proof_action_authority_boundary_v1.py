from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_action_authority_boundary_v1 import (
    KX108ProofActionAuthorityBoundary,
)


def packet():

    return cognitive_to_context_packet(
        {
            "signal": "cg54-action-candidate",
        }
    )


def test_action_candidate_is_held():

    result = (
        KX108ProofActionAuthorityBoundary()
        .evaluate(packet())
    )

    assert (
        result["action_authority_boundary_status"]
        == "VALIDATED"
    )

    assert result["decision"] == "HOLD"


def test_action_boundary_never_authorizes_act():

    result = (
        KX108ProofActionAuthorityBoundary()
        .evaluate(packet())
    )

    assert result["authorizes_act"] is False
    assert result["emits_act"] is False


def test_emits_act_escalation_is_blocked():

    candidate = packet()
    candidate.emits_act = True

    result = (
        KX108ProofActionAuthorityBoundary()
        .evaluate(candidate)
    )

    assert result["decision"] == "BLOCK"
    assert result["authorizes_act"] is False


def test_missing_packet_rejected():

    result = (
        KX108ProofActionAuthorityBoundary()
        .evaluate(None)
    )

    assert (
        result["action_authority_boundary_status"]
        == "REJECTED"
    )


def test_action_authority_status_is_non_sovereign():

    status = (
        KX108ProofActionAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["action_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
