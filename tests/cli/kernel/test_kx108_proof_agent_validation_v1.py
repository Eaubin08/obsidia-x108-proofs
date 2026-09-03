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

from scripts.kernel.kx108_proof_agent_validation_v1 import (
    KX108ProofAgentValidation,
)


def action():

    return ActionCandidate(
        action_id="action-cg86",
        domain="CG86_TEST",
        actor_id="tester",
        intent="observe",
        action_type="DRY_RUN",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
    )


def proof_surfaces():

    actual = run_registered_agent(
        "world_action_agent_v4",
        action(),
    )

    runtime = (
        KX108ProofAgentRuntime()
        .validate(actual)
    )

    boundary = (
        KX108ProofAgentBoundary()
        .validate(
            runtime,
            WORLD_ACTION_SPEC,
        )
    )

    interface = (
        KX108ProofAgentInterface()
        .validate(
            boundary,
            actual,
        )
    )

    return runtime, boundary, interface


def test_agent_validation_validated():

    runtime, boundary, interface = proof_surfaces()

    result = (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            boundary,
            interface,
        )
    )

    assert result["agent_validation_status"] == "VALIDATED"
    assert result["agent_id"] == "world_action_agent_v4"


def test_agent_identity_drift_rejected():

    runtime, boundary, interface = proof_surfaces()

    candidate = dict(interface)
    candidate["agent_id"] = "other-agent"

    result = (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            boundary,
            candidate,
        )
    )

    assert result["agent_validation_status"] == "REJECTED"


def test_nonvalidated_boundary_rejected():

    runtime, boundary, interface = proof_surfaces()

    candidate = dict(boundary)

    candidate[
        "agent_boundary_status"
    ] = "REJECTED"

    result = (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            candidate,
            interface,
        )
    )

    assert result["agent_validation_status"] == "REJECTED"


def test_authority_escalation_rejected():

    runtime, boundary, interface = proof_surfaces()

    candidate = dict(interface)

    candidate[
        "execution_authority"
    ] = True

    result = (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            boundary,
            candidate,
        )
    )

    assert result["agent_validation_status"] == "REJECTED"


def test_agent_validation_creates_no_authority():

    runtime, boundary, interface = proof_surfaces()

    result = (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            boundary,
            interface,
        )
    )

    assert result["agent_invoked_here"] is False
    assert result["validation_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
