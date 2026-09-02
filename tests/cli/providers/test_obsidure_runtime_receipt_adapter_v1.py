from scripts.providers.obsidure_runtime_receipt_adapter_v1 import (
    ObsidureRuntimeReceiptAdapter,
)


def test_execution_creates_receipt():

    adapter = ObsidureRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-001",
        capability="proof",
        proof_target="theorem",
        payload={}
    )

    assert output["result"]["provider_id"] == "obsidure"
    assert output["receipt"]["provider_id"] == "obsidure"


def test_receipt_links_result():

    adapter = ObsidureRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-002",
        capability="proof",
        proof_target="lemma",
        payload={}
    )

    assert output["receipt"]["result_ref"] == output["result"]["runtime_id"]


def test_authority_boundary():

    status = ObsidureRuntimeReceiptAdapter().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_provider_identity():

    assert ObsidureRuntimeReceiptAdapter().provider_id == "obsidure"


def test_no_decision():

    output = ObsidureRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="mission-003",
        capability="proof",
        proof_target="theorem",
        payload={}
    )

    assert "decision" not in output
