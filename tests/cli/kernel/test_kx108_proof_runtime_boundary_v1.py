from scripts.kernel.kx108_proof_runtime_boundary_v1 import (
    KX108ProofRuntimeBoundary,
)

from scripts.providers.canonical_execution_flow_v1 import (
    CanonicalExecutionFlow,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-cg37-001",
        "provider": "brody",
    }


def flow_output():

    flow = CanonicalExecutionFlow()

    flow.register_provider(
        "brody",
        fake_provider,
    )

    return flow.run(
        mission_id="mission-cg37",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def test_runtime_boundary_validated():

    result = KX108ProofRuntimeBoundary().validate(
        flow_output()
    )

    assert result["runtime_boundary_status"] == "VALIDATED"


def test_runtime_boundary_ref_preserved():

    result = KX108ProofRuntimeBoundary().validate(
        flow_output()
    )

    assert result["runtime_ref"] == "runtime-cg37-001"


def test_runtime_and_execution_refs_match():

    result = KX108ProofRuntimeBoundary().validate(
        flow_output()
    )

    assert result["checks"]["runtime_refs_match"] is True


def test_tampered_runtime_rejected():

    candidate = flow_output()
    candidate["execution"]["envelope"]["status"] = "OPEN"

    result = KX108ProofRuntimeBoundary().validate(
        candidate
    )

    assert result["runtime_boundary_status"] == "REJECTED"


def test_runtime_boundary_has_no_authority():

    status = KX108ProofRuntimeBoundary().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
