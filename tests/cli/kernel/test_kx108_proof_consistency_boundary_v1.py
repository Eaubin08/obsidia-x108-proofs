from scripts.kernel.kx108_proof_consistency_boundary_v1 import (
    KX108ProofConsistencyBoundary,
)


def valid_proof():

    return {
        "proof_id": "proof-cg26-v1",
        "provenance_chain": [1, 2, 3, 4],
        "contradiction": False,
    }


def test_consistent_proof():

    result = KX108ProofConsistencyBoundary().evaluate(
        valid_proof()
    )

    assert result["consistency_status"] == "CONSISTENT"
    assert result["propagation_allowed"] is True


def test_contradiction_blocks_propagation():

    proof = valid_proof()
    proof["contradiction"] = True
    proof["contradiction_type"] = "semantic_conflict"

    result = KX108ProofConsistencyBoundary().evaluate(
        proof
    )

    assert result["consistency_status"] == "REJECTED"
    assert result["propagation_allowed"] is False
    assert (
        result["contradiction_resolution"]["propagation_blocked"]
        is True
    )


def test_invalid_provenance_rejected():

    proof = valid_proof()
    proof["provenance_chain"] = [1, 2]

    result = KX108ProofConsistencyBoundary().evaluate(
        proof
    )

    assert result["consistency_status"] == "REJECTED"
    assert (
        result["verification"]["checks"]["chain_integrity"]
        is False
    )


def test_consistency_has_no_authority():

    result = KX108ProofConsistencyBoundary().evaluate(
        valid_proof()
    )

    assert result["authority"] is False
    assert result["decision_authority"] is False


def test_consistency_kernel_integrity():

    status = KX108ProofConsistencyBoundary().status()

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
