from scripts.kernel.kx108_proof_final_boundary_v1 import (
    KX108ProofFinalBoundary,
)


def governance():

    return {
        "governance_closure_status": "CLOSED",
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def decision():

    return {
        "canonical_decision_boundary_status":
            "VALIDATED",

        "decision_recomputed":
            False,

        "kx108_invoked":
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


def test_proof_final_boundary_closes():

    result = (
        KX108ProofFinalBoundary()
        .close(
            governance(),
            decision(),
        )
    )

    assert (
        result["final_boundary_status"]
        == "PROOF_BOUNDARY_CLOSED"
    )

    assert result["proof_pack_closed"] is True


def test_final_boundary_is_not_runtime_closure():

    result = (
        KX108ProofFinalBoundary()
        .close(
            governance(),
            decision(),
        )
    )

    assert result["runtime_closed"] is False
    assert result["release_ready"] is False
    assert result["final_freeze"] is False


def test_governance_failure_rejects_final_boundary():

    candidate = governance()
    candidate["governance_closure_status"] = "REJECTED"

    result = (
        KX108ProofFinalBoundary()
        .close(
            candidate,
            decision(),
        )
    )

    assert result["final_boundary_status"] == "REJECTED"


def test_decision_failure_rejects_final_boundary():

    candidate = decision()
    candidate[
        "canonical_decision_boundary_status"
    ] = "REJECTED"

    result = (
        KX108ProofFinalBoundary()
        .close(
            governance(),
            candidate,
        )
    )

    assert result["final_boundary_status"] == "REJECTED"


def test_final_boundary_creates_no_authority():

    result = (
        KX108ProofFinalBoundary()
        .close(
            governance(),
            decision(),
        )
    )

    assert result["new_authority_created"] is False
    assert result["final_authority"] is False
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
