from scripts.kernel.kernel_decision_gate_v1 import (
    KernelDecisionGate,
)


def valid_audit():

    return {
        "audit_status": "PASSED",
    }


def test_gate_opens_after_audit():

    gate = KernelDecisionGate()

    result = gate.evaluate(
        valid_audit()
    )

    assert result["gate_status"] == "OPEN_FOR_DECISION"


def test_candidate_verified():

    gate = KernelDecisionGate()

    result = gate.evaluate(
        valid_audit()
    )

    assert result["candidate_verified"] is True


def test_no_act():

    gate = KernelDecisionGate()

    result = gate.evaluate(
        valid_audit()
    )

    assert result["act"] is False


def test_rejected_audit_closes_gate():

    gate = KernelDecisionGate()

    result = gate.evaluate(
        {
            "audit_status": "FAILED",
        }
    )

    assert result["gate_status"] == "CLOSED"


def test_kernel_authority_boundary():

    status = KernelDecisionGate().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
