from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)

from scripts.kernel.kx108_proof_receipt_chain_v1 import (
    KX108ProofReceiptChain,
)

from scripts.kernel.kx108_proof_agent_receipt_closure_v1 import (
    KX108ProofAgentReceiptClosure,
)


def agent_envelope():
    return {
        "agent_canonical_envelope_status":
            "VALIDATED",

        "agent_binding_claimed":
            False,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,

        "canonical_envelope":
            CanonicalDecisionEnvelopeBuilder()
            .build({
                "provider_id":
                    "kx108-gateway",

                "runtime_id":
                    "runtime-cg95",

                "status":
                    "GUARD_PASSED",
            })
            .to_dict(),
    }


def receipt_chain():
    receipt = ProviderRuntimeReceipt(
        provider_id="provider-cg95",
        adapter_id="adapter-cg95",
        invocation_id="invocation-cg95",
        result_ref="runtime-cg95",
    ).to_dict()

    return (
        KX108ProofReceiptChain()
        .validate(
            receipt,
            expected_result_ref="runtime-cg95",
            expected_invocation_id="invocation-cg95",
        )
    )


def test_agent_receipt_closure_validated():
    result = (
        KX108ProofAgentReceiptClosure()
        .validate(
            agent_envelope(),
            receipt_chain(),
        )
    )

    assert (
        result["agent_receipt_closure_status"]
        == "VALIDATED"
    )


def test_receipt_chain_required():
    chain = receipt_chain()
    chain["receipt_chain_status"] = "REJECTED"

    result = (
        KX108ProofAgentReceiptClosure()
        .validate(
            agent_envelope(),
            chain,
        )
    )

    assert (
        result["agent_receipt_closure_status"]
        == "REJECTED"
    )


def test_receipt_authority_claim_rejected():
    chain = receipt_chain()
    chain["receipt_is_authority"] = True

    result = (
        KX108ProofAgentReceiptClosure()
        .validate(
            agent_envelope(),
            chain,
        )
    )

    assert (
        result["agent_receipt_closure_status"]
        == "REJECTED"
    )


def test_fabricated_agent_binding_claim_rejected():
    envelope = agent_envelope()
    envelope["agent_binding_claimed"] = True

    result = (
        KX108ProofAgentReceiptClosure()
        .validate(
            envelope,
            receipt_chain(),
        )
    )

    assert (
        result["agent_receipt_closure_status"]
        == "REJECTED"
    )


def test_receipt_closure_creates_no_agent_receipt_authority():
    result = (
        KX108ProofAgentReceiptClosure()
        .validate(
            agent_envelope(),
            receipt_chain(),
        )
    )

    assert result["agent_receipt_generated_here"] is False
    assert result["agent_receipt_binding_claimed"] is False
    assert result["receipt_is_decision_authority"] is False
    assert result["receipt_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
