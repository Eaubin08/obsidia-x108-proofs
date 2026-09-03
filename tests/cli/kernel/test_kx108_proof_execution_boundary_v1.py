from scripts.kernel.kx108_proof_execution_boundary_v1 import (
    KX108ProofExecutionBoundary,
)

from scripts.providers.canonical_execution_orchestrator_v1 import (
    CanonicalExecutionOrchestrator,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-cg34-001",
        "provider_id": "brody",
    }


def execution():

    orchestrator = CanonicalExecutionOrchestrator()

    orchestrator.register_provider(
        "brody",
        fake_provider,
    )

    return orchestrator.execute(
        mission_id="mission-cg34",
        provider_id="brody",
        capability="analysis",
        payload={},
    )


def test_execution_boundary_validated():

    result = KX108ProofExecutionBoundary().validate(
        execution()
    )

    assert result["execution_boundary_status"] == "VALIDATED"


def test_execution_runtime_preserved():

    result = KX108ProofExecutionBoundary().validate(
        execution()
    )

    assert result["runtime_ref"] == "runtime-cg34-001"


def test_unsealed_execution_rejected():

    candidate = execution()
    candidate["envelope"]["status"] = "OPEN"

    result = KX108ProofExecutionBoundary().validate(
        candidate
    )

    assert result["execution_boundary_status"] == "REJECTED"
    assert result["checks"]["envelope_sealed"] is False


def test_execution_receipt_created():

    result = KX108ProofExecutionBoundary().validate(
        execution()
    )

    assert (
        result["receipt"]["source_boundary"]
        == "KX108_EXECUTION_BOUNDARY"
    )

    assert result["receipt"]["act"] is False


def test_execution_boundary_has_no_authority():

    status = KX108ProofExecutionBoundary().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
