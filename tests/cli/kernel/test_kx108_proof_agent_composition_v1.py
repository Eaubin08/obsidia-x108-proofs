from scripts.kernel.kx108_proof_agent_composition_v1 import (
    KX108ProofAgentComposition,
)


def runtime(agent_id):
    return {
        "agent_complete_runtime_status":
            "VALIDATED",

        "agent_id":
            agent_id,

        "global_runtime_validated":
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


def test_agent_composition_validated():
    result = KX108ProofAgentComposition().compose([
        runtime("agent-a"),
        runtime("agent-b"),
    ])

    assert result["agent_composition_status"] == "COMPOSED"
    assert result["agent_count"] == 2


def test_empty_composition_rejected():
    result = KX108ProofAgentComposition().compose([])

    assert result["agent_composition_status"] == "REJECTED"


def test_duplicate_identity_rejected():
    result = KX108ProofAgentComposition().compose([
        runtime("agent-a"),
        runtime("agent-a"),
    ])

    assert result["agent_composition_status"] == "REJECTED"


def test_authority_escalation_rejected():
    unsafe = runtime("agent-b")
    unsafe["execution_authority"] = True

    result = KX108ProofAgentComposition().compose([
        runtime("agent-a"),
        unsafe,
    ])

    assert result["agent_composition_status"] == "REJECTED"


def test_composition_does_not_merge_authority():
    result = KX108ProofAgentComposition().compose([
        runtime("agent-a"),
        runtime("agent-b"),
    ])

    assert result["authority_merged"] is False
    assert result["authority_elevated"] is False
    assert result["composition_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
