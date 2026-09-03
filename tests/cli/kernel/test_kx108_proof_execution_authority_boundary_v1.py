from scripts.kernel.kx108_proof_execution_authority_boundary_v1 import (
    KX108ProofExecutionAuthorityBoundary,
)

from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)

from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.providers.provider_runtime_receipt_binding_v1 import (
    ProviderRuntimeReceiptBinding,
)


def execution_triplet():

    envelope = CanonicalExecutionEnvelope(
        mission_id="mission-cg55",
        provider_id="brody",
        capability="semantic_context",
        runtime_id="runtime-result-cg55",
    )

    envelope.seal()

    receipt = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody-adapter",
        invocation_id="invocation-cg55",
    )

    receipt.complete(
        "runtime-result-cg55"
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

    return envelope, receipt, binding


def test_execution_trace_validated():

    envelope, receipt, binding = (
        execution_triplet()
    )

    result = (
        KX108ProofExecutionAuthorityBoundary()
        .validate(
            envelope,
            receipt,
            binding,
        )
    )

    assert (
        result[
            "execution_authority_boundary_status"
        ]
        == "VALIDATED"
    )


def test_completed_trace_is_not_execution_authority():

    envelope, receipt, binding = (
        execution_triplet()
    )

    result = (
        KX108ProofExecutionAuthorityBoundary()
        .validate(
            envelope,
            receipt,
            binding,
        )
    )

    assert result["authorizes_execution"] is False
    assert result["execution_authority"] is False


def test_envelope_authority_escalation_rejected():

    envelope, receipt, binding = (
        execution_triplet()
    )

    envelope.execution_authority = True

    result = (
        KX108ProofExecutionAuthorityBoundary()
        .validate(
            envelope,
            receipt,
            binding,
        )
    )

    assert (
        result[
            "execution_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_broken_result_binding_rejected():

    envelope, receipt, binding = (
        execution_triplet()
    )

    binding.result_ref = "wrong-result"

    result = (
        KX108ProofExecutionAuthorityBoundary()
        .validate(
            envelope,
            receipt,
            binding,
        )
    )

    assert (
        result[
            "execution_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_execution_boundary_has_no_act():

    status = (
        KX108ProofExecutionAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
