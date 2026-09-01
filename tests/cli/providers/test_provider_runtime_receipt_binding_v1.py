import pytest

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
    ProviderRuntimeReceiptBindingError,
)


def build_binding():

    return ProviderRuntimeReceiptBinding(
        runtime_execution_id="runtime-001",
        invocation_id="invocation-001",
        result_ref="result-001",
    )


def test_initial_invariants():

    binding = build_binding()

    assert binding.bound is False
    assert binding.decision_authority is False
    assert binding.execution_authority is False
    assert binding.memory_write is False
    assert binding.kernel_mutation is False
    assert binding.emits_act is False


def test_bind_runtime_to_result():

    binding = build_binding()

    assert binding.bind() is True
    assert binding.bound is True


def test_missing_runtime_blocked():

    binding = ProviderRuntimeReceiptBinding(
        runtime_execution_id="",
        invocation_id="invocation-001",
        result_ref="result-001",
    )

    with pytest.raises(ProviderRuntimeReceiptBindingError):

        binding.bind()


def test_missing_result_blocked():

    binding = ProviderRuntimeReceiptBinding(
        runtime_execution_id="runtime-001",
        invocation_id="invocation-001",
        result_ref="",
    )

    with pytest.raises(ProviderRuntimeReceiptBindingError):

        binding.bind()


def test_to_dict_contains_trace():

    binding = build_binding()

    data = binding.to_dict()

    assert data["runtime_execution_id"] == "runtime-001"
    assert data["invocation_id"] == "invocation-001"
    assert data["result_ref"] == "result-001"
