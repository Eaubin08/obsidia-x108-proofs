from scripts.kernel.kx108_proof_kx108_security_audit_v1 import (
    KX108ProofSecurityAudit,
)


def safe():
    return {
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def surfaces():
    boundary = safe()
    boundary["checks"] = {
        "payload_object": True,
        "sanitization_valid": True,
    }

    provider = safe()
    provider[
        "provider_security_runtime_status"
    ] = "VALIDATED"

    agent = safe()
    agent[
        "agent_security_status"
    ] = "VALIDATED"

    e2e = safe()
    e2e.update({
        "kx108_end_to_end_validation_status":
            "PROOF_E2E_VALIDATED",

        "runtime_end_to_end_validated":
            False,

        "runtime_globally_validated":
            False,
    })

    return boundary, provider, agent, e2e


def test_security_proof_surfaces_audited():
    result = (
        KX108ProofSecurityAudit()
        .validate(
            *surfaces()
        )
    )

    assert (
        result["kx108_security_audit_status"]
        == "PROOF_SECURITY_SURFACES_AUDITED"
    )

    assert (
        result["proof_security_surfaces_audited"]
        is True
    )


def test_invalid_agent_security_rejected():
    values = list(surfaces())

    values[2][
        "agent_security_status"
    ] = "REJECTED"

    result = (
        KX108ProofSecurityAudit()
        .validate(
            *values
        )
    )

    assert result["kx108_security_audit_status"] == "REJECTED"


def test_invalid_security_boundary_check_rejected():
    values = list(surfaces())

    values[0]["checks"][
        "sanitization_valid"
    ] = False

    result = (
        KX108ProofSecurityAudit()
        .validate(
            *values
        )
    )

    assert result["kx108_security_audit_status"] == "REJECTED"


def test_false_runtime_global_claim_rejected():
    values = list(surfaces())

    values[3][
        "runtime_globally_validated"
    ] = True

    result = (
        KX108ProofSecurityAudit()
        .validate(
            *values
        )
    )

    assert result["kx108_security_audit_status"] == "REJECTED"


def test_security_audit_is_explicitly_bounded():
    result = (
        KX108ProofSecurityAudit()
        .validate(
            *surfaces()
        )
    )

    assert result["complete_system_security_audit"] is False
    assert result["penetration_test_completed"] is False
    assert result["infrastructure_security_certified"] is False
    assert result["production_security_approved"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False
    assert result["audit_authority"] is False
    assert result["security_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
