from scripts.kernel.kx108_proof_agent_complete_runtime_v1 import (
    KX108ProofAgentCompleteRuntime,
)


def base(status_key, status):
    return {
        status_key: status,
        "agent_id": "agent-a",
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def surfaces():
    validation = base(
        "agent_validation_status",
        "VALIDATED",
    )

    governance = base(
        "agent_governance_status",
        "VALIDATED",
    )

    security = base(
        "agent_security_status",
        "VALIDATED",
    )

    release = base(
        "agent_release_status",
        "AGENT_RELEASE_CANDIDATE",
    )

    release.update({
        "agent_release_candidate": True,
        "release_ready": False,
        "production_ready": False,
        "deployment_ready": False,
        "final_freeze": False,
    })

    return validation, governance, security, release


def test_agent_complete_runtime_validated():
    result = KX108ProofAgentCompleteRuntime().validate(
        *surfaces()
    )

    assert result["agent_complete_runtime_status"] == "VALIDATED"
    assert result["agent_proof_runtime_complete"] is True


def test_agent_identity_drift_rejected():
    validation, governance, security, release = surfaces()
    security["agent_id"] = "agent-b"

    result = KX108ProofAgentCompleteRuntime().validate(
        validation,
        governance,
        security,
        release,
    )

    assert result["agent_complete_runtime_status"] == "REJECTED"


def test_nonvalidated_security_rejected():
    validation, governance, security, release = surfaces()
    security["agent_security_status"] = "REJECTED"

    result = KX108ProofAgentCompleteRuntime().validate(
        validation,
        governance,
        security,
        release,
    )

    assert result["agent_complete_runtime_status"] == "REJECTED"


def test_false_release_claim_rejected():
    validation, governance, security, release = surfaces()
    release["release_ready"] = True

    result = KX108ProofAgentCompleteRuntime().validate(
        validation,
        governance,
        security,
        release,
    )

    assert result["agent_complete_runtime_status"] == "REJECTED"


def test_complete_runtime_is_not_global_runtime():
    result = KX108ProofAgentCompleteRuntime().validate(
        *surfaces()
    )

    assert result["global_runtime_validated"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False
    assert result["new_authority_created"] is False
    assert result["agent_authority"] is False
    assert result["runtime_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
