"""B8 isolated deterministic core (spec docs/architecture/B8_KNOWLEDGE_PROMOTION_SPEC_V1.md, CLOSED).

GREEN tranche 1: closed enums, local canonical JSON, full SHA-256 identities, slot canonicalization,
object bound, immutable types and the pure T2 evaluator with CAS / duplicate / multi-cause rejection.
Isolated: no app.cognition, no app.harness, no network, no persistence, no runtime authority.
"""
from app.knowledge.b8.contracts import (
    BOUNDARY, OBJECT_TOTAL_BOUND, ClaimClass, ClaimState, GapState, MalformedSlot, ReasonCode,
    TransitionVerdict,
)
from app.knowledge.b8.core import (
    GATE_CONTRACT_VERSION, KnowledgeRecord, SlotSnapshot, TransitionReceipt, TransitionRequest,
    TransitionResult, evaluate_transition,
)
from app.knowledge.b8.serialization import canonical_json, full_identity, knowledge_slot_id

__all__ = [
    "BOUNDARY", "OBJECT_TOTAL_BOUND", "ClaimClass", "ClaimState", "GapState", "MalformedSlot", "ReasonCode",
    "TransitionVerdict", "GATE_CONTRACT_VERSION", "KnowledgeRecord", "SlotSnapshot", "TransitionReceipt",
    "TransitionRequest", "TransitionResult", "evaluate_transition", "canonical_json", "full_identity",
    "knowledge_slot_id",
]
