import pytest

from scripts.providers.provider_reliability_receipt_v1 import (
    ProviderReliabilityReceipt,
)


def build_receipt():

    return ProviderReliabilityReceipt(
        provider_id="brody"
    )


def test_initial_invariants():

    receipt = build_receipt()

    assert receipt.decision_authority is False
    assert receipt.execution_authority is False
    assert receipt.memory_write is False
    assert receipt.kernel_mutation is False
    assert receipt.emits_act is False


def test_record_success_and_failure():

    receipt = build_receipt()

    receipt.record_execution(True)
    receipt.record_execution(False)

    assert receipt.executions_total == 2
    assert receipt.executions_success == 1
    assert receipt.executions_failed == 1


def test_record_health_and_conformance():

    receipt = build_receipt()

    receipt.record_health_event()
    receipt.record_conformance(True)
    receipt.record_conformance(False)

    assert receipt.health_events == 1
    assert receipt.conformance_passes == 1
    assert receipt.conformance_failures == 1


def test_to_dict():

    receipt = build_receipt()

    data = receipt.to_dict()

    assert data["provider_id"] == "brody"
    assert data["status"] == "RECORDED"


def test_no_decision_field():

    receipt = build_receipt()

    data = receipt.to_dict()

    assert "decision" not in data
