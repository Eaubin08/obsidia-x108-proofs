from periphery.agent_contracts import (
    AgentLayer,
    AgentResult,
)

from periphery.agent_registry import (
    run_registered_agent,
)

from periphery.common import (
    ActionCandidate,
    PeripheralSignalPacket,
)

from scripts.kernel.kx108_proof_agent_runtime_v1 import (
    KX108ProofAgentRuntime,
)


def action():

    return ActionCandidate(
        action_id="action-cg83",
        domain="CG83_TEST",
        actor_id="tester",
        intent="observe",
        action_type="DRY_RUN",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
    )


def real_result():

    return run_registered_agent(
        "world_action_agent_v4",
        action(),
    )


def test_agent_runtime_validated():

    result = (
        KX108ProofAgentRuntime()
        .validate(
            real_result()
        )
    )

    assert result["agent_runtime_status"] == "VALIDATED"
    assert result["agent_id"] == "world_action_agent_v4"


def test_agent_runtime_requires_agent_provenance():

    packet = PeripheralSignalPacket(
        action_id="action-cg83",
        domain="CG83_TEST",
    )

    candidate = AgentResult(
        agent_id="world_action_agent_v4",
        layer=AgentLayer.WORLD_ACTION,
        packet=packet,
    )

    result = (
        KX108ProofAgentRuntime()
        .validate(candidate)
    )

    assert result["agent_runtime_status"] == "REJECTED"


def test_unknown_agent_rejected():

    packet = PeripheralSignalPacket(
        action_id="action-cg83",
        domain="CG83_TEST",
    )

    packet.evidence_refs.append(
        "agent:unknown-agent"
    )

    candidate = AgentResult(
        agent_id="unknown-agent",
        layer=AgentLayer.CONTROL,
        packet=packet,
    )

    result = (
        KX108ProofAgentRuntime()
        .validate(candidate)
    )

    assert result["agent_runtime_status"] == "REJECTED"


def test_agent_packet_act_escalation_rejected():

    candidate = real_result()

    candidate.packet.can_emit_act = True

    result = (
        KX108ProofAgentRuntime()
        .validate(candidate)
    )

    assert result["agent_runtime_status"] == "REJECTED"


def test_agent_runtime_does_not_invoke_or_authorize():

    result = (
        KX108ProofAgentRuntime()
        .validate(
            real_result()
        )
    )

    assert result["agent_invoked_here"] is False
    assert result["agent_runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
