from scripts.kernel.kx108_proof_decision_boundary_v1 import (
    KX108ProofDecisionBoundary,
)


def guard_result():

    return {
        "provider_id": "brody",
        "runtime_id": "runtime-cg35-001",
        "status": "GUARD_PASSED",
    }


def test_decision_candidate_validated():

    result = KX108ProofDecisionBoundary().validate(
        guard_result()
    )

    assert result["decision_boundary_status"] == "VALIDATED"


def test_decision_stays_candidate_only():

    result = KX108ProofDecisionBoundary().validate(
        guard_result()
    )

    assert (
        result["envelope"]["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_failed_guard_rejected():

    candidate = guard_result()
    candidate["status"] = "GUARD_BLOCKED"

    result = KX108ProofDecisionBoundary().validate(
        candidate
    )

    assert result["decision_boundary_status"] == "REJECTED"
    assert result["checks"]["guard_passed"] is False


def test_decision_receipt_traces_candidate():

    result = KX108ProofDecisionBoundary().validate(
        guard_result()
    )

    assert (
        result["receipt"]["source_envelope"]
        == "KX108_DECISION_ENVELOPE"
    )

    assert (
        result["receipt"]["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_decision_boundary_has_no_authority():

    status = KX108ProofDecisionBoundary().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
