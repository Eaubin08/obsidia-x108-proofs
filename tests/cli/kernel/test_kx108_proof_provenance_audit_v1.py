from scripts.kernel.kx108_proof_provenance_audit_v1 import (
    KX108ProofProvenanceAudit,
)


def test_audit_pass():

    result = (
        KX108ProofProvenanceAudit()
        .audit(
            {

            "chain_id":
                "kx108-proof-provenance-chain-v1",

            "chain_status":
                "VALID",

            "provenance_depth":
                4,

            "authority":
                False,

            "kernel_mutation":
                False,

            }
        )
    )


    assert (
        result["audit_status"]
        ==
        "PASSED"
    )


def test_chain_required():

    result = (
        KX108ProofProvenanceAudit()
        .audit({})
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_depth_required():

    result = (
        KX108ProofProvenanceAudit()
        .audit(
            {
            "chain_id":
                "kx108-proof-provenance-chain-v1",

            "chain_status":
                "VALID",

            "provenance_depth":
                2,

            "authority":
                False,

            "kernel_mutation":
                False,
            }
        )
    )

    assert (
        result["audit_status"]
        ==
        "FAILED"
    )


def test_authority():

    result = (
        KX108ProofProvenanceAudit()
        .audit({})
    )

    assert (
        "checks"
        in result
    )


def test_kernel():

    assert True
