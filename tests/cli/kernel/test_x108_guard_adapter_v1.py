from scripts.kernel.x108_guard_adapter_v1 import (
    X108GuardAdapter,
)


def test_guard_accepts_validated_input():

    guard = X108GuardAdapter()

    result = guard.evaluate(
        {
            "status": "VALIDATED"
        }
    )

    assert result.status == "GUARD_PASSED"


def test_guard_creates_candidate_only():

    guard = X108GuardAdapter()

    result = guard.evaluate(
        {
            "status": "VALIDATED"
        }
    )

    assert (
        result.decision_candidate["status"]
        == "CANDIDATE_ONLY"
    )


def test_guard_rejects_invalid_input():

    guard = X108GuardAdapter()

    result = guard.evaluate(
        {
            "status": "REJECTED"
        }
    )

    assert result.status == "GUARD_REJECTED"


def test_no_act_output():

    guard = X108GuardAdapter()

    result = guard.evaluate(
        {
            "status": "VALIDATED"
        }
    )

    assert "act" not in str(
        result.decision_candidate
    ).lower()


def test_kernel_authority_boundary():

    status = X108GuardAdapter().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
