from scripts.kernel.kx108_proof_runtime_validation_v1 import (
    KX108ProofRuntimeValidator,
)

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-cg31-001",
        "provider": "brody",
    }


def runtime_output():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    return flow.run(
        mission_id="mission-cg31",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def test_runtime_validated():

    result = KX108ProofRuntimeValidator().validate(
        runtime_output()
    )

    assert result["runtime_validation_status"] == "VALIDATED"


def test_runtime_identity_preserved():

    result = KX108ProofRuntimeValidator().validate(
        runtime_output()
    )

    assert result["runtime_ref"] == "runtime-cg31-001"


def test_unsealed_runtime_rejected():

    output = runtime_output()
    output["execution"]["envelope"]["status"] = "OPEN"

    result = KX108ProofRuntimeValidator().validate(
        output
    )

    assert result["runtime_validation_status"] == "REJECTED"
    assert result["checks"]["envelope_sealed"] is False


def test_missing_runtime_identity_rejected():

    output = runtime_output()
    output["execution"]["envelope"]["runtime_id"] = ""

    result = KX108ProofRuntimeValidator().validate(
        output
    )

    assert result["checks"]["runtime_identity"] is False


def test_runtime_validation_has_no_authority():

    status = KX108ProofRuntimeValidator().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
