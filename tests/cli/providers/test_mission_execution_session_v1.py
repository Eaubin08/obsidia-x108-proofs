from scripts.providers.mission_execution_session_v1 import (
    MissionExecutionSession,
)


def test_session_creation():

    session = MissionExecutionSession(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
    )

    data = session.to_dict()

    assert data["mission_id"] == "mission-001"
    assert data["provider_id"] == "brody"


def test_session_start():

    session = MissionExecutionSession(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
    )

    result = session.start()

    assert result["status"] == "RUNNING"


def test_session_complete():

    session = MissionExecutionSession(
        mission_id="mission-001",
        provider_id="obsidure",
        capability="proof",
    )

    result = session.complete()

    assert result["status"] == "COMPLETED"


def test_authority_boundary():

    data = MissionExecutionSession(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
    ).to_dict()

    assert data["decision_authority"] is False
    assert data["execution_authority"] is False
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["emits_act"] is False


def test_session_identity():

    first = MissionExecutionSession(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
    )

    second = MissionExecutionSession(
        mission_id="mission-002",
        provider_id="brody",
        capability="analysis",
    )

    assert first.session_id != second.session_id
