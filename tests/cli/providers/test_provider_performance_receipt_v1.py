import pytest

from scripts.providers.provider_performance_receipt_v1 import (
    ProviderPerformanceReceipt,
    ProviderPerformanceReceiptError,
)


def build_receipt():

    return ProviderPerformanceReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        execution_id="execution-001",
    )


def test_initial_invariants():

    receipt = build_receipt()

    assert receipt.decision_authority is False
    assert receipt.execution_authority is False
    assert receipt.memory_write is False
    assert receipt.kernel_mutation is False
    assert receipt.emits_act is False


def test_record_metrics():

    receipt = build_receipt()

    assert receipt.record(
        latency_ms=120.5,
        token_cost=50,
        compute_cost=0.2,
        resource_usage={
            "cpu": "low"
        },
    ) is True

    assert receipt.latency_ms == 120.5
    assert receipt.token_cost == 50
    assert receipt.compute_cost == 0.2


def test_negative_latency_blocked():

    receipt = build_receipt()

    with pytest.raises(ProviderPerformanceReceiptError):

        receipt.record(
            latency_ms=-1,
            token_cost=0,
            compute_cost=0,
            resource_usage={},
        )


def test_negative_cost_blocked():

    receipt = build_receipt()

    with pytest.raises(ProviderPerformanceReceiptError):

        receipt.record(
            latency_ms=1,
            token_cost=-1,
            compute_cost=0,
            resource_usage={},
        )


def test_to_dict_contains_metrics():

    receipt = build_receipt()

    receipt.record(
        latency_ms=10,
        token_cost=5,
        compute_cost=1,
        resource_usage={
            "gpu": "none"
        },
    )

    data = receipt.to_dict()

    assert data["provider_id"] == "brody"
    assert data["latency_ms"] == 10
    assert data["resource_usage"]["gpu"] == "none"
