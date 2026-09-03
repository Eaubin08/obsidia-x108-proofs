from scripts.kernel.kx108_proof_execution_runtime_v1 import (
    KX108ProofExecutionRuntime,
)

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id":
            "runtime-cg73",

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
        mission_id="mission-cg73",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def test_execution_runtime_validated():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert (
        result["execution_runtime_status"]
        == "VALIDATED"
    )


def test_execution_runtime_has_runtime_ref():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert result["runtime_ref"] == "runtime-cg73"


def test_unsealed_execution_rejected():

    candidate = flow_output()

    candidate[
        "execution"
    ][
        "envelope"
    ][
        "status"
    ] = "CREATED"

    result = (
        KX108ProofExecutionRuntime()
        .validate(candidate)
    )

    assert result["execution_runtime_status"] == "REJECTED"


def test_execution_authority_escalation_rejected():

    candidate = flow_output()

    candidate[
        "execution"
    ][
        "envelope"
    ][
        "execution_authority"
    ] = True

    result = (
        KX108ProofExecutionRuntime()
        .validate(candidate)
    )

    assert result["execution_runtime_status"] == "REJECTED"


def test_execution_runtime_creates_no_authority():

    result = (
        KX108ProofExecutionRuntime()
        .validate(flow_output())
    )

    assert result["runtime_authority"] is False
    assert result["execution_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
