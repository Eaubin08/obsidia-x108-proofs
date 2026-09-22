from scripts.kernel.kx108_proof_agent_governance_v1 import (
    KX108ProofAgentGovernance,
)


def agent_validation():

    return {
        "agent_validation_status":
            "VALIDATED",

        "agent_id":
            "world_action_agent_v4",

        "validation_authority":
            False,

        "agent_authority":
            False,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,
    }


def governance_closure():

    return {
        "governance_closure_status":
            "CLOSED",

        "new_authority_created":
            False,

        "closure_authority":
            False,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,
    }


def test_agent_governance_validated():

    result = (
        KX108ProofAgentGovernance()
        .validate(
            agent_validation(),
            governance_closure(),
        )
    )

    assert result["agent_governance_status"] == "VALIDATED"


def test_governance_closure_required():

    candidate = governance_closure()

    candidate[
        "governance_closure_status"
    ] = "REJECTED"

    result = (
        KX108ProofAgentGovernance()
        .validate(
            agent_validation(),
            candidate,
        )
    )

    assert result["agent_governance_status"] == "REJECTED"


def test_agent_validation_required():

    candidate = agent_validation()

    candidate[
        "agent_validation_status"
    ] = "REJECTED"

    result = (
        KX108ProofAgentGovernance()
        .validate(
            candidate,
            governance_closure(),
        )
    )

    assert result["agent_governance_status"] == "REJECTED"


def test_governance_authority_escalation_rejected():

    candidate = governance_closure()

    candidate[
        "execution_authority"
    ] = True

    result = (
        KX108ProofAgentGovernance()
        .validate(
            agent_validation(),
            candidate,
        )
    )

    assert result["agent_governance_status"] == "REJECTED"


def test_agent_governance_never_decides():

    result = (
        KX108ProofAgentGovernance()
        .validate(
            agent_validation(),
            governance_closure(),
        )
    )

    assert result["agent_can_decide"] is False
    assert result["governance_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
