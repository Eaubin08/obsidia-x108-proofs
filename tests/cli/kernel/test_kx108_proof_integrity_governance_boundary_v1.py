from types import SimpleNamespace

from periphery.math_core.proof_of_governance import (
    ProofOfGovernanceResult,
)

from scripts.kernel.kx108_proof_integrity_governance_boundary_v1 import (
    KX108ProofIntegrityGovernanceBoundary,
)


def ticket():

    return SimpleNamespace(
        input_hash="input-cg51",
        trace_hash="trace-cg51",
    )


def pog(
    *,
    valid=True,
    stable=True,
    ticket_valid=True,
):

    return ProofOfGovernanceResult(
        action_id="action-cg51",
        pog_valid=valid,
        theta_maps_to_omega=valid,
        lyapunov_stable=stable,
        ticket_valid=ticket_valid,
        reason=(
            "POG_VALID"
            if valid
            else "POG_INVALID"
        ),
    )


def test_integrity_governance_validated():

    result = (
        KX108ProofIntegrityGovernanceBoundary()
        .validate(
            "action-cg51",
            ticket(),
            pog(),
        )
    )

    assert (
        result["integrity_governance_status"]
        == "VALIDATED"
    )


def test_invalid_pog_rejected():

    result = (
        KX108ProofIntegrityGovernanceBoundary()
        .validate(
            "action-cg51",
            ticket(),
            pog(valid=False),
        )
    )

    assert (
        result["integrity_governance_status"]
        == "REJECTED"
    )


def test_unstable_governance_rejected():

    result = (
        KX108ProofIntegrityGovernanceBoundary()
        .validate(
            "action-cg51",
            ticket(),
            pog(stable=False),
        )
    )

    assert result["checks"]["lyapunov_stable"] is False


def test_invalid_ticket_integrity_rejected():

    result = (
        KX108ProofIntegrityGovernanceBoundary()
        .validate(
            "action-cg51",
            ticket(),
            pog(ticket_valid=False),
        )
    )

    assert result["checks"]["ticket_integrity"] is False


def test_integrity_governance_is_attestation_only():

    result = (
        KX108ProofIntegrityGovernanceBoundary()
        .validate(
            "action-cg51",
            ticket(),
            pog(),
        )
    )

    assert (
        result["proof_of_governance"]["runtime_bound"]
        is False
    )

    assert (
        result["proof_of_governance"]["lean_decides"]
        is False
    )

    assert result["authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["emits_act"] is False
