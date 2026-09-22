from scripts.kernel.kx108_proof_provider_release_runtime_v1 import (
    KX108ProofProviderReleaseRuntime,
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


def release_candidate():

    return {
        "release_candidate_status":
            "PROOF_PACK_RELEASE_CANDIDATE",

        "proof_pack_release_candidate":
            True,

        "release_review_allowed":
            True,

        "runtime_globally_validated":
            False,

        "production_ready":
            False,

        "release_ready":
            False,

        "deployment_ready":
            False,

        "final_freeze":
            False,

        "candidate_authority":
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


def test_provider_becomes_release_review_candidate():

    result = (
        KX108ProofProviderReleaseRuntime()
        .evaluate(
            provider_validation(),
            release_candidate(),
        )
    )

    assert (
        result[
            "provider_release_runtime_status"
        ]
        == "PROVIDER_RELEASE_CANDIDATE"
    )

    assert (
        result["provider_release_candidate"]
        is True
    )


def test_provider_candidate_is_not_release_ready():

    result = (
        KX108ProofProviderReleaseRuntime()
        .evaluate(
            provider_validation(),
            release_candidate(),
        )
    )

    assert result["release_review_allowed"] is True
    assert result["release_ready"] is False
    assert result["production_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False


def test_invalid_provider_rejected():

    candidate = provider_validation()

    candidate[
        "provider_validation_runtime_status"
    ] = "REJECTED"

    result = (
        KX108ProofProviderReleaseRuntime()
        .evaluate(
            candidate,
            release_candidate(),
        )
    )

    assert (
        result[
            "provider_release_runtime_status"
        ]
        == "REJECTED"
    )


def test_false_release_ready_claim_rejected():

    candidate = release_candidate()

    candidate[
        "release_ready"
    ] = True

    result = (
        KX108ProofProviderReleaseRuntime()
        .evaluate(
            provider_validation(),
            candidate,
        )
    )

    assert (
        result[
            "provider_release_runtime_status"
        ]
        == "REJECTED"
    )


def test_provider_release_creates_no_authority():

    result = (
        KX108ProofProviderReleaseRuntime()
        .evaluate(
            provider_validation(),
            release_candidate(),
        )
    )

    assert result["new_authority_created"] is False
    assert result["release_authority"] is False
    assert result["provider_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
