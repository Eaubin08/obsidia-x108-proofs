from scripts.kernel.kx108_proof_agent_decision_flow_v1 import (
    KX108ProofAgentDecisionFlow,
)


def boundary():
    return {
        "agent_orchestration_boundary_status":
            "VALIDATED",

        "orchestrator_invoked_here":
            False,

        "orchestration_authority":
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


def test_agent_decision_flow_boundary_validated():
    result = (
        KX108ProofAgentDecisionFlow()
        .validate(boundary())
    )

    assert (
        result["agent_decision_flow_status"]
        == "BOUNDARY_VALIDATED"
    )


def test_allow_context_only_is_valid_x108_observation():
    result = (
        KX108ProofAgentDecisionFlow()
        .validate(
            boundary(),
            observed_x108_decision="ALLOW_CONTEXT_ONLY",
        )
    )

    assert (
        result["agent_decision_flow_status"]
        == "BOUNDARY_VALIDATED"
    )


def test_hold_and_block_are_valid_x108_observations():
    validator = KX108ProofAgentDecisionFlow()

    hold = validator.validate(
        boundary(),
        observed_x108_decision="HOLD",
    )

    block = validator.validate(
        boundary(),
        observed_x108_decision="BLOCK",
    )

    assert hold["agent_decision_flow_status"] == "BOUNDARY_VALIDATED"
    assert block["agent_decision_flow_status"] == "BOUNDARY_VALIDATED"


def test_fake_direct_agent_allow_rejected():
    result = (
        KX108ProofAgentDecisionFlow()
        .validate(
            boundary(),
            observed_x108_decision="ALLOW",
        )
    )

    assert result["agent_decision_flow_status"] == "REJECTED"


def test_agent_never_becomes_decision_authority():
    result = (
        KX108ProofAgentDecisionFlow()
        .validate(boundary())
    )

    assert result["direct_agent_decision_flow"] is False
    assert result["agent_decision_created"] is False
    assert result["context_packet_created_here"] is False
    assert result["x108_submitted_here"] is False
    assert result["requires_canonical_context_adapter"] is True
    assert result["decision_flow_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
