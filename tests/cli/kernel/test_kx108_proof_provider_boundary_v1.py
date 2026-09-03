from scripts.kernel.kx108_proof_provider_boundary_v1 import (
    KX108ProofProviderBoundary,
)


def runtime():

    return {
        "provider_runtime_status":
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


def binding():

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


def test_provider_boundary_validated():

    result = (
        KX108ProofProviderBoundary()
        .validate(
            runtime(),
            binding(),
        )
    )

    assert result["provider_boundary_status"] == "VALIDATED"


def test_provider_identity_drift_rejected():

    candidate = binding()
    candidate["provider_id"] = "obsidure"

    result = (
        KX108ProofProviderBoundary()
        .validate(
            runtime(),
            candidate,
        )
    )

    assert result["provider_boundary_status"] == "REJECTED"


def test_failed_provider_runtime_rejected():

    candidate = runtime()
    candidate["provider_runtime_status"] = "REJECTED"

    result = (
        KX108ProofProviderBoundary()
        .validate(
            candidate,
            binding(),
        )
    )

    assert result["provider_boundary_status"] == "REJECTED"


def test_provider_authority_escalation_rejected():

    candidate = binding()
    candidate["execution_authority"] = True

    result = (
        KX108ProofProviderBoundary()
        .validate(
            runtime(),
            candidate,
        )
    )

    assert result["provider_boundary_status"] == "REJECTED"


def test_provider_remains_non_sovereign():

    result = (
        KX108ProofProviderBoundary()
        .validate(
            runtime(),
            binding(),
        )
    )

    assert result["provider_authority"] is False
    assert result["provider_can_decide"] is False
    assert result["provider_can_execute_by_authority"] is False
    assert result["provider_can_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False
