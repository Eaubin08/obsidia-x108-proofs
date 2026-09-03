from scripts.kernel.kx108_proof_authority_boundary_v1 import (
    KX108ProofAuthorityBoundary,
)

from scripts.providers.provider_invocation_authorization_receipt_v0 import (
    build_authorization_receipt,
)


def receipt():

    return build_authorization_receipt(
        mission_submission_id="mission-cg46",
        capability_request_ref="capability-cg46",
        provider_id="brody",
        activation_status="AUTHORIZED_FOR_INVOCATION",
        adapter_id="brody-adapter",
    )


def test_authority_receipt_validated():

    result = (
        KX108ProofAuthorityBoundary()
        .validate_receipt(receipt())
    )

    assert (
        result["authority_boundary_status"]
        == "VALIDATED"
    )

    assert result["authority_observed_only"] is True


def test_execution_authority_escalation_rejected():

    candidate = receipt()
    candidate["execution_authority"] = True

    result = (
        KX108ProofAuthorityBoundary()
        .validate_receipt(candidate)
    )

    assert (
        result["authority_boundary_status"]
        == "REJECTED"
    )


def test_kx_authority_escalation_rejected():

    candidate = receipt()
    candidate["kx_authority"] = True

    result = (
        KX108ProofAuthorityBoundary()
        .validate_receipt(candidate)
    )

    assert (
        result["authority_boundary_status"]
        == "REJECTED"
    )


def test_authority_memory_write_rejected():

    candidate = receipt()
    candidate["memory_write"] = True

    result = (
        KX108ProofAuthorityBoundary()
        .validate_receipt(candidate)
    )

    assert (
        result["authority_boundary_status"]
        == "REJECTED"
    )


def test_authority_boundary_is_non_sovereign():

    status = KX108ProofAuthorityBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["kx_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
