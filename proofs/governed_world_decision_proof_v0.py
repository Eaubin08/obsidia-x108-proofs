"""F8 proof packet for the governed-world -> KX108 decision boundary.

This is an audit proof, never a decision or execution authority.
It hash-binds the world/domain references and the real CanonicalDecisionEnvelope.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

from sigma.contracts import CanonicalDecisionEnvelope
from periphery.udip.contracts_v0 import GovernancePayloadV0


def _canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class GovernedWorldDecisionProofV0:
    proof_version: str
    world_state_ref: str
    domain_state_ref: str
    domain_id: str
    proposed_action_ref: str | None
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    decision_id: str
    trace_id: str
    x108_gate: str
    reason_code: str
    decision_envelope_hash: str
    input_binding_hash: str
    proof_hash: str
    decision_authority: str = "KX108_ONLY"
    proof_authority: bool = False
    execution_authority: bool = False

    def __post_init__(self) -> None:
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("proof cannot change decision authority")
        if self.proof_authority or self.execution_authority:
            raise ValueError("proof packet cannot authorize decision or execution")


def _envelope_projection(envelope: CanonicalDecisionEnvelope) -> dict[str, object]:
    if not isinstance(envelope, CanonicalDecisionEnvelope):
        raise TypeError("proof requires the real CanonicalDecisionEnvelope")
    return {
        "domain": envelope.domain,
        "market_verdict": envelope.market_verdict,
        "confidence": envelope.confidence,
        "contradictions": list(envelope.contradictions),
        "unknowns": list(envelope.unknowns),
        "risk_flags": list(envelope.risk_flags),
        "x108_gate": envelope.x108_gate,
        "reason_code": envelope.reason_code,
        "severity": str(envelope.severity),
        "decision_id": envelope.decision_id,
        "trace_id": envelope.trace_id,
        "ticket_required": envelope.ticket_required,
        "ticket_id": envelope.ticket_id,
        "attestation_ref": envelope.attestation_ref,
        "source": envelope.source,
        "evidence_refs": list(envelope.evidence_refs),
    }


def _input_projection(payload: GovernancePayloadV0) -> dict[str, object]:
    return {
        "domain_id": payload.domain_id,
        "domain_state_ref": payload.domain_state_ref,
        "world_state_ref": payload.world_state_ref,
        "unknowns": list(payload.unknowns),
        "contradictions": list(payload.contradictions),
        "risk_flags": list(payload.risk_flags),
        "evidence_refs": list(payload.evidence_refs),
        "provenance_refs": list(payload.provenance_refs),
        "proposed_action_ref": payload.proposed_action_ref,
        "decision_authority": payload.decision_authority,
    }


def build_governed_world_decision_proof_v0(
    payload: GovernancePayloadV0,
    envelope: CanonicalDecisionEnvelope,
) -> GovernedWorldDecisionProofV0:
    if envelope.domain != payload.domain_id:
        raise ValueError("domain binding mismatch")
    if envelope.x108_gate not in {"ALLOW", "HOLD", "BLOCK"}:
        raise ValueError("invalid KX108 gate")

    input_hash = _canonical_hash(_input_projection(payload))
    envelope_hash = _canonical_hash(_envelope_projection(envelope))
    body = {
        "proof_version": "GOVERNED_WORLD_DECISION_PROOF_V0",
        "world_state_ref": payload.world_state_ref,
        "domain_state_ref": payload.domain_state_ref,
        "domain_id": payload.domain_id,
        "proposed_action_ref": payload.proposed_action_ref,
        "evidence_refs": list(payload.evidence_refs),
        "provenance_refs": list(payload.provenance_refs),
        "decision_id": envelope.decision_id,
        "trace_id": envelope.trace_id,
        "x108_gate": envelope.x108_gate,
        "reason_code": envelope.reason_code,
        "decision_envelope_hash": envelope_hash,
        "input_binding_hash": input_hash,
        "decision_authority": "KX108_ONLY",
        "proof_authority": False,
        "execution_authority": False,
    }
    packet = dict(body)
    packet["evidence_refs"] = tuple(body["evidence_refs"])
    packet["provenance_refs"] = tuple(body["provenance_refs"])
    packet["proof_hash"] = _canonical_hash(body)
    return GovernedWorldDecisionProofV0(**packet)


def verify_governed_world_decision_proof_v0(
    proof: GovernedWorldDecisionProofV0,
    payload: GovernancePayloadV0,
    envelope: CanonicalDecisionEnvelope,
) -> tuple[bool, str]:
    if not isinstance(proof, GovernedWorldDecisionProofV0):
        return False, "PROOF_TYPE_INVALID"
    if proof.decision_authority != "KX108_ONLY" or proof.proof_authority or proof.execution_authority:
        return False, "PROOF_AUTHORITY_INVALID"
    if proof.domain_id != payload.domain_id or envelope.domain != payload.domain_id:
        return False, "DOMAIN_BINDING_MISMATCH"
    if proof.input_binding_hash != _canonical_hash(_input_projection(payload)):
        return False, "INPUT_BINDING_HASH_MISMATCH"
    if proof.decision_envelope_hash != _canonical_hash(_envelope_projection(envelope)):
        return False, "DECISION_ENVELOPE_HASH_MISMATCH"

    body = asdict(proof)
    body.pop("proof_hash")
    body["evidence_refs"] = list(proof.evidence_refs)
    body["provenance_refs"] = list(proof.provenance_refs)
    if proof.proof_hash != _canonical_hash(body):
        return False, "PROOF_HASH_MISMATCH"
    return True, "VERIFIED"
