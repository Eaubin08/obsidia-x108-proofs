from scripts.kernel.kx108_proof_provider_validation_runtime_v1 import (
    KX108ProofProviderValidationRuntime,
)


def provider_runtime():

    return {
        "provider_runtime_status":
            "VALIDATED",

        "provider_id":
            "brody",

        "provider_invoked_here":
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


def provider_binding():

    return {
        "provider_binding_status":
            "VALIDATED",

        "provider_id":
            "brody",

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


def provider_boundary():

    return {
        "provider_boundary_status":
            "VALIDATED",

        "provider_id":
            "brody",

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


def test_provider_validation_runtime_validated():

    result = (
        KX108ProofProviderValidationRuntime()
        .validate(
            provider_runtime(),
            provider_binding(),
            provider_boundary(),
        )
    )

    assert (
        result[
            "provider_validation_runtime_status"
        ]
        == "VALIDATED"
    )


def test_provider_identity_closed():

    result = (
        KX108ProofProviderValidationRuntime()
        .validate(
            provider_runtime(),
            provider_binding(),
            provider_boundary(),
        )
    )

    assert (
        result["checks"]["provider_identity_closed"]
        is True
    )

    assert result["provider_id"] == "brody"


def test_provider_identity_drift_rejected():

    candidate = provider_binding()
    candidate["provider_id"] = "obsidure"

    result = (
        KX108ProofProviderValidationRuntime()
        .validate(
            provider_runtime(),
            candidate,
            provider_boundary(),
        )
    )

    assert (
        result[
            "provider_validation_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_authority_escalation_rejected():

    candidate = provider_boundary()
    candidate["execution_authority"] = True

    result = (
        KX108ProofProviderValidationRuntime()
        .validate(
            provider_runtime(),
            provider_binding(),
            candidate,
        )
    )

    assert (
        result[
            "provider_validation_runtime_status"
        ]
        == "REJECTED"
    )


def test_validation_runtime_does_not_invoke_provider():

    result = (
        KX108ProofProviderValidationRuntime()
        .validate(
            provider_runtime(),
            provider_binding(),
            provider_boundary(),
        )
    )

    assert result["provider_invoked_here"] is False
    assert result["validation_authority"] is False
    assert result["provider_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
