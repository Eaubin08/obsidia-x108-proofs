from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)

from scripts.kernel.kx108_proof_provider_binding_v1 import (
    KX108ProofProviderBinding,
)


def pair():

    receipt = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody_runtime",
        invocation_id="mission-cg67",
    )

    receipt.complete(
        "runtime-result-cg67"
    )

    binding = ProviderRuntimeReceiptBinding(
        runtime_execution_id=(
            receipt.runtime_execution_id
        ),
        invocation_id=(
            receipt.invocation_id
        ),
        result_ref=(
            receipt.result_ref
        ),
    )

    binding.bind()

    return receipt, binding


def test_provider_binding_validated():

    receipt, binding = pair()

    result = (
        KX108ProofProviderBinding()
        .validate(
            receipt,
            binding,
            expected_provider_id="brody",
            expected_adapter_id="brody_runtime",
        )
    )

    assert result["provider_binding_status"] == "VALIDATED"


def test_provider_identity_mismatch_rejected():

    receipt, binding = pair()

    result = (
        KX108ProofProviderBinding()
        .validate(
            receipt,
            binding,
            expected_provider_id="obsidure",
        )
    )

    assert result["provider_binding_status"] == "REJECTED"


def test_invocation_binding_drift_rejected():

    receipt, binding = pair()

    binding.invocation_id = "wrong-invocation"

    result = (
        KX108ProofProviderBinding()
        .validate(
            receipt,
            binding,
        )
    )

    assert result["provider_binding_status"] == "REJECTED"


def test_provider_execution_authority_rejected():

    receipt, binding = pair()

    receipt.execution_authority = True

    result = (
        KX108ProofProviderBinding()
        .validate(
            receipt,
            binding,
        )
    )

    assert result["provider_binding_status"] == "REJECTED"


def test_provider_binding_is_non_sovereign():

    receipt, binding = pair()

    result = (
        KX108ProofProviderBinding()
        .validate(
            receipt,
            binding,
        )
    )

    assert result["provider_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
