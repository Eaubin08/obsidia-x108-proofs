from periphery.agent_registry import (
    run_registered_agent,
)

from periphery.agents.world_action_agent import (
    SPEC as WORLD_ACTION_SPEC,
)

from periphery.common import (
    ActionCandidate,
)

from scripts.kernel.kx108_proof_agent_runtime_v1 import (
    KX108ProofAgentRuntime,
)

from scripts.kernel.kx108_proof_agent_boundary_v1 import (
    KX108ProofAgentBoundary,
)

from scripts.kernel.kx108_proof_agent_interface_v1 import (
    KX108ProofAgentInterface,
)


def action():

    return ActionCandidate(
        action_id="action-cg85",
        domain="CG85_TEST",
        actor_id="tester",
        intent="observe",
        action_type="DRY_RUN",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
    )


def actual_result():

    return run_registered_agent(
        "world_action_agent_v4",
        action(),
    )


def boundary(actual):

    runtime = (
        KX108ProofAgentRuntime()
        .validate(actual)
    )

    return (
        KX108ProofAgentBoundary()
        .validate(
            runtime,
            WORLD_ACTION_SPEC,
        )
    )


def test_agent_interface_validated():

    actual = actual_result()

    result = (
        KX108ProofAgentInterface()
        .validate(
            boundary(actual),
            actual,
        )
    )

    assert result["agent_interface_status"] == "VALIDATED"


def test_agent_interface_stays_peripheral():

    actual = actual_result()

    result = (
        KX108ProofAgentInterface()
        .validate(
            boundary(actual),
            actual,
        )
    )

    assert result["interface_mode"] == "PERIPHERAL_SIGNAL_ONLY"
    assert result["requires_context_adapter"] is True


def test_agent_interface_does_not_invent_context_adapter():

    actual = actual_result()

    result = (
        KX108ProofAgentInterface()
        .validate(
            boundary(actual),
            actual,
        )
    )

    assert result["context_adapter_invoked_here"] is False
    assert result["context_packet_created"] is False
    assert result["x108_submitted_here"] is False


def test_agent_interface_rejects_act_capable_packet():

    actual = actual_result()
    current_boundary = boundary(actual)

    actual.packet.can_emit_act = True

    result = (
        KX108ProofAgentInterface()
        .validate(
            current_boundary,
            actual,
        )
    )

    assert result["agent_interface_status"] == "REJECTED"


def test_agent_interface_non_sovereign():

    actual = actual_result()

    result = (
        KX108ProofAgentInterface()
        .validate(
            boundary(actual),
            actual,
        )
    )

    assert result["interface_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
