from types import SimpleNamespace

from periphery.memory.memory_source_registry import (
    get_source,
)

from periphery.memory.memory_source_types import (
    MemoryCandidateStatus,
)

from scripts.kernel.kx108_proof_memory_authority_boundary_v1 import (
    KX108ProofMemoryAuthorityBoundary,
)


def candidate(
    status,
    auto_promotion_allowed=False,
):

    return SimpleNamespace(
        candidate_id="candidate-cg57",
        status=status,
        auto_promotion_allowed=(
            auto_promotion_allowed
        ),
    )


def test_registered_memory_source_is_readonly():

    entry = get_source(
        "brody_runtime"
    )

    result = (
        KX108ProofMemoryAuthorityBoundary()
        .validate_source(entry)
    )

    assert (
        result["memory_source_boundary_status"]
        == "VALIDATED"
    )

    assert result["checks"]["readonly"] is True
    assert result["checks"]["write_forbidden"] is True


def test_promotion_ready_remains_human_review():

    result = (
        KX108ProofMemoryAuthorityBoundary()
        .evaluate_candidate(
            candidate(
                MemoryCandidateStatus.PROMOTION_READY
            )
        )
    )

    assert (
        result["memory_promotion_boundary_status"]
        == "VALIDATED"
    )

    assert (
        result["manual_promotion_eligibility"]
        is True
    )

    assert (
        result["automatic_promotion_authority"]
        is False
    )

    assert (
        result["promotion"][
            "requires_human_review"
        ]
        is True
    )


def test_auto_promotion_invariant_is_blocked():

    result = (
        KX108ProofMemoryAuthorityBoundary()
        .evaluate_candidate(
            candidate(
                MemoryCandidateStatus.PROMOTION_READY,
                auto_promotion_allowed=True,
            )
        )
    )

    assert (
        result["promotion"]["promotion_allowed"]
        is False
    )

    assert (
        result["promotion"]["reason"]
        == "AUTO_PROMOTION_INVARIANT_VIOLATED"
    )


def test_rejected_candidate_cannot_promote():

    result = (
        KX108ProofMemoryAuthorityBoundary()
        .evaluate_candidate(
            candidate(
                MemoryCandidateStatus.REJECTED
            )
        )
    )

    assert (
        result["promotion"]["promotion_allowed"]
        is False
    )


def test_memory_boundary_has_no_authority():

    status = (
        KX108ProofMemoryAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["memory_authority"] is False
    assert status["memory_write"] is False
    assert status["auto_promotion"] is False
    assert status["execution_authority"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
