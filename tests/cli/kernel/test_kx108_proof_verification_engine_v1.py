from scripts.kernel.kx108_proof_verification_engine_v1 import (
    KX108ProofVerificationEngine,
)


def proof():

    return {

        "proof_id":
            "proof-cg24-v1",

        "provenance_chain":
            [
                1,2,3,4
            ],

        "contradiction":
            False,

    }



def test_verified():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            proof()
        )
    )

    assert (
        result["verification_status"]
        ==
        "VERIFIED"
    )


def test_identity():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            proof()
        )
    )

    assert (
        result["checks"]["proof_identity"]
        is True
    )


def test_chain():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            proof()
        )
    )

    assert (
        result["checks"]["chain_integrity"]
        is True
    )


def test_contradiction():

    result = (
        KX108ProofVerificationEngine()
        .verify(
            proof()
        )
    )

    assert (
        result["checks"]["contradiction_free"]
        is True
    )


def test_kernel():

    assert (
        KX108ProofVerificationEngine()
        .status()["kernel_mutation"]
        is False
    )
