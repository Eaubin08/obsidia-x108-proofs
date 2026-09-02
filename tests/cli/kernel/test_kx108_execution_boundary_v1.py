from scripts.kernel.kx108_execution_boundary_v1 import (
    KX108ExecutionBoundary,
)


def valid_audit():

    return {
        "audit_status": "PASSED",
    }


def test_execution_authorized():

    result = KX108ExecutionBoundary().authorize(
        valid_audit()
    )

    assert (
        result["execution_status"]
        == "EXECUTION_AUTHORIZED"
    )


def test_failed_audit_blocked():

    result = KX108ExecutionBoundary().authorize(
        {
            "audit_status": "FAILED",
        }
    )

    assert (
        result["execution_status"]
        == "EXECUTION_BLOCKED"
    )


def test_no_act():

    result = KX108ExecutionBoundary().authorize(
        valid_audit()
    )

    assert result["act"] is False


def test_no_decision_mutation():

    result = KX108ExecutionBoundary().authorize(
        valid_audit()
    )

    assert result["decision"] is None


def test_kernel_boundary():

    status = KX108ExecutionBoundary().status()

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
