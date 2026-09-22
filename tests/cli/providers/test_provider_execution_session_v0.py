import pytest

from scripts.providers.provider_execution_session_v0 import (
    ProviderExecutionSession,
    ProviderExecutionSessionError,
    ExecutionState,
)


def build_session():
    return ProviderExecutionSession(
        mission_submission_id="mission-001",
        authorization_receipt_id="receipt-001",
        provider_id="brody",
        adapter_id="brody-adapter",
        capability="reasoning",
    )


def test_session_created():
    session = build_session()

    assert session.state == ExecutionState.CREATED
    assert session.execution_authority is False
    assert session.memory_write is False
    assert session.emits_act is False
    assert session.kernel_mutation is False


def test_full_execution_lifecycle():
    session = build_session()

    session.authorize()
    assert session.state == ExecutionState.AUTHORIZED

    session.start()
    assert session.state == ExecutionState.RUNNING

    session.complete("result-001")
    assert session.state == ExecutionState.COMPLETED

    session.close()
    assert session.state == ExecutionState.CLOSED


def test_start_without_authorization_blocked():
    session = build_session()

    with pytest.raises(ProviderExecutionSessionError):
        session.start()


def test_close_without_completion_blocked():
    session = build_session()

    session.authorize()
    session.start()

    with pytest.raises(ProviderExecutionSessionError):
        session.close()


def test_closed_session_cannot_restart():
    session = build_session()

    session.authorize()
    session.start()
    session.complete("result-001")
    session.close()

    with pytest.raises(ProviderExecutionSessionError):
        session.start()
