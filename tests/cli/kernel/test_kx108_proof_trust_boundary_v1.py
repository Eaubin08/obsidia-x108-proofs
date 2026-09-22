from types import SimpleNamespace

from scripts.kernel.kx108_proof_trust_boundary_v1 import (
    KX108ProofTrustBoundary,
)


def ticket(
    input_hash="input-hash",
    trace_hash="trace-hash",
):

    return SimpleNamespace(
        input_hash=input_hash,
        trace_hash=trace_hash,
    )


def pog(
    lyapunov_stable=True,
    pog_valid=True,
):

    return SimpleNamespace(
        lyapunov_stable=lyapunov_stable,
        pog_valid=pog_valid,
    )


def test_complete_trust_path_is_trusted():

    result = KX108ProofTrustBoundary().validate(
        "action-cg47",
        ticket(),
        pog(),
    )

    assert result["trust_boundary_status"] == "TRUSTED"
    assert result["trust_path"]["is_complete"] is True
    assert result["trust_is_authority"] is False


def test_missing_input_hash_breaks_trust():

    result = KX108ProofTrustBoundary().validate(
        "action-cg47",
        ticket(input_hash=""),
        pog(),
    )

    assert result["trust_boundary_status"] == "REJECTED"
    assert result["broken_at"] == "OS3_INPUT"


def test_missing_trace_hash_breaks_trust():

    result = KX108ProofTrustBoundary().validate(
        "action-cg47",
        ticket(trace_hash=""),
        pog(),
    )

    assert result["trust_boundary_status"] == "REJECTED"
    assert result["broken_at"] == "OS3_TRACE"


def test_unstable_lyapunov_breaks_trust():

    result = KX108ProofTrustBoundary().validate(
        "action-cg47",
        ticket(),
        pog(lyapunov_stable=False),
    )

    assert result["trust_boundary_status"] == "REJECTED"
    assert result["broken_at"] == "LYAPUNOV"


def test_invalid_pog_does_not_grant_authority():

    boundary = KX108ProofTrustBoundary()

    result = boundary.validate(
        "action-cg47",
        ticket(),
        pog(pog_valid=False),
    )

    assert result["trust_boundary_status"] == "REJECTED"
    assert result["broken_at"] == "POG"

    status = boundary.status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
