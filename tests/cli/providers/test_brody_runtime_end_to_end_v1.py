from scripts.providers.brody_runtime_receipt_adapter_v1 import (
    BrodyRuntimeReceiptAdapter,
)


def test_brody_full_runtime_flow():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-e2e-001",
        capability="analysis",
        payload={
            "input":"hello"
        },
    )

    result = output["result"]
    receipt = output["receipt"]

    assert result["provider_id"] == "brody"

    assert receipt["provider_id"] == "brody"

    assert receipt["invocation_id"] == "mission-e2e-001"

    assert receipt["result_ref"] == result["runtime_id"]


def test_brody_no_decision_authority():

    adapter = BrodyRuntimeReceiptAdapter()

    status = adapter.status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_brody_result_is_not_decision():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-e2e-002",
        capability="analysis",
        payload={},
    )

    assert "decision" not in output


def test_brody_receipt_exists():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-e2e-003",
        capability="analysis",
        payload={},
    )

    assert "receipt" in output


def test_brody_runtime_identity():

    adapter = BrodyRuntimeReceiptAdapter()

    assert adapter.provider_id == "brody"
