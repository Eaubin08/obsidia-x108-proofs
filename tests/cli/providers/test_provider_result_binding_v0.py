import pytest

from scripts.providers.provider_result_binding_v0 import (
    ProviderResultBinding,
    ProviderResultBindingError,
)


def build_binding():
    return ProviderResultBinding(
        execution_session_id="session-001",
        invocation_id="invocation-001",
        provider_id="brody",
        result_ref="result-001",
    )


def test_initial_state():

    binding = build_binding()

    assert binding.bound is False
    assert binding.execution_authority is False
    assert binding.decision_authority is False
    assert binding.memory_write is False
    assert binding.kernel_mutation is False
    assert binding.emits_act is False


def test_valid_binding():

    binding = build_binding()

    binding.bind()

    assert binding.bound is True


def test_missing_session_blocked():

    binding = ProviderResultBinding(
        execution_session_id="",
        invocation_id="invocation-001",
        provider_id="brody",
        result_ref="result-001",
    )

    with pytest.raises(ProviderResultBindingError):
        binding.bind()


def test_missing_result_blocked():

    binding = ProviderResultBinding(
        execution_session_id="session-001",
        invocation_id="invocation-001",
        provider_id="brody",
        result_ref="",
    )

    with pytest.raises(ProviderResultBindingError):
        binding.bind()


def test_to_dict_contains_binding_state():

    binding = build_binding()

    binding.bind()

    data = binding.to_dict()

    assert data["bound"] is True
    assert data["provider_id"] == "brody"
