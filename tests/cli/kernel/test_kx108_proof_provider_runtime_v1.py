from scripts.providers.provider_runtime_receipt_v1 import (
    ProviderRuntimeReceipt,
)

from scripts.kernel.kx108_proof_provider_runtime_v1 import (
    KX108ProofProviderRuntime,
)


def canonical_output():

    receipt = ProviderRuntimeReceipt(
        provider_id="brody",
        adapter_id="brody_runtime",
        invocation_id="mission-cg71",
        result_ref="runtime-cg71",
    )

    return {
        "execution": {
            "flow_status": "COMPLETED",

            "execution": {
                "session": {
                    "status": "COMPLETED",
                },

                "envelope": {
                    "provider_id": "brody",
                    "runtime_id": "runtime-cg71",
                    "status": "SEALED",
                    "decision_authority": False,
                    "execution_authority": False,
                    "memory_write": False,
                    "kernel_mutation": False,
                    "emits_act": False,
                },
            },
        },

        "receipt":
            receipt.to_dict(),
    }


def test_provider_runtime_validated():

    result = (
        KX108ProofProviderRuntime()
        .validate(canonical_output())
    )

    assert result["provider_runtime_status"] == "VALIDATED"


def test_provider_runtime_binds_receipt_to_runtime():

    result = (
        KX108ProofProviderRuntime()
        .validate(canonical_output())
    )

    assert (
        result["checks"]["receipt_chain_validated"]
        is True
    )

    assert result["runtime_id"] == "runtime-cg71"


def test_provider_identity_drift_rejected():

    candidate = canonical_output()

    candidate[
        "receipt"
    ]["provider_id"] = "obsidure"

    result = (
        KX108ProofProviderRuntime()
        .validate(candidate)
    )

    assert result["provider_runtime_status"] == "REJECTED"


def test_provider_runtime_authority_escalation_rejected():

    candidate = canonical_output()

    candidate[
        "execution"
    ][
        "execution"
    ][
        "envelope"
    ][
        "execution_authority"
    ] = True

    result = (
        KX108ProofProviderRuntime()
        .validate(candidate)
    )

    assert result["provider_runtime_status"] == "REJECTED"


def test_provider_runtime_does_not_invoke_provider():

    result = (
        KX108ProofProviderRuntime()
        .validate(canonical_output())
    )

    assert result["provider_invoked_here"] is False
    assert result["provider_runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
