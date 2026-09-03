from scripts.kernel.kx108_proof_context_authority_boundary_v1 import (
    KX108ProofContextAuthorityBoundary,
)


def context_packet():

    return {
        "readonly": True,
        "context_signal_only": True,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "kernel_mutation": False,
    }


def test_readonly_context_is_validated():

    result = (
        KX108ProofContextAuthorityBoundary()
        .validate(context_packet())
    )

    assert (
        result[
            "context_authority_boundary_status"
        ]
        == "VALIDATED"
    )


def test_context_acceptance_is_not_authority():

    result = (
        KX108ProofContextAuthorityBoundary()
        .validate(context_packet())
    )

    assert result["context_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_context_decision_escalation_rejected():

    candidate = context_packet()
    candidate["allowed_to_decide"] = True

    result = (
        KX108ProofContextAuthorityBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "context_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_context_write_escalation_rejected():

    candidate = context_packet()
    candidate["memory_write"] = True

    result = (
        KX108ProofContextAuthorityBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "context_authority_boundary_status"
        ]
        == "REJECTED"
    )


def test_context_authority_boundary_non_sovereign():

    status = (
        KX108ProofContextAuthorityBoundary()
        .status()
    )

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["context_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
