"""B8 isolated deterministic core (spec docs/architecture/B8_KNOWLEDGE_PROMOTION_SPEC_V1.md, CLOSED).

GREEN tranches 1–2: closed enums, local canonical JSON, full SHA-256 identities, slot canonicalization,
object bound, typed claim / evidence / verification / attestation objects, V1 same-frame valid-time algebra
and the single pure gate for T1–T12 (T9 atomic bundle) with CAS / duplicate / multi-cause rejection.
Isolated: no app.cognition, no app.harness, no network, no persistence, no runtime authority.
"""
from app.knowledge.b8.artifacts import EvidenceRef, HumanAttestation, KnowledgeClaim, VerificationRecord
from app.knowledge.b8.contracts import (
    BOUNDARY, OBJECT_TOTAL_BOUND, AttestationKind, ClaimClass, ClaimState, GapState, MalformedSlot, ReasonCode,
    StalenessMechanism, TransitionVerdict, VerificationVerdict,
)
from app.knowledge.b8.core import (
    GATE_CONTRACT_VERSION, KnowledgeRecord, SlotSnapshot, SupersessionTransitionBundle, TransitionReceipt,
    TransitionRequest, TransitionResult, evaluate_transition,
)
from app.knowledge.b8.serialization import canonical_json, full_identity, knowledge_slot_id
from app.knowledge.b8.temporal import (
    TEMPORALLY_INDETERMINATE, TemporalFrameRef, ValidTimeInterval, contains, overlaps, temporally_comparable,
)

__all__ = [
    "BOUNDARY", "OBJECT_TOTAL_BOUND", "AttestationKind", "ClaimClass", "ClaimState", "GapState", "MalformedSlot",
    "ReasonCode", "StalenessMechanism", "TransitionVerdict", "VerificationVerdict", "GATE_CONTRACT_VERSION",
    "KnowledgeRecord", "SlotSnapshot", "SupersessionTransitionBundle", "TransitionReceipt", "TransitionRequest",
    "TransitionResult", "evaluate_transition", "canonical_json", "full_identity", "knowledge_slot_id",
    "EvidenceRef", "HumanAttestation", "KnowledgeClaim", "VerificationRecord", "TEMPORALLY_INDETERMINATE",
    "TemporalFrameRef", "ValidTimeInterval", "contains", "overlaps", "temporally_comparable",
]
