from scripts.kernel.kx108_proof_receipt_validation_v1 import (
    KX108ProofReceiptValidator,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)


def receipt():

    return ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        invocation_id="mission-cg32",
        result_ref="runtime-cg32-001",
    ).to_dict()


def test_receipt_validated():

    result = KX108ProofReceiptValidator().validate(
        receipt(),
        expected_result_ref="runtime-cg32-001",
        expected_invocation_id="mission-cg32",
    )

    assert result["receipt_validation_status"] == "VALIDATED"


def test_binding_is_real():

    result = KX108ProofReceiptValidator().validate(
        receipt()
    )

    assert result["binding"]["bound"] is True


def test_result_ref_mismatch_rejected():

    result = KX108ProofReceiptValidator().validate(
        receipt(),
        expected_result_ref="wrong-runtime",
    )

    assert result["receipt_validation_status"] == "REJECTED"
    assert result["checks"]["result_ref_matches"] is False


def test_failed_receipt_rejected():

    candidate = receipt()
    candidate["status"] = "FAILED"

    result = KX108ProofReceiptValidator().validate(
        candidate
    )

    assert result["receipt_validation_status"] == "REJECTED"
    assert result["checks"]["status_acceptable"] is False


def test_receipt_validation_has_no_authority():

    status = KX108ProofReceiptValidator().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
