from scripts.kernel.kx108_proof_provider_governance_runtime_v1 import (
    KX108ProofProviderGovernanceRuntime,
)


def provider_validation():

    return {
        "provider_validation_runtime_status":
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


def governance_closure():

    return {
        "governance_closure_status":
            "CLOSED",

        "new_authority_created":
            False,

        "closure_authority":
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


def test_provider_governance_runtime_validated():

    result = (
        KX108ProofProviderGovernanceRuntime()
        .validate(
            provider_validation(),
            governance_closure(),
        )
    )

    assert (
        result[
            "provider_governance_runtime_status"
        ]
        == "VALIDATED"
    )


def test_governance_closure_required():

    candidate = governance_closure()

    candidate[
        "governance_closure_status"
    ] = "REJECTED"

    result = (
        KX108ProofProviderGovernanceRuntime()
        .validate(
            provider_validation(),
            candidate,
        )
    )

    assert (
        result[
            "provider_governance_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_validation_required():

    candidate = provider_validation()

    candidate[
        "provider_validation_runtime_status"
    ] = "REJECTED"

    result = (
        KX108ProofProviderGovernanceRuntime()
        .validate(
            candidate,
            governance_closure(),
        )
    )

    assert (
        result[
            "provider_governance_runtime_status"
        ]
        == "REJECTED"
    )


def test_governance_authority_escalation_rejected():

    candidate = governance_closure()

    candidate[
        "execution_authority"
    ] = True

    result = (
        KX108ProofProviderGovernanceRuntime()
        .validate(
            provider_validation(),
            candidate,
        )
    )

    assert (
        result[
            "provider_governance_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_governance_never_decides():

    result = (
        KX108ProofProviderGovernanceRuntime()
        .validate(
            provider_validation(),
            governance_closure(),
        )
    )

    assert result["provider_can_decide"] is False
    assert result["governance_authority"] is False
    assert result["provider_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
