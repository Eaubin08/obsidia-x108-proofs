from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
)

from scripts.kernel.kx108_proof_provider_interface_runtime_v1 import (
    KX108ProofProviderInterfaceRuntime,
)


def provider_boundary():

    return {
        "provider_boundary_status":
            "VALIDATED",

        "provider_id":
            "brody",

        "provider_authority":
            False,

        "provider_can_decide":
            False,

        "provider_can_execute_by_authority":
            False,

        "provider_can_act":
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
    }


def packet():

    return cognitive_to_context_packet(
        {
            "signal":
                "cg75-provider-interface-runtime",
        }
    )


def test_provider_interface_runtime_validated():

    result = (
        KX108ProofProviderInterfaceRuntime()
        .validate(
            provider_boundary(),
            packet(),
        )
    )

    assert (
        result[
            "provider_interface_runtime_status"
        ]
        == "VALIDATED"
    )


def test_provider_crosses_as_context_only():

    result = (
        KX108ProofProviderInterfaceRuntime()
        .validate(
            provider_boundary(),
            packet(),
        )
    )

    assert result["checks"]["context_only"] is True

    assert (
        result["kernel_interface"]["x108_decision"]
        == "ALLOW_CONTEXT_ONLY"
    )


def test_missing_provider_identity_rejected():

    candidate = provider_boundary()
    candidate["provider_id"] = ""

    result = (
        KX108ProofProviderInterfaceRuntime()
        .validate(
            candidate,
            packet(),
        )
    )

    assert (
        result[
            "provider_interface_runtime_status"
        ]
        == "REJECTED"
    )


def test_interface_authority_escalation_rejected():

    candidate = packet()
    candidate.decision_authority = "BRODY"

    result = (
        KX108ProofProviderInterfaceRuntime()
        .validate(
            provider_boundary(),
            candidate,
        )
    )

    assert (
        result[
            "provider_interface_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_interface_runtime_non_sovereign():

    result = (
        KX108ProofProviderInterfaceRuntime()
        .validate(
            provider_boundary(),
            packet(),
        )
    )

    assert result["provider_interface_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
