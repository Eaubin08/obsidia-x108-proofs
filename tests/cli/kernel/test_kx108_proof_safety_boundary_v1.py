from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_safety_boundary_v1 import (
    KX108ProofSafetyBoundary,
)


def packet():

    return cognitive_to_context_packet(
        {
            "signal": "cg49-safety",
        }
    )


def test_safe_bridge_contract_validated():

    result = (
        KX108ProofSafetyBoundary()
        .validate_bridge()
    )

    assert result["safety_bridge_status"] == "VALIDATED"
    assert result["bridge_input"]["readonly"] is True
    assert result["bridge_input"]["emits_act"] is False
    assert result["authorizes_act"] is False


def test_bridge_runtime_activation_fails_closed():

    result = (
        KX108ProofSafetyBoundary()
        .validate_bridge(
            {
                "runtime_active": True,
            }
        )
    )

    assert result["safety_bridge_status"] == "REJECTED"
    assert result["fail_closed"] is True


def test_safe_context_is_context_only():

    result = (
        KX108ProofSafetyBoundary()
        .evaluate_packet(
            packet(),
            critical_action_requested=False,
        )
    )

    assert (
        result["decision"]
        == "ALLOW_CONTEXT_ONLY"
    )

    assert result["authorizes_act"] is False


def test_critical_action_is_held():

    result = (
        KX108ProofSafetyBoundary()
        .evaluate_packet(
            packet(),
            critical_action_requested=True,
        )
    )

    assert result["decision"] == "HOLD"
    assert result["authorizes_act"] is False


def test_boundary_violation_is_blocked():

    candidate = packet()

    candidate.emits_act = True

    result = (
        KX108ProofSafetyBoundary()
        .evaluate_packet(
            candidate,
            critical_action_requested=False,
        )
    )

    assert result["decision"] == "BLOCK"

    assert (
        result["x108_gate_status"]
        == "X108_FAIL_CLOSED"
    )

    assert result["emits_act"] is False
    assert result["authorizes_act"] is False
