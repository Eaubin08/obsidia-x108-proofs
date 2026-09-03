from scripts.kernel.kx108_proof_mission_boundary_v1 import (
    KX108ProofMissionBoundary,
)

from scripts.kernel.kx108_proof_mission_runtime_v1 import (
    KX108ProofMissionRuntime,
)

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id":
            "runtime-cg82",

        "provider":
            "brody",
    }


def flow_output():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    return flow.run(
        mission_id="mission-cg82",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def authority():

    return {
        "mission_id":
            "mission-cg82",

        "authority":
            "NON_SOVEREIGN",

        "is_kx_authority":
            False,

        "plan_is_execution_authority":
            False,

        "runtime_authority_active":
            False,
    }


def mission_runtime():

    return (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            authority(),
        )
    )


def test_mission_boundary_validated():

    result = (
        KX108ProofMissionBoundary()
        .validate(
            mission_runtime()
        )
    )

    assert result["mission_boundary_status"] == "VALIDATED"
    assert result["mission_id"] == "mission-cg82"


def test_mission_boundary_requires_non_sovereign_authority():

    candidate = mission_runtime()

    candidate[
        "mission_authority_evidence"
    ][
        "authority"
    ] = "SOVEREIGN"

    result = (
        KX108ProofMissionBoundary()
        .validate(candidate)
    )

    assert result["mission_boundary_status"] == "REJECTED"


def test_mission_boundary_rejects_kx_escalation():

    candidate = mission_runtime()

    candidate[
        "mission_authority_evidence"
    ][
        "is_kx_authority"
    ] = True

    result = (
        KX108ProofMissionBoundary()
        .validate(candidate)
    )

    assert result["mission_boundary_status"] == "REJECTED"


def test_mission_boundary_rejects_runtime_activation():

    candidate = mission_runtime()

    candidate[
        "runtime_authority_active"
    ] = True

    result = (
        KX108ProofMissionBoundary()
        .validate(candidate)
    )

    assert result["mission_boundary_status"] == "REJECTED"


def test_mission_boundary_creates_no_authority():

    result = (
        KX108ProofMissionBoundary()
        .validate(
            mission_runtime()
        )
    )

    assert result["mission_boundary_authority"] is False
    assert result["runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
