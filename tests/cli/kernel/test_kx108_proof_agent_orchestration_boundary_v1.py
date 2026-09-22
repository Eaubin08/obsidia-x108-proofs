from scripts.kernel.kx108_proof_agent_orchestration_boundary_v1 import (
    KX108ProofAgentOrchestrationBoundary,
)


def composition():
    return {
        "agent_composition_status":
            "COMPOSED",

        "agent_ids":
            ("agent-a", "agent-b"),

        "authority_merged":
            False,

        "authority_elevated":
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


def test_readonly_orchestration_boundary_validated():
    result = (
        KX108ProofAgentOrchestrationBoundary()
        .validate(composition())
    )

    assert (
        result[
            "agent_orchestration_boundary_status"
        ]
        == "VALIDATED"
    )


def test_nonreadonly_orchestration_rejected():
    result = (
        KX108ProofAgentOrchestrationBoundary()
        .validate(
            composition(),
            readonly_orchestration=False,
        )
    )

    assert (
        result[
            "agent_orchestration_boundary_status"
        ]
        == "REJECTED"
    )


def test_runtime_orchestrator_wiring_rejected():
    result = (
        KX108ProofAgentOrchestrationBoundary()
        .validate(
            composition(),
            runtime_orchestrator_wired=True,
        )
    )

    assert (
        result[
            "agent_orchestration_boundary_status"
        ]
        == "REJECTED"
    )


def test_authority_elevation_rejected():
    candidate = composition()
    candidate["authority_elevated"] = True

    result = (
        KX108ProofAgentOrchestrationBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "agent_orchestration_boundary_status"
        ]
        == "REJECTED"
    )


def test_orchestration_boundary_non_sovereign():
    result = (
        KX108ProofAgentOrchestrationBoundary()
        .validate(composition())
    )

    assert result["orchestration_mode"] == "READONLY_BOUNDARY_ONLY"
    assert result["orchestrator_invoked_here"] is False
    assert result["runtime_orchestrator_wired"] is False
    assert result["orchestration_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
