from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelopeBuilder,
)

from scripts.kernel.kx108_proof_agent_decision_flow_v1 import (
    KX108ProofAgentDecisionFlow,
)

from scripts.kernel.kx108_proof_agent_canonical_envelope_v1 import (
    KX108ProofAgentCanonicalEnvelope,
)


def orchestration_boundary():
    return {
        "agent_orchestration_boundary_status":
            "VALIDATED",

        "orchestrator_invoked_here":
            False,

        "orchestration_authority":
            False,

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


def decision_flow():
    return (
        KX108ProofAgentDecisionFlow()
        .validate(
            orchestration_boundary()
        )
    )


def envelope():
    return (
        CanonicalDecisionEnvelopeBuilder()
        .build({
            "provider_id":
                "kx108-gateway",

            "runtime_id":
                "runtime-cg94",

            "status":
                "GUARD_PASSED",
        })
    )


def test_agent_canonical_envelope_validated():
    result = (
        KX108ProofAgentCanonicalEnvelope()
        .validate(
            decision_flow(),
            envelope(),
        )
    )

    assert (
        result["agent_canonical_envelope_status"]
        == "VALIDATED"
    )


def test_canonical_envelope_remains_candidate_only():
    result = (
        KX108ProofAgentCanonicalEnvelope()
        .validate(
            decision_flow(),
            envelope(),
        )
    )

    assert (
        result["canonical_envelope"][
            "decision_status"
        ]
        == "CANDIDATE_ONLY"
    )


def test_direct_agent_decision_claim_rejected():
    flow = decision_flow()
    flow["agent_decision_created"] = True

    result = (
        KX108ProofAgentCanonicalEnvelope()
        .validate(
            flow,
            envelope(),
        )
    )

    assert (
        result["agent_canonical_envelope_status"]
        == "REJECTED"
    )


def test_missing_canonical_runtime_rejected():
    candidate = envelope()
    candidate.runtime_ref = ""

    result = (
        KX108ProofAgentCanonicalEnvelope()
        .validate(
            decision_flow(),
            candidate,
        )
    )

    assert (
        result["agent_canonical_envelope_status"]
        == "REJECTED"
    )


def test_agent_does_not_gain_envelope_authority():
    result = (
        KX108ProofAgentCanonicalEnvelope()
        .validate(
            decision_flow(),
            envelope(),
        )
    )

    assert result["agent_envelope_created_here"] is False
    assert result["agent_binding_claimed"] is False
    assert result["canonical_envelope_is_agent_authority"] is False
    assert result["context_adapter_invoked_here"] is False
    assert result["x108_submitted_here"] is False
    assert result["envelope_authority"] is False
    assert result["agent_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
