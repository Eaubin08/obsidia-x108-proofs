from scripts.providers.brody_runtime_receipt_adapter_v1 import (
    BrodyRuntimeReceiptAdapter,
)


def test_execution_creates_receipt():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-001",
        capability="analysis",
        payload={
            "text":"hello"
        },
    )

    assert output["result"]["provider_id"] == "brody"
    assert output["receipt"]["provider_id"] == "brody"


def test_receipt_links_result():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-002",
        capability="analysis",
        payload={}
    )

    assert output["receipt"]["result_ref"] == output["result"]["runtime_id"]


def test_authority_boundary():

    adapter = BrodyRuntimeReceiptAdapter()

    status = adapter.status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_identity():

    adapter = BrodyRuntimeReceiptAdapter()

    assert adapter.provider_id == "brody"


def test_no_decision_output():

    adapter = BrodyRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-003",
        capability="analysis",
        payload={}
    )

    assert "decision" not in output
