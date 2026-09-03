from scripts.kernel.kx108_proof_decision_model_boundary_v1 import (
    KX108ProofDecisionModelBoundary,
)


def guard(status="GUARD_PASSED"):

    return {
        "provider_id": "brody",
        "runtime_id": "runtime-cg44-001",
        "status": status,
    }


def test_decision_model_is_candidate_only():

    result = KX108ProofDecisionModelBoundary().validate(
        guard()
    )

    assert (
        result["decision_model_boundary_status"]
        == "VALIDATED"
    )

    assert (
        result["decision_model"]["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_blocked_guard_does_not_become_act():

    result = KX108ProofDecisionModelBoundary().validate(
        guard("GUARD_BLOCKED")
    )

    assert (
        result["decision_model"]["decision_status"]
        == "CANDIDATE_ONLY"
    )

    assert result["emits_act"] is False


def test_missing_provider_rejected():

    candidate = guard()
    candidate.pop("provider_id")

    result = KX108ProofDecisionModelBoundary().validate(
        candidate
    )

    assert (
        result["decision_model_boundary_status"]
        == "REJECTED"
    )


def test_unknown_guard_status_rejected():

    candidate = guard()
    candidate.pop("status")

    result = KX108ProofDecisionModelBoundary().validate(
        candidate
    )

    assert result["checks"]["guard_status_known"] is False


def test_decision_model_has_no_authority():

    status = KX108ProofDecisionModelBoundary().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
