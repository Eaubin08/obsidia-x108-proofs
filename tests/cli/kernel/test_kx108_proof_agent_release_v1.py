from scripts.kernel.kx108_proof_agent_release_v1 import (
    KX108ProofAgentRelease,
)


def agent_validation():

    return {
        "agent_validation_status":
            "VALIDATED",

        "agent_id":
            "world_action_agent_v4",

        "agent_authority":
            False,

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


def agent_governance():

    return {
        "agent_governance_status":
            "VALIDATED",

        "agent_id":
            "world_action_agent_v4",

        "agent_authority":
            False,

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


def agent_security():

    return {
        "agent_security_status":
            "VALIDATED",

        "agent_id":
            "world_action_agent_v4",

        "agent_authority":
            False,

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


def release_candidate():

    return {
        "release_candidate_status":
            "PROOF_PACK_RELEASE_CANDIDATE",

        "proof_pack_release_candidate":
            True,

        "release_review_allowed":
            True,

        "production_ready":
            False,

        "release_ready":
            False,

        "deployment_ready":
            False,

        "final_freeze":
            False,

        "candidate_authority":
            False,

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


def test_agent_becomes_release_review_candidate():

    result = (
        KX108ProofAgentRelease()
        .evaluate(
            agent_validation(),
            agent_governance(),
            agent_security(),
            release_candidate(),
        )
    )

    assert (
        result["agent_release_status"]
        == "AGENT_RELEASE_CANDIDATE"
    )

    assert result["agent_release_candidate"] is True


def test_agent_candidate_is_not_actual_release():

    result = (
        KX108ProofAgentRelease()
        .evaluate(
            agent_validation(),
            agent_governance(),
            agent_security(),
            release_candidate(),
        )
    )

    assert result["release_review_allowed"] is True
    assert result["release_ready"] is False
    assert result["production_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False


def test_agent_identity_drift_rejected():

    candidate = agent_security()
    candidate["agent_id"] = "other-agent"

    result = (
        KX108ProofAgentRelease()
        .evaluate(
            agent_validation(),
            agent_governance(),
            candidate,
            release_candidate(),
        )
    )

    assert result["agent_release_status"] == "REJECTED"


def test_false_release_ready_claim_rejected():

    candidate = release_candidate()

    candidate[
        "release_ready"
    ] = True

    result = (
        KX108ProofAgentRelease()
        .evaluate(
            agent_validation(),
            agent_governance(),
            agent_security(),
            candidate,
        )
    )

    assert result["agent_release_status"] == "REJECTED"


def test_agent_release_creates_no_authority():

    result = (
        KX108ProofAgentRelease()
        .evaluate(
            agent_validation(),
            agent_governance(),
            agent_security(),
            release_candidate(),
        )
    )

    assert result["new_authority_created"] is False
    assert result["release_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
