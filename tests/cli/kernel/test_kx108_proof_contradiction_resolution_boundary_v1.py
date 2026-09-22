from scripts.kernel.kx108_proof_contradiction_resolution_boundary_v1 import (
    KX108ProofContradictionResolver,
)


def contradiction():

    return {

        "proof_id":
            "cg25-proof",

        "contradiction":
            True,

        "contradiction_type":
            "INVARIANT_CONFLICT",

    }



def test_detect():

    result = (
        KX108ProofContradictionResolver()
        .resolve(
            contradiction()
        )
    )

    assert result["contradiction_detected"] is True


def test_type():

    result = (
        KX108ProofContradictionResolver()
        .resolve(
            contradiction()
        )
    )

    assert (
        result["contradiction_type"]
        ==
        "INVARIANT_CONFLICT"
    )


def test_block():

    result = (
        KX108ProofContradictionResolver()
        .resolve(
            contradiction()
        )
    )

    assert (
        result["propagation_blocked"]
        is True
    )


def test_status():

    assert (
        KX108ProofContradictionResolver()
        .status()["kernel_mutation"]
        is False
    )


def test_closed():

    result = (
        KX108ProofContradictionResolver()
        .resolve({})
    )

    assert result["contradiction_detected"] is False
    assert result["authority"] is False
    assert result["kernel_mutation"] is False
