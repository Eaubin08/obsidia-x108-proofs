from scripts.providers.mission_sequencer_v1 import (
    MissionSequencer,
)


def test_create_session():

    sequencer = MissionSequencer()

    session = sequencer.create_session(
        "mission-001",
        "brody",
        "analysis",
    )

    assert session.mission_id == "mission-001"


def test_start_mission():

    sequencer = MissionSequencer()

    result = sequencer.start_mission(
        "mission-002",
        "obsidure",
        "proof",
    )

    assert result["status"] == "RUNNING"


def test_session_registry():

    sequencer = MissionSequencer()

    sequencer.create_session(
        "mission-003",
        "brody",
        "analysis",
    )

    assert len(sequencer.sessions) == 1


def test_authority_boundary():

    status = MissionSequencer().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_multiple_sessions():

    sequencer = MissionSequencer()

    first = sequencer.create_session(
        "mission-004",
        "brody",
        "analysis",
    )

    second = sequencer.create_session(
        "mission-005",
        "obsidure",
        "proof",
    )

    assert first.session_id != second.session_id
