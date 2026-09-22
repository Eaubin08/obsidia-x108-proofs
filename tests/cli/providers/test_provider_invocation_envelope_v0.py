import pytest

from scripts.providers.provider_invocation_envelope_v0 import (
    ProviderInvocationEnvelope,
    ProviderInvocationEnvelopeError,
)


def build_envelope():

    return ProviderInvocationEnvelope(
        mission_ref="mission-001",
        provider_id="brody",
        adapter_id="brody-adapter-v0",
        capability="reasoning",
        authorization_ref="receipt-001",
        execution_session_id="session-001",
        input_ref="input-001",
    )


def test_initial_invariants():

    envelope = build_envelope()

    assert envelope.decision_authority is False
    assert envelope.execution_authority is False
    assert envelope.memory_write is False
    assert envelope.kernel_mutation is False
    assert envelope.emits_act is False


def test_valid_envelope():

    envelope = build_envelope()

    assert envelope.validate() is True


def test_missing_provider_blocked():

    envelope = ProviderInvocationEnvelope(
        mission_ref="mission-001",
        provider_id="",
        adapter_id="adapter",
        capability="reasoning",
        authorization_ref="receipt",
        execution_session_id="session",
        input_ref="input",
    )

    with pytest.raises(ProviderInvocationEnvelopeError):
        envelope.validate()


def test_to_dict_contains_refs():

    envelope = build_envelope()

    data = envelope.to_dict()

    assert data["provider_id"] == "brody"
    assert data["authorization_ref"] == "receipt-001"
    assert data["execution_session_id"] == "session-001"


def test_unique_invocation_id():

    first = build_envelope()
    second = build_envelope()

    assert first.invocation_id != second.invocation_id
