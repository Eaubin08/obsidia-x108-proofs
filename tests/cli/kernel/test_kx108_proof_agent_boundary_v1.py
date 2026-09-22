from periphery.agent_contracts import (
    AgentLayer,
    NonSovereignAgentSpec,
)

from periphery.agent_registry import (
    run_registered_agent,
)

from periphery.agents.world_action_agent import (
    SPEC as WORLD_ACTION_SPEC,
)

from periphery.common import (
    ActionCandidate,
)

from scripts.kernel.kx108_proof_agent_boundary_v1 import (
    KX108ProofAgentBoundary,
)

from scripts.kernel.kx108_proof_agent_runtime_v1 import (
    KX108ProofAgentRuntime,
)


def action():

    return ActionCandidate(
        action_id="action-cg84",
        domain="CG84_TEST",
        actor_id="tester",
        intent="observe",
        action_type="DRY_RUN",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
    )


def runtime_result():

    actual = run_registered_agent(
        "world_action_agent_v4",
        action(),
    )

    return (
        KX108ProofAgentRuntime()
        .validate(actual)
    )


def test_agent_boundary_validated():

    result = (
        KX108ProofAgentBoundary()
        .validate(
            runtime_result(),
            WORLD_ACTION_SPEC,
        )
    )

    assert result["agent_boundary_status"] == "VALIDATED"


def test_agent_identity_drift_rejected():

    other_spec = NonSovereignAgentSpec(
        agent_id="other-agent",
        layer=AgentLayer.CONTROL,
        description="test",
    )

    result = (
        KX108ProofAgentBoundary()
        .validate(
            runtime_result(),
            other_spec,
        )
    )

    assert result["agent_boundary_status"] == "REJECTED"


def test_agent_authorization_capability_rejected():

    unsafe_spec = NonSovereignAgentSpec(
        agent_id="world_action_agent_v4",
        layer=AgentLayer.WORLD_ACTION,
        description="unsafe",
        can_authorize=True,
    )

    result = (
        KX108ProofAgentBoundary()
        .validate(
            runtime_result(),
            unsafe_spec,
        )
    )

    assert result["agent_boundary_status"] == "REJECTED"


def test_agent_memory_write_capability_rejected():

    unsafe_spec = NonSovereignAgentSpec(
        agent_id="world_action_agent_v4",
        layer=AgentLayer.WORLD_ACTION,
        description="unsafe",
        can_write_memory=True,
    )

    result = (
        KX108ProofAgentBoundary()
        .validate(
            runtime_result(),
            unsafe_spec,
        )
    )

    assert result["agent_boundary_status"] == "REJECTED"


def test_agent_boundary_non_sovereign():

    result = (
        KX108ProofAgentBoundary()
        .validate(
            runtime_result(),
            WORLD_ACTION_SPEC,
        )
    )

    assert result["agent_authority"] is False
    assert result["agent_can_decide"] is False
    assert result["agent_can_authorize"] is False
    assert result["agent_can_execute_by_authority"] is False
    assert result["agent_can_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
