import pytest

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
    ProviderRuntimeReceiptError,
)


def build_receipt():

    return ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        invocation_id="invocation-001",
    )


def test_initial_receipt():

    receipt = build_receipt()

    assert receipt.status == "STARTED"
    assert receipt.execution_authority is False
    assert receipt.decision_authority is False
    assert receipt.memory_write is False
    assert receipt.kernel_mutation is False
    assert receipt.emits_act is False


def test_complete_runtime_execution():

    receipt = build_receipt()

    receipt.complete(
        "result-001"
    )

    assert receipt.status == "COMPLETED"
    assert receipt.result_ref == "result-001"
    assert receipt.completed_at != ""


def test_missing_result_blocked():

    receipt = build_receipt()

    with pytest.raises(ProviderRuntimeReceiptError):

        receipt.complete("")


def test_failed_execution():

    receipt = build_receipt()

    receipt.fail()

    assert receipt.status == "FAILED"


def test_to_dict_contains_runtime_trace():

    receipt = build_receipt()

    data = receipt.to_dict()

    assert data["provider_id"] == "brody"
    assert data["adapter_id"] == "brody-runtime-v1"
    assert data["invocation_id"] == "invocation-001"
