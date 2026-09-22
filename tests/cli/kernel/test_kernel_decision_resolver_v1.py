from scripts.kernel.kernel_decision_resolver_v1 import (
    KernelDecisionResolver,
)


def valid_gate():

    return {
        "gate_status": "OPEN_FOR_DECISION",
    }


def test_resolution_ready():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        valid_gate()
    )

    assert result["resolver_status"] == "RESOLUTION_READY"


def test_candidate_only():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        valid_gate()
    )

    assert (
        result["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_no_act():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        valid_gate()
    )

    assert result["act"] is False


def test_closed_gate_rejected():

    resolver = KernelDecisionResolver()

    result = resolver.resolve(
        {
            "gate_status": "CLOSED",
        }
    )

    assert result["resolver_status"] == "REJECTED"


def test_kernel_authority_boundary():

    status = KernelDecisionResolver().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
