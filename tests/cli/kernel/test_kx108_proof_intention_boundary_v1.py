from scripts.kernel.kx108_proof_intention_boundary_v1 import (
    KX108ProofIntentionBoundary,
)


def test_critical_intention_is_candidate():

    result = KX108ProofIntentionBoundary().build(
        {
            "intent": "inspect",
        }
    )

    assert result["intention_boundary_status"] == "VALIDATED"

    assert (
        result["intent_envelope"]["candidate_only"]
        is True
    )


def test_intention_requires_x108():

    result = KX108ProofIntentionBoundary().build(
        {
            "intent": "inspect",
        }
    )

    assert result["checks"]["requires_x108"] is True

    assert (
        result["intent_envelope"]["authority"]
        == "KX108_ONLY"
    )


def test_critical_intention_is_held():

    result = KX108ProofIntentionBoundary().build(
        {
            "intent": "critical_action",
        },
        action_candidate_type="WORLD_ACTION",
    )

    assert result["decision"]["decision"] == "HOLD"


def test_invalid_intention_input_rejected():

    result = KX108ProofIntentionBoundary().build(
        None
    )

    assert result["intention_boundary_status"] == "REJECTED"


def test_intention_boundary_has_no_authority():

    status = KX108ProofIntentionBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
