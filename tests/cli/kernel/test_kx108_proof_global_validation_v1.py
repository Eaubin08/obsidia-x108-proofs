from scripts.kernel.kx108_proof_global_validation_v1 import (
    KX108ProofGlobalValidation,
)


def proof(
    status_key,
    status_value,
):

    return {
        status_key:
            status_value,

        "decision_authority":
            "KX108_ONLY",

        "execution_authority":
            False,

        "memory_write":
            False,

        "kernel_mutation":
            False,

        "emits_act":
            False,
    }


def proofs():

    return {
        "boundary_composition":
            proof(
                "boundary_composition_status",
                "COMPOSED",
            ),

        "final_boundary":
            proof(
                "final_boundary_status",
                "PROOF_BOUNDARY_CLOSED",
            ),

        "envelope_integrity":
            proof(
                "envelope_integrity_status",
                "INTACT",
            ),

        "receipt_chain":
            proof(
                "receipt_chain_status",
                "VALIDATED",
            ),

        "provider_binding":
            proof(
                "provider_binding_status",
                "VALIDATED",
            ),

        "kernel_interface":
            proof(
                "kernel_interface_status",
                "VALIDATED",
            ),
    }


def test_proof_pack_globally_validated():

    result = (
        KX108ProofGlobalValidation()
        .validate(proofs())
    )

    assert (
        result["global_validation_status"]
        == "PROOF_PACK_VALIDATED"
    )

    assert result["proof_pack_validated"] is True
    assert result["proof_count"] == 6


def test_missing_proof_rejects_global_validation():

    candidate = proofs()
    candidate.pop("receipt_chain")

    result = (
        KX108ProofGlobalValidation()
        .validate(candidate)
    )

    assert result["global_validation_status"] == "REJECTED"


def test_failed_proof_rejects_global_validation():

    candidate = proofs()

    candidate[
        "kernel_interface"
    ][
        "kernel_interface_status"
    ] = "REJECTED"

    result = (
        KX108ProofGlobalValidation()
        .validate(candidate)
    )

    assert result["global_validation_status"] == "REJECTED"


def test_authority_escalation_rejects_global_validation():

    candidate = proofs()

    candidate[
        "provider_binding"
    ]["execution_authority"] = True

    result = (
        KX108ProofGlobalValidation()
        .validate(candidate)
    )

    assert result["global_validation_status"] == "REJECTED"


def test_global_means_proof_pack_only():

    result = (
        KX108ProofGlobalValidation()
        .validate(proofs())
    )

    assert result["runtime_globally_validated"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False
    assert result["new_authority_created"] is False
    assert result["global_authority"] is False
