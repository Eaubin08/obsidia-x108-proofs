from scripts.kernel.canonical_decision_envelope_v1 import (
    CanonicalDecisionEnvelope,
)

from scripts.kernel.kx108_decision_envelope_v1 import (
    KX108DecisionEnvelope,
)

from scripts.providers.canonical_execution_envelope_v1 import (
    CanonicalExecutionEnvelope,
)

from scripts.kernel.kx108_proof_envelope_integrity_v1 import (
    KX108ProofEnvelopeIntegrity,
)


def envelopes():

    execution = CanonicalExecutionEnvelope(
        mission_id="mission-cg65",
        provider_id="brody",
        capability="semantic_context",
        runtime_id="runtime-cg65",
    )

    execution.seal()

    decision = CanonicalDecisionEnvelope(
        envelope_id="decision-envelope-v1",
        source_provider="brody",
        runtime_ref="runtime-cg65",
        guard_status="GUARD_PASSED",
        decision_status="CANDIDATE_ONLY",
    )

    kx108 = KX108DecisionEnvelope(
        authority_status="AUTHORIZED_CANDIDATE",
        decision_status="KX108_DECISION_READY",
        source_authority="KX108",
        act=False,
    )

    return decision, kx108, execution


def test_envelope_chain_is_intact():

    decision, kx108, execution = envelopes()

    result = (
        KX108ProofEnvelopeIntegrity()
        .validate(
            decision,
            kx108,
            execution,
        )
    )

    assert (
        result["envelope_integrity_status"]
        == "INTACT"
    )


def test_runtime_binding_drift_rejected():

    decision, kx108, execution = envelopes()

    decision.runtime_ref = "wrong-runtime"

    result = (
        KX108ProofEnvelopeIntegrity()
        .validate(
            decision,
            kx108,
            execution,
        )
    )

    assert (
        result["envelope_integrity_status"]
        == "REJECTED"
    )


def test_non_kx108_authority_envelope_rejected():

    decision, kx108, execution = envelopes()

    kx108.source_authority = "BRODY"

    result = (
        KX108ProofEnvelopeIntegrity()
        .validate(
            decision,
            kx108,
            execution,
        )
    )

    assert (
        result["envelope_integrity_status"]
        == "REJECTED"
    )


def test_unsealed_execution_envelope_rejected():

    decision, kx108, execution = envelopes()

    execution.status = "CREATED"

    result = (
        KX108ProofEnvelopeIntegrity()
        .validate(
            decision,
            kx108,
            execution,
        )
    )

    assert (
        result["envelope_integrity_status"]
        == "REJECTED"
    )


def test_integrity_layer_claims_no_new_hash_or_authority():

    decision, kx108, execution = envelopes()

    result = (
        KX108ProofEnvelopeIntegrity()
        .validate(
            decision,
            kx108,
            execution,
        )
    )

    assert result["cryptographic_hash_claimed"] is False
    assert result["integrity_authority"] is False
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
