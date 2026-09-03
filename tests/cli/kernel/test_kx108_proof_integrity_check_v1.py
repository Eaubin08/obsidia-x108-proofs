from scripts.kernel.kx108_proof_integrity_check_v1 import (
    KX108ProofIntegrityCheck,
)


def proof():

    return {
        "proof_id": "proof-cg30-v1",
        "provenance_chain": [1, 2, 3, 4],
        "contradiction": False,
    }


def states():

    return [
        {
            "meta_domain": "SYSTEM",
            "state": "validated",
        },
        {
            "meta_domain": "ENVIRONMENT",
            "state": "validated",
        },
    ]


def test_integrity_intact():

    result = KX108ProofIntegrityCheck().check(
        proof(),
        states(),
    )

    assert result["integrity_status"] == "INTACT"
    assert all(result["checks"].values())


def test_contradiction_breaks_integrity():

    candidate = proof()
    candidate["contradiction"] = True
    candidate["contradiction_type"] = "conflict"

    result = KX108ProofIntegrityCheck().check(
        candidate,
        states(),
    )

    assert result["integrity_status"] == "REJECTED"
    assert result["checks"]["proof_consistent"] is False


def test_invalid_state_breaks_integrity():

    state_set = states()
    state_set[0]["state"] = "pending"

    result = KX108ProofIntegrityCheck().check(
        proof(),
        state_set,
    )

    assert result["integrity_status"] == "REJECTED"
    assert result["checks"]["state_validated"] is False


def test_integrity_preserves_kernel_boundary():

    result = KX108ProofIntegrityCheck().check(
        proof(),
        states(),
    )

    assert (
        result["checks"]["kernel_boundary_preserved"]
        is True
    )

    assert result["kernel_mutation"] is False


def test_integrity_has_no_authority():

    status = KX108ProofIntegrityCheck().status()

    assert status["authority"] is False
    assert status["decision_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
