from scripts.kernel.kx108_proof_release_candidate_v1 import (
    KX108ProofReleaseCandidate,
)


def global_validation():

    return {
        "global_validation_status":
            "PROOF_PACK_VALIDATED",

        "proof_pack_validated":
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


def test_validated_pack_becomes_release_candidate():

    result = (
        KX108ProofReleaseCandidate()
        .evaluate(global_validation())
    )

    assert (
        result["release_candidate_status"]
        == "PROOF_PACK_RELEASE_CANDIDATE"
    )

    assert (
        result["proof_pack_release_candidate"]
        is True
    )


def test_release_candidate_is_not_release_ready():

    result = (
        KX108ProofReleaseCandidate()
        .evaluate(global_validation())
    )

    assert result["release_review_allowed"] is True
    assert result["release_ready"] is False
    assert result["production_ready"] is False


def test_runtime_validation_claim_rejected():

    candidate = global_validation()

    candidate[
        "runtime_globally_validated"
    ] = True

    result = (
        KX108ProofReleaseCandidate()
        .evaluate(candidate)
    )

    assert result["release_candidate_status"] == "REJECTED"


def test_unvalidated_pack_rejected():

    candidate = global_validation()

    candidate[
        "global_validation_status"
    ] = "REJECTED"

    result = (
        KX108ProofReleaseCandidate()
        .evaluate(candidate)
    )

    assert result["release_candidate_status"] == "REJECTED"


def test_release_candidate_creates_no_authority():

    result = (
        KX108ProofReleaseCandidate()
        .evaluate(global_validation())
    )

    assert result["new_authority_created"] is False
    assert result["candidate_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
