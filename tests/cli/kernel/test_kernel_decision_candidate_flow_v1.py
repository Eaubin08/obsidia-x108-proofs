from scripts.kernel.kernel_decision_candidate_flow_v1 import (
    KernelDecisionCandidateFlow,
)


def valid_bridge():

    return {
        "status": "VALIDATED",
        "provider_id": "brody",
        "runtime_id": "runtime-001",
    }


def test_candidate_creation():

    flow = KernelDecisionCandidateFlow()

    result = flow.process(
        valid_bridge()
    )

    assert result["status"] == "CANDIDATE_CREATED"


def test_candidate_only():

    flow = KernelDecisionCandidateFlow()

    result = flow.process(
        valid_bridge()
    )

    assert (
        result["candidate"]["decision_status"]
        == "CANDIDATE_ONLY"
    )


def test_rejected_bridge():

    flow = KernelDecisionCandidateFlow()

    result = flow.process(
        {
            "status": "REJECTED",
        }
    )

    assert result["status"] == "REJECTED"


def test_no_act():

    flow = KernelDecisionCandidateFlow()

    result = flow.process(
        valid_bridge()
    )

    assert (
        result["candidate"]["decision_status"]
        != "ACT"
    )


def test_kernel_boundary():

    status = KernelDecisionCandidateFlow().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
