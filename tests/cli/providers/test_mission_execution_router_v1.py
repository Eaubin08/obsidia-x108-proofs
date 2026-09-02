from scripts.providers.mission_execution_router_v1 import (
    MissionExecutionRouter,
)


def fake_provider(**kwargs):

    return {
        "provider": "brody",
        "runtime": "ok",
    }


def test_provider_registration():

    router = MissionExecutionRouter()

    router.register_provider(
        "brody",
        fake_provider,
    )

    assert "brody" in router.routes


def test_execution_routing():

    router = MissionExecutionRouter()

    router.register_provider(
        "brody",
        fake_provider,
    )

    output = router.execute(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["result"]["provider"] == "brody"


def test_session_created():

    router = MissionExecutionRouter()

    router.register_provider(
        "brody",
        fake_provider,
    )

    output = router.execute(
        mission_id="mission-002",
        provider_id="brody",
        capability="analysis",
        payload={},
    )

    assert output["session"]["status"] == "COMPLETED"


def test_authority_boundary():

    status = MissionExecutionRouter().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_isolated():

    router = MissionExecutionRouter()

    router.register_provider(
        "brody",
        fake_provider,
    )

    assert len(router.routes) == 1
