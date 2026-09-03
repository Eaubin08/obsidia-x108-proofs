from scripts.kernel.kx108_proof_mission_runtime_v1 import (
    KX108ProofMissionRuntime,
)

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id":
            "runtime-cg81",

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
        mission_id="mission-cg81",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def mission_authority():

    return {
        "status":
            "BOUND",

        "mission_id":
            "mission-cg81",

        "issuer":
            "HUMAN",

        "authority":
            "NON_SOVEREIGN",

        "is_kx_authority":
            False,

        "plan_is_execution_authority":
            False,

        "runtime_authority_active":
            False,
    }


def test_mission_runtime_validated():

    result = (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            mission_authority(),
        )
    )

    assert (
        result["mission_runtime_status"]
        == "VALIDATED"
    )

    assert result["mission_id"] == "mission-cg81"


def test_mission_identity_is_closed():

    result = (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            mission_authority(),
        )
    )

    assert (
        result["checks"]["mission_identity_closed"]
        is True
    )


def test_mission_identity_drift_rejected():

    candidate = mission_authority()

    candidate[
        "mission_id"
    ] = "wrong-mission"

    result = (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            candidate,
        )
    )

    assert result["mission_runtime_status"] == "REJECTED"


def test_kx_authority_escalation_rejected():

    candidate = mission_authority()

    candidate[
        "is_kx_authority"
    ] = True

    result = (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            candidate,
        )
    )

    assert result["mission_runtime_status"] == "REJECTED"


def test_mission_runtime_remains_non_sovereign():

    result = (
        KX108ProofMissionRuntime()
        .validate(
            flow_output(),
            mission_authority(),
        )
    )

    assert result["runtime_authority_active"] is False
    assert result["mission_authority"] is False
    assert result["runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
