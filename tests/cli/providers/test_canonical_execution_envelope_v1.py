from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)


def test_envelope_creation():

    envelope = CanonicalExecutionEnvelope(
        mission_id="mission-001",
        provider_id="brody",
        capability="analysis",
        runtime_id="runtime-001",
    )

    data = envelope.to_dict()

    assert data["mission_id"] == "mission-001"
    assert data["provider_id"] == "brody"


def test_envelope_seal():

    envelope = CanonicalExecutionEnvelope(
        mission_id="mission-002",
        provider_id="obsidure",
        capability="proof",
        runtime_id="runtime-002",
    )

    result = envelope.seal()

    assert result["status"] == "SEALED"


def test_runtime_binding():

    envelope = CanonicalExecutionEnvelope(
        mission_id="mission-003",
        provider_id="obsidure",
        capability="proof",
        runtime_id="runtime-003",
    )

    assert envelope.to_dict()["runtime_id"] == "runtime-003"


def test_authority_boundary():

    data = CanonicalExecutionEnvelope(
        mission_id="mission-004",
        provider_id="brody",
        capability="analysis",
        runtime_id="runtime-004",
    ).to_dict()

    assert data["decision_authority"] is False
    assert data["execution_authority"] is False
    assert data["memory_write"] is False
    assert data["kernel_mutation"] is False
    assert data["emits_act"] is False


def test_unique_envelope():

    first = CanonicalExecutionEnvelope(
        mission_id="mission-005",
        provider_id="brody",
        capability="analysis",
        runtime_id="runtime-005",
    )

    second = CanonicalExecutionEnvelope(
        mission_id="mission-006",
        provider_id="obsidure",
        capability="proof",
        runtime_id="runtime-006",
    )

    assert first.envelope_id != second.envelope_id
