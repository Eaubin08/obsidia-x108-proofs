from __future__ import annotations

from dataclasses import replace

from periphery.governed_world.bridge_v0 import decide_governed_world_v0
from periphery.udip.contracts_v0 import GovernancePayloadV0
from proofs.governed_world_decision_proof_v0 import (
    build_governed_world_decision_proof_v0,
    verify_governed_world_decision_proof_v0,
)


def payload(**overrides):
    data = dict(
        domain_id="gps_defense_aviation",
        domain_state_ref="gps:world-proof:t",
        world_state_ref="world-proof",
        evidence_refs=("evidence:gps:1",),
        provenance_refs=("source:rinex:1",),
        proposed_action_ref="proposal:inspect",
    )
    data.update(overrides)
    return GovernancePayloadV0(**data)


def test_real_guard_envelope_builds_verifiable_world_proof():
    p = payload()
    envelope = decide_governed_world_v0(p, confidence=0.9)
    proof = build_governed_world_decision_proof_v0(p, envelope)
    assert verify_governed_world_decision_proof_v0(proof, p, envelope) == (True, "VERIFIED")
    assert proof.x108_gate == "ALLOW"
    assert proof.decision_authority == "KX108_ONLY"


def test_input_tampering_breaks_world_binding():
    p = payload()
    envelope = decide_governed_world_v0(p, confidence=0.9)
    proof = build_governed_world_decision_proof_v0(p, envelope)
    tampered = payload(world_state_ref="world-substituted")
    assert verify_governed_world_decision_proof_v0(proof, tampered, envelope)[1] == "INPUT_BINDING_HASH_MISMATCH"


def test_envelope_tampering_breaks_decision_binding():
    p = payload()
    envelope = decide_governed_world_v0(p, confidence=0.9)
    proof = build_governed_world_decision_proof_v0(p, envelope)
    envelope.reason_code = "FORGED_REASON"
    assert verify_governed_world_decision_proof_v0(proof, p, envelope)[1] == "DECISION_ENVELOPE_HASH_MISMATCH"


def test_proof_packet_tampering_breaks_own_hash():
    p = payload()
    envelope = decide_governed_world_v0(p, confidence=0.9)
    proof = build_governed_world_decision_proof_v0(p, envelope)
    tampered = replace(proof, proposed_action_ref="proposal:substituted")
    assert verify_governed_world_decision_proof_v0(tampered, p, envelope)[1] == "PROOF_HASH_MISMATCH"


def test_proof_never_grants_execution_or_decision_authority():
    p = payload(unknowns=("PHYSICAL_AUTHENTICITY_UNKNOWN",))
    envelope = decide_governed_world_v0(p, confidence=0.4)
    proof = build_governed_world_decision_proof_v0(p, envelope)
    assert proof.x108_gate == "HOLD"
    assert proof.proof_authority is False
    assert proof.execution_authority is False
