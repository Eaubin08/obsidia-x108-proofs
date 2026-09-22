from scripts.providers.obsidure_runtime_receipt_adapter_v1 import (
    ObsidureRuntimeReceiptAdapter,
)


def test_obsidure_full_runtime_flow():

    adapter = ObsidureRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-e2e-001",
        capability="proof",
        proof_target="theorem",
        payload={
            "input": "test"
        },
    )

    result = output["result"]
    receipt = output["receipt"]

    assert result["provider_id"] == "obsidure"

    assert result["verified"] is True

    assert receipt["provider_id"] == "obsidure"

    assert receipt["invocation_id"] == "mission-e2e-001"

    assert receipt["result_ref"] == result["runtime_id"]


def test_obsidure_proof_exists():

    adapter = ObsidureRuntimeReceiptAdapter()

    output = adapter.execute_with_receipt(
        mission_id="mission-e2e-002",
        capability="proof",
        proof_target="lemma",
        payload={},
    )

    assert output["result"]["proof"]["status"] == "verified"


def test_obsidure_authority_boundary():

    status = ObsidureRuntimeReceiptAdapter().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_obsidure_no_decision():

    output = ObsidureRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="mission-e2e-003",
        capability="proof",
        proof_target="theorem",
        payload={},
    )

    assert "decision" not in output


def test_obsidure_identity():

    adapter = ObsidureRuntimeReceiptAdapter()

    assert adapter.provider_id == "obsidure"
