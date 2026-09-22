from copy import deepcopy

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

from scripts.kernel.kx108_proof_agent_security_v1 import (
    KX108ProofAgentSecurity,
)


def action():

    return ActionCandidate(
        action_id="action-cg88",
        domain="CG88_TEST",
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


def validation(actual):

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

    return (
        KX108ProofAgentValidation()
        .validate(
            runtime,
            boundary,
            interface,
        )
    )


def test_agent_security_validated():

    actual = actual_result()

    result = (
        KX108ProofAgentSecurity()
        .validate(
            validation(actual),
            actual,
        )
    )

    assert result["agent_security_status"] == "VALIDATED"


def test_agent_secret_is_detected_and_sanitized():

    actual = actual_result()

    actual.packet.extra_metrics[
        "credential"
    ] = "password=super-secret-value"

    result = (
        KX108ProofAgentSecurity()
        .validate(
            validation(actual),
            actual,
        )
    )

    assert result["agent_security_status"] == "VALIDATED"
    assert result["secret_detected"] is True

    assert (
        result["sanitized_projection"]
        != result["security_projection"]
    )


def test_security_does_not_mutate_agent_packet():

    actual = actual_result()

    actual.packet.extra_metrics[
        "credential"
    ] = "password=super-secret-value"

    original = deepcopy(
        actual.packet.extra_metrics
    )

    (
        KX108ProofAgentSecurity()
        .validate(
            validation(actual),
            actual,
        )
    )

    assert (
        actual.packet.extra_metrics
        == original
    )


def test_act_capable_agent_packet_rejected():

    actual = actual_result()
    valid = validation(actual)

    actual.packet.can_emit_act = True

    result = (
        KX108ProofAgentSecurity()
        .validate(
            valid,
            actual,
        )
    )

    assert result["agent_security_status"] == "REJECTED"


def test_agent_security_creates_no_interface_or_authority():

    actual = actual_result()

    result = (
        KX108ProofAgentSecurity()
        .validate(
            validation(actual),
            actual,
        )
    )

    assert result["agent_invoked_here"] is False
    assert result["context_packet_created"] is False
    assert result["x108_submitted_here"] is False
    assert result["security_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
