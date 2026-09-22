from scripts.kernel.kx108_proof_kx108_release_preparation_v1 import (
    KX108ProofReleasePreparation,
)


def safe():
    return {
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "production_ready": False,
        "release_ready": False,
        "deployment_ready": False,
        "final_freeze": False,
    }


def surfaces():
    e2e = safe()
    e2e.update({
        "kx108_end_to_end_validation_status":
            "PROOF_E2E_VALIDATED",

        "runtime_globally_validated":
            False,

        "runtime_end_to_end_validated":
            False,
    })

    security = safe()
    security[
        "kx108_security_audit_status"
    ] = "PROOF_SECURITY_SURFACES_AUDITED"

    proof_release = safe()
    proof_release.update({
        "release_candidate_status":
            "PROOF_PACK_RELEASE_CANDIDATE",

        "proof_pack_release_candidate":
            True,

        "release_review_allowed":
            True,
    })

    provider_release = safe()
    provider_release.update({
        "provider_release_runtime_status":
            "PROVIDER_RELEASE_CANDIDATE",

        "provider_release_candidate":
            True,

        "release_review_allowed":
            True,
    })

    agent_release = safe()
    agent_release.update({
        "agent_release_status":
            "AGENT_RELEASE_CANDIDATE",

        "agent_release_candidate":
            True,

        "release_review_allowed":
            True,
    })

    return (
        e2e,
        security,
        proof_release,
        provider_release,
        agent_release,
    )


def test_proof_release_review_prepared():
    result = (
        KX108ProofReleasePreparation()
        .validate(
            *surfaces()
        )
    )

    assert (
        result[
            "kx108_release_preparation_status"
        ]
        == "PROOF_RELEASE_REVIEW_PREPARED"
    )

    assert result["proof_release_review_prepared"] is True
    assert result["release_review_allowed"] is True


def test_release_preparation_does_not_authorize_release():
    result = (
        KX108ProofReleasePreparation()
        .validate(
            *surfaces()
        )
    )

    assert result["release_authorized"] is False
    assert result["runtime_activation_authorized"] is False
    assert result["release_ready"] is False
    assert result["production_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False


def test_missing_security_audit_rejected():
    values = list(surfaces())

    values[1][
        "kx108_security_audit_status"
    ] = "REJECTED"

    result = (
        KX108ProofReleasePreparation()
        .validate(
            *values
        )
    )

    assert (
        result[
            "kx108_release_preparation_status"
        ]
        == "REJECTED"
    )


def test_false_release_ready_claim_rejected():
    values = list(surfaces())

    values[2][
        "release_ready"
    ] = True

    result = (
        KX108ProofReleasePreparation()
        .validate(
            *values
        )
    )

    assert (
        result[
            "kx108_release_preparation_status"
        ]
        == "REJECTED"
    )


def test_release_preparation_creates_no_authority():
    result = (
        KX108ProofReleasePreparation()
        .validate(
            *surfaces()
        )
    )

    assert result["new_authority_created"] is False
    assert result["release_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
