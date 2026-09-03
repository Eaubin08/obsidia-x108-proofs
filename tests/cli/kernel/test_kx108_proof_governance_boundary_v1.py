from scripts.kernel.kx108_proof_governance_boundary_v1 import (
    KX108ProofGovernanceBoundary,
)

from scripts.providers.provider_invocation_authorization_receipt_v0 import (
    build_authorization_receipt,
)


def receipt():

    return build_authorization_receipt(
        mission_submission_id="mission-cg45",
        capability_request_ref="capability-cg45",
        provider_id="brody",
        activation_status="AUTHORIZED_FOR_INVOCATION",
        adapter_id="brody-adapter",
    )


def test_governance_receipt_validated():

    result = (
        KX108ProofGovernanceBoundary()
        .validate_authorization_receipt(
            receipt()
        )
    )

    assert (
        result["governance_receipt_status"]
        == "VALIDATED"
    )


def test_tampered_governance_receipt_rejected():

    candidate = receipt()
    candidate["kx_authority"] = True

    result = (
        KX108ProofGovernanceBoundary()
        .validate_authorization_receipt(
            candidate
        )
    )

    assert (
        result["governance_receipt_status"]
        == "REJECTED"
    )


def test_context_only_governance():

    result = KX108ProofGovernanceBoundary().evaluate(
        {
            "signal": "context only",
        },
        critical_action_requested=False,
    )

    assert (
        result["decision"]
        == "ALLOW_CONTEXT_ONLY"
    )

    assert result["authorizes_act"] is False


def test_critical_governance_holds():

    result = KX108ProofGovernanceBoundary().evaluate(
        {
            "signal": "critical",
        },
        critical_action_requested=True,
    )

    assert result["decision"] == "HOLD"
    assert result["authorizes_act"] is False


def test_governance_boundary_is_kx108_only():

    status = KX108ProofGovernanceBoundary().status()

    assert (
        status["decision_authority"]
        == "KX108_ONLY"
    )

    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
