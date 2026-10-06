"""F10 double demonstration: physical GPS and cognitive Brody/GMS consumers.

Both paths enter the same MMonde -> UDIP -> GuardX108 -> proof boundary.
The demo never grants execution authority and does not claim live GPS closure.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.gps_physical.bridge_v0 import RecordedGpsEvidenceV0, recorded_gps_to_world
from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0
from periphery.udip.contracts_v0 import domain_state_to_governance_payload, world_state_to_domain_state
from periphery.governed_world.bridge_v0 import decide_governed_world_v0
from proofs.governed_world_decision_proof_v0 import (
    GovernedWorldDecisionProofV0,
    build_governed_world_decision_proof_v0,
    verify_governed_world_decision_proof_v0,
)


@dataclass(frozen=True)
class CognitiveEvidenceV0:
    observation_id: str
    observed_at: str
    source_ref: str
    source_hash: str
    state: dict[str, object]
    evidence_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()


@dataclass(frozen=True)
class DoubleDemoResultV0:
    path: str
    domain_id: str
    world_state_ref: str
    domain_state_ref: str
    x108_gate: str
    reason_code: str
    proof: GovernedWorldDecisionProofV0
    proof_verified: bool
    proof_verdict: str
    decision_authority: str = "KX108_ONLY"
    execution_authority: bool = False


def cognitive_evidence_to_world(evidence: CognitiveEvidenceV0) -> WorldStateV0:
    """Conservative cognitive/GMS observation: content is represented, never promoted to truth."""
    obs = WorldObservationV0(
        observation_id=evidence.observation_id,
        observed_at=evidence.observed_at,
        source_refs=(evidence.source_ref,),
        source_hashes=(evidence.source_hash,),
        entity_ref="brody_gms_cognitive_observation",
        state=dict(evidence.state),
        uncertainty=evidence.uncertainty,
        contradictions=evidence.contradictions,
        evidence_refs=evidence.evidence_refs,
        causal_status="UNKNOWN",
    )
    return WorldStateV0(
        world_state_id=f"cognitive-world:{evidence.observation_id}",
        valid_at=evidence.observed_at,
        observations=(obs,),
        candidate_reality=True,
        unknowns=evidence.uncertainty,
        contradictions=evidence.contradictions,
        provenance_refs=(evidence.source_ref,),
    )


def _run_path(*, path: str, world: WorldStateV0, domain_id: str, proposed_action_ref: str, confidence: float) -> DoubleDemoResultV0:
    domain_state = world_state_to_domain_state(world, domain_id=domain_id)
    payload = domain_state_to_governance_payload(domain_state, proposed_action_ref=proposed_action_ref)
    envelope = decide_governed_world_v0(payload, confidence=confidence)
    proof = build_governed_world_decision_proof_v0(payload, envelope)
    verified, verdict = verify_governed_world_decision_proof_v0(proof, payload, envelope)
    return DoubleDemoResultV0(
        path=path,
        domain_id=domain_id,
        world_state_ref=payload.world_state_ref,
        domain_state_ref=payload.domain_state_ref,
        x108_gate=envelope.x108_gate,
        reason_code=envelope.reason_code,
        proof=proof,
        proof_verified=verified,
        proof_verdict=verdict,
    )


def run_gps_demo_v0(evidence: RecordedGpsEvidenceV0, *, confidence: float = 0.9) -> DoubleDemoResultV0:
    return _run_path(
        path="GPS_PHYSICAL",
        world=recorded_gps_to_world(evidence),
        domain_id="gps_defense_aviation",
        proposed_action_ref="proposal:gps:inspect",
        confidence=confidence,
    )


def run_brody_gms_demo_v0(evidence: CognitiveEvidenceV0, *, confidence: float = 0.9) -> DoubleDemoResultV0:
    # The current canonical KX108 domain vocabulary has no Brody-specific sovereign domain.
    # Brody/GMS is therefore a cognitive consumer represented through the existing generic
    # enterprise governance domain; this adapter does not invent a new kernel domain.
    return _run_path(
        path="BRODY_GMS_COGNITIVE",
        world=cognitive_evidence_to_world(evidence),
        domain_id="enterprise",
        proposed_action_ref="proposal:brody-gms:respond",
        confidence=confidence,
    )
