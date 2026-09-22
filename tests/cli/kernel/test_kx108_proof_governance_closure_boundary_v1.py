from scripts.kernel.kx108_proof_governance_closure_boundary_v1 import (
    KX108ProofGovernanceClosureBoundary,
)


def governance():

    return {
        "governance_boundary_status": "VALIDATED",
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def integrity():

    return {
        "integrity_governance_status": "VALIDATED",
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def canonical():

    return {
        "canonical_authority_status": "VALIDATED",

        "authority_result": {
            "authority_status": "AUTHORIZED_CANDIDATE",
            "decision_status": "KX108_DECISION_READY",
            "decision": None,
            "act": False,
        },

        "decision_envelope": {
            "authority_status": "AUTHORIZED_CANDIDATE",
            "decision_status": "KX108_DECISION_READY",
            "source_authority": "KX108",
            "act": False,
        },

        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def test_governance_proofs_close():

    result = (
        KX108ProofGovernanceClosureBoundary()
        .close(
            governance(),
            integrity(),
            canonical(),
        )
    )

    assert result["governance_closure_status"] == "CLOSED"
    assert result["closed"] is True


def test_closure_creates_no_authority():

    result = (
        KX108ProofGovernanceClosureBoundary()
        .close(
            governance(),
            integrity(),
            canonical(),
        )
    )

    assert result["new_authority_created"] is False
    assert result["closure_authority"] is False


def test_wrong_authority_breaks_closure():

    candidate = governance()
    candidate["decision_authority"] = "BRODY"

    result = (
        KX108ProofGovernanceClosureBoundary()
        .close(
            candidate,
            integrity(),
            canonical(),
        )
    )

    assert result["governance_closure_status"] == "REJECTED"


def test_execution_authority_breaks_closure():

    candidate = integrity()
    candidate["execution_authority"] = True

    result = (
        KX108ProofGovernanceClosureBoundary()
        .close(
            governance(),
            candidate,
            canonical(),
        )
    )

    assert result["governance_closure_status"] == "REJECTED"


def test_closure_does_not_create_decision_or_act():

    result = (
        KX108ProofGovernanceClosureBoundary()
        .close(
            governance(),
            integrity(),
            canonical(),
        )
    )

    assert result["decision_created"] is False
    assert result["act_created"] is False
    assert result["emits_act"] is False
