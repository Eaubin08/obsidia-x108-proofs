from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.kernel.kx108_proof_receipt_chain_v1 import (
    KX108ProofReceiptChain,
)


def receipt():

    r = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody_runtime",
        invocation_id="mission-cg66",
    )

    r.complete(
        "runtime-result-cg66"
    )

    return r.to_dict()


def test_receipt_chain_validated():

    result = (
        KX108ProofReceiptChain()
        .validate(
            receipt(),
            expected_result_ref="runtime-result-cg66",
            expected_invocation_id="mission-cg66",
        )
    )

    assert result["receipt_chain_status"] == "VALIDATED"


def test_receipt_chain_binds_runtime_identity():

    r = receipt()

    result = (
        KX108ProofReceiptChain()
        .validate(r)
    )

    assert result["checks"]["runtime_identity_bound"] is True
    assert result["checks"]["invocation_identity_bound"] is True
    assert result["checks"]["result_reference_bound"] is True


def test_wrong_result_reference_rejected():

    result = (
        KX108ProofReceiptChain()
        .validate(
            receipt(),
            expected_result_ref="wrong-result",
        )
    )

    assert result["receipt_chain_status"] == "REJECTED"


def test_receipt_authority_escalation_rejected():

    r = receipt()
    r["execution_authority"] = True

    result = (
        KX108ProofReceiptChain()
        .validate(r)
    )

    assert result["receipt_chain_status"] == "REJECTED"


def test_receipt_chain_is_not_authority():

    result = (
        KX108ProofReceiptChain()
        .validate(receipt())
    )

    assert result["receipt_is_authority"] is False
    assert result["authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
