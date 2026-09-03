from scripts.kernel.kx108_proof_kx108_global_runtime_v1 import (
    KX108ProofGlobalRuntime,
)


def safe(status_key, status):
    return {
        status_key: status,
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def surfaces():
    proof_pack = safe(
        "global_validation_status",
        "PROOF_PACK_VALIDATED",
    )

    proof_pack.update({
        "proof_pack_validated": True,
        "runtime_globally_validated": False,
        "production_ready": False,
        "release_ready": False,
        "deployment_ready": False,
        "final_freeze": False,
    })

    execution = safe(
        "execution_runtime_status",
        "VALIDATED",
    )

    provider = safe(
        "provider_validation_runtime_status",
        "VALIDATED",
    )

    mission = safe(
        "mission_runtime_status",
        "VALIDATED",
    )

    agent = safe(
        "agent_complete_runtime_status",
        "VALIDATED",
    )

    agent.update({
        "agent_proof_runtime_complete": True,
        "global_runtime_validated": False,
    })

    envelope = safe(
        "agent_canonical_envelope_status",
        "VALIDATED",
    )

    receipt = safe(
        "agent_receipt_closure_status",
        "VALIDATED",
    )

    return (
        proof_pack,
        execution,
        provider,
        mission,
        agent,
        envelope,
        receipt,
    )


def test_proof_runtime_surfaces_validate():
    result = (
        KX108ProofGlobalRuntime()
        .validate(
            *surfaces()
        )
    )

    assert (
        result["kx108_global_runtime_status"]
        == "PROOF_RUNTIME_SURFACES_VALIDATED"
    )

    assert (
        result["proof_runtime_surfaces_validated"]
        is True
    )


def test_global_runtime_does_not_claim_production_runtime():
    result = (
        KX108ProofGlobalRuntime()
        .validate(
            *surfaces()
        )
    )

    assert result["runtime_globally_validated"] is False
    assert result["runtime_end_to_end_validated"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False


def test_false_upstream_global_runtime_claim_rejected():
    values = list(surfaces())

    values[0][
        "runtime_globally_validated"
    ] = True

    result = (
        KX108ProofGlobalRuntime()
        .validate(
            *values
        )
    )

    assert (
        result["kx108_global_runtime_status"]
        == "REJECTED"
    )


def test_invalid_provider_runtime_rejected():
    values = list(surfaces())

    values[2][
        "provider_validation_runtime_status"
    ] = "REJECTED"

    result = (
        KX108ProofGlobalRuntime()
        .validate(
            *values
        )
    )

    assert (
        result["kx108_global_runtime_status"]
        == "REJECTED"
    )


def test_global_runtime_creates_no_authority():
    result = (
        KX108ProofGlobalRuntime()
        .validate(
            *surfaces()
        )
    )

    assert result["new_authority_created"] is False
    assert result["global_runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
