from scripts.kernel.kx108_proof_alignment_boundary_v1 import (
    KX108ProofAlignmentBoundary,
)


def aligned_snapshot():

    return {
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "runtime_active": False,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "allowed_to_decide": False,
    }


def test_aligned_snapshot_validated():

    result = KX108ProofAlignmentBoundary().validate(
        aligned_snapshot()
    )

    assert result["alignment_boundary_status"] == "ALIGNED"


def test_wrong_decision_authority_rejected():

    candidate = aligned_snapshot()
    candidate["decision_authority"] = "BRODY"

    result = KX108ProofAlignmentBoundary().validate(
        candidate
    )

    assert result["alignment_boundary_status"] == "REJECTED"


def test_act_alignment_violation_rejected():

    candidate = aligned_snapshot()
    candidate["emits_act"] = True

    result = KX108ProofAlignmentBoundary().validate(
        candidate
    )

    assert result["alignment_boundary_status"] == "REJECTED"


def test_write_alignment_violation_rejected():

    candidate = aligned_snapshot()
    candidate["memory_write"] = True

    result = KX108ProofAlignmentBoundary().validate(
        candidate
    )

    assert result["alignment_boundary_status"] == "REJECTED"


def test_alignment_does_not_grant_authority():

    status = KX108ProofAlignmentBoundary().status()

    assert status["authority"] is False
    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
