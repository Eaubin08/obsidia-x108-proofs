from scripts.providers.brody_runtime_receipt_adapter_v1 import (
    BrodyRuntimeReceiptAdapter,
)

from scripts.providers.obsidure_runtime_receipt_adapter_v1 import (
    ObsidureRuntimeReceiptAdapter,
)


def test_brody_and_obsidure_global_execution():

    brody = BrodyRuntimeReceiptAdapter()

    brody_output = brody.execute_with_receipt(
        mission_id="global-brody-001",
        capability="analysis",
        payload={},
    )

    obsidure = ObsidureRuntimeReceiptAdapter()

    obsidure_output = obsidure.execute_with_receipt(
        mission_id="global-obsidure-001",
        capability="proof",
        proof_target="theorem",
        payload={},
    )

    assert brody_output["receipt"]["provider_id"] == "brody"

    assert obsidure_output["receipt"]["provider_id"] == "obsidure"


def test_provider_identity_separation():

    brody = BrodyRuntimeReceiptAdapter()
    obsidure = ObsidureRuntimeReceiptAdapter()

    assert brody.provider_id != obsidure.provider_id


def test_shared_authority_boundary():

    brody_status = BrodyRuntimeReceiptAdapter().status()

    obsidure_status = ObsidureRuntimeReceiptAdapter().status()

    for status in [
        brody_status,
        obsidure_status,
    ]:

        assert status["decision_authority"] is False
        assert status["execution_authority"] is False
        assert status["memory_write"] is False
        assert status["kernel_mutation"] is False
        assert status["emits_act"] is False


def test_no_decision_leakage():

    brody_output = BrodyRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="global-brody-002",
        capability="analysis",
        payload={},
    )

    obsidure_output = ObsidureRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="global-obsidure-002",
        capability="proof",
        proof_target="lemma",
        payload={},
    )

    assert "decision" not in brody_output

    assert "decision" not in obsidure_output


def test_global_runtime_binding():

    brody_output = BrodyRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="global-brody-003",
        capability="analysis",
        payload={},
    )

    obsidure_output = ObsidureRuntimeReceiptAdapter().execute_with_receipt(
        mission_id="global-obsidure-003",
        capability="proof",
        proof_target="theorem",
        payload={},
    )

    assert (
        brody_output["receipt"]["result_ref"]
        == brody_output["result"]["runtime_id"]
    )

    assert (
        obsidure_output["receipt"]["result_ref"]
        == obsidure_output["result"]["runtime_id"]
    )
