from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_runtime_authority_boundary_v1 import (
    KX108ProofRuntimeAuthorityBoundary,
)


def packet():

    return cognitive_to_context_packet(
        {
            "signal": "cg56-runtime",
        }
    )


def test_runtime_packet_validated():

    result = (
        KX108ProofRuntimeAuthorityBoundary()
        .validate(packet())
    )

    assert (
        result[
            "runtime_authority_boundary_status"
        ]
        == "VALIDATED"
    )


def test_runtime_allowed_now_is_false():

    result = (
        KX108ProofRuntimeAuthorityBoundary()
        .validate(packet())
    )

    assert (
        result["runtime_allowed_now"]
        is False
    )

    assert result["authorizes_runtime"] is False


def test_runtime_activation_escalation_rejected():

    candidate = packet()
    candidate.runtime_allowed_now = True

    result = (
        KX108ProofRuntimeAuthorityBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "runtime_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_runtime_decision_escalation_rejected():

    candidate = packet()
    candidate.emits_decision = True

    result = (
        KX108ProofRuntimeAuthorityBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "runtime_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_runtime_authority_is_non_sovereign():

    status = (
        KX108ProofRuntimeAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["runtime_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
