from scripts.providers.canonical_execution_orchestrator_v1 import (
    CanonicalExecutionOrchestrator,
)


def fake_provider(**kwargs):

    return {
        "runtime_id": "runtime-001",
        "provider_id": "brody",
    }


def test_execution_creates_envelope():

    orchestrator = CanonicalExecutionOrchestrator()

    orchestrator.register_provider(
        "brody",
        fake_provider,
    )

    output = orchestrator.execute(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["envelope"]["status"] == "SEALED"


def test_envelope_binding():

    orchestrator = CanonicalExecutionOrchestrator()

    orchestrator.register_provider(
        "brody",
        fake_provider,
    )

    output = orchestrator.execute(
        mission_id="mission-002",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["envelope"]["runtime_id"] == "runtime-001"


def test_session_completed():

    orchestrator = CanonicalExecutionOrchestrator()

    orchestrator.register_provider(
        "brody",
        fake_provider,
    )

    output = orchestrator.execute(
        mission_id="mission-003",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["session"]["status"] == "COMPLETED"


def test_authority_boundary():

    status = CanonicalExecutionOrchestrator().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_route():

    orchestrator = CanonicalExecutionOrchestrator()

    orchestrator.register_provider(
        "brody",
        fake_provider,
    )

    assert "brody" in orchestrator.router.routes
