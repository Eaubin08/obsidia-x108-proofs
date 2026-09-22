from scripts.kernel.kx108_proof_action_boundary_v1 import (
    KX108ProofActionBoundary,
)


def blocked_act():

    return {
        "act_status": "ACT_BLOCKED",
        "act": False,
    }


def test_action_trace_validated():

    result = KX108ProofActionBoundary().validate(
        blocked_act()
    )

    assert result["action_boundary_status"] == "VALIDATED"


def test_action_receipt_canonical():

    result = KX108ProofActionBoundary().validate(
        blocked_act()
    )

    assert (
        result["receipt"]["source_boundary"]
        == "KX108_ACT_BOUNDARY"
    )


def test_missing_action_status_rejected():

    result = KX108ProofActionBoundary().validate(
        {
            "act": False,
        }
    )

    assert result["action_boundary_status"] == "REJECTED"
    assert result["checks"]["act_status_present"] is False


def test_action_boundary_never_authorizes_act():

    result = KX108ProofActionBoundary().validate(
        {
            "act_status": "ACT_RECORDED",
            "act": True,
        }
    )

    assert result["act_observed"] is True
    assert result["authorizes_act"] is False
    assert result["act_authority"] is False


def test_action_boundary_kernel_integrity():

    status = KX108ProofActionBoundary().status()

    assert status["act_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
