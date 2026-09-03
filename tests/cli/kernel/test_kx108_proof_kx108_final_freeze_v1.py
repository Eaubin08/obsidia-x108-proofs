from scripts.kernel.kx108_proof_kx108_final_freeze_v1 import (
    KX108ProofFinalFreeze,
)


def safe():
    return {
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "release_ready": False,
        "final_freeze": False,
    }


def surfaces():
    e2e = safe()
    e2e.update({
        "kx108_end_to_end_validation_status":
            "PROOF_E2E_VALIDATED",

        "runtime_end_to_end_validated":
            False,

        "runtime_globally_validated":
            False,
    })

    security = safe()
    security[
        "kx108_security_audit_status"
    ] = "PROOF_SECURITY_SURFACES_AUDITED"

    preparation = safe()
    preparation.update({
        "kx108_release_preparation_status":
            "PROOF_RELEASE_REVIEW_PREPARED",

        "release_authorized":
            False,

        "runtime_activation_authorized":
            False,

        "production_ready":
            False,

        "deployment_ready":
            False,
    })

    final_boundary = safe()
    final_boundary.update({
        "final_boundary_status":
            "PROOF_BOUNDARY_CLOSED",

        "proof_pack_closed":
            True,

        "runtime_closed":
            False,
    })

    return (
        e2e,
        security,
        preparation,
        final_boundary,
    )


def test_final_numbered_cg_proof_sequence_frozen():
    result = (
        KX108ProofFinalFreeze()
        .close(
            *surfaces()
        )
    )

    assert (
        result["kx108_final_freeze_status"]
        == "CG_PROOF_SEQUENCE_FROZEN"
    )

    assert result["numbered_cg_sequence_closed"] is True
    assert result["last_numbered_cg"] == 100
    assert result["proof_artifact_freeze"] is True


def test_proof_freeze_is_not_runtime_freeze():
    result = (
        KX108ProofFinalFreeze()
        .close(
            *surfaces()
        )
    )

    assert result["runtime_closed"] is False
    assert result["runtime_frozen"] is False
    assert result["runtime_globally_validated"] is False
    assert result["runtime_end_to_end_validated"] is False
    assert result["final_freeze"] is False


def test_unclosed_proof_boundary_rejected():
    values = list(surfaces())

    values[3][
        "proof_pack_closed"
    ] = False

    result = (
        KX108ProofFinalFreeze()
        .close(
            *values
        )
    )

    assert result["kx108_final_freeze_status"] == "REJECTED"


def test_false_release_authorization_rejected():
    values = list(surfaces())

    values[2][
        "release_authorized"
    ] = True

    result = (
        KX108ProofFinalFreeze()
        .close(
            *values
        )
    )

    assert result["kx108_final_freeze_status"] == "REJECTED"


def test_final_cg_freeze_creates_no_authority():
    result = (
        KX108ProofFinalFreeze()
        .close(
            *surfaces()
        )
    )

    assert result["release_authorized"] is False
    assert result["runtime_activation_authorized"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["new_authority_created"] is False
    assert result["freeze_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
