from copy import deepcopy

from scripts.kernel.kx108_proof_provider_security_runtime_v1 import (
    KX108ProofProviderSecurityRuntime,
)


def provider_boundary():

    return {
        "provider_boundary_status":
            "VALIDATED",

        "provider_id":
            "brody",

        "provider_authority":
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


def test_provider_security_runtime_validated():

    result = (
        KX108ProofProviderSecurityRuntime()
        .validate(
            provider_boundary(),
            {
                "message":
                    "normal provider result",
            },
        )
    )

    assert (
        result[
            "provider_security_runtime_status"
        ]
        == "VALIDATED"
    )


def test_secret_payload_is_detected_and_processed():

    result = (
        KX108ProofProviderSecurityRuntime()
        .validate(
            provider_boundary(),
            {
                "message":
                    "password=super-secret-value",
            },
        )
    )

    assert (
        result[
            "provider_security_runtime_status"
        ]
        == "VALIDATED"
    )

    assert result["secret_detected"] is True

    assert (
        result["checks"]["security_checks_valid"]
        is True
    )


def test_security_processing_does_not_mutate_input():

    payload = {
        "message":
            "api_key=secret-value-cg78",
    }

    original = deepcopy(payload)

    (
        KX108ProofProviderSecurityRuntime()
        .validate(
            provider_boundary(),
            payload,
        )
    )

    assert payload == original


def test_provider_authority_escalation_rejected():

    candidate = provider_boundary()

    candidate[
        "provider_authority"
    ] = True

    result = (
        KX108ProofProviderSecurityRuntime()
        .validate(
            candidate,
            {
                "message":
                    "normal",
            },
        )
    )

    assert (
        result[
            "provider_security_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_security_runtime_non_sovereign():

    result = (
        KX108ProofProviderSecurityRuntime()
        .validate(
            provider_boundary(),
            {
                "message":
                    "normal",
            },
        )
    )

    assert result["security_authority"] is False
    assert result["provider_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
