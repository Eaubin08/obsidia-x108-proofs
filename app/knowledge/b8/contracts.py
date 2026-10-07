"""B8 closed vocabularies, authority boundary and object bound (spec §1–§4, §8, §9.1, §9.5, §11).

Enums are plain (non-str) Enums so that VERDICT != STATE != REASON holds as values, not only as names.
"""
from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

BOUNDARY: Mapping[str, Any] = MappingProxyType({
    "decision_authority": "KX108_ONLY",
    "promotion_authority": "B8_CANONICAL_TRANSITION_GATE",
    "kx108_knowledge_promotion_role": "NONE",
    "memory_write": False,
    "emits_act": False,
    "kernel_mutation": False,
})

OBJECT_TOTAL_BOUND = 32768  # OBJECT_TOTAL_BOUND=MAX_CANDIDATE_CHARS, canonical JSON chars per B8 object


class TransitionVerdict(Enum):
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    NO_OP_DUPLICATE = "NO_OP_DUPLICATE"


class ClaimState(Enum):
    CANDIDATE = "CANDIDATE"
    HELD = "HELD"
    REJECTED = "REJECTED"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    PROMOTED = "PROMOTED"
    CONTESTED = "CONTESTED"
    SUPERSEDED = "SUPERSEDED"
    INVALIDATED = "INVALIDATED"
    STALE = "STALE"


class GapState(Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    SUPERSEDED = "SUPERSEDED"


class ClaimClass(Enum):
    FORMAL_CLAIM = "FORMAL_CLAIM"
    CODE_BUILD_CLAIM = "CODE_BUILD_CLAIM"
    PHYSICAL_CLAIM = "PHYSICAL_CLAIM"
    DOCUMENTARY_CLAIM = "DOCUMENTARY_CLAIM"
    DOMAIN_CLAIM = "DOMAIN_CLAIM"
    HUMAN_DECLARATION = "HUMAN_DECLARATION"
    ORGANIZATIONAL_POLICY = "ORGANIZATIONAL_POLICY"


class ReasonCode(Enum):
    """Closed canonical rejection reasons (§9.5), listed in code point order."""
    attestation_inadmissible = "attestation_inadmissible"
    attestation_missing = "attestation_missing"
    backdated_record = "backdated_record"
    containment_not_satisfied = "containment_not_satisfied"
    contradiction_inadmissible = "contradiction_inadmissible"
    contradiction_unresolved = "contradiction_unresolved"
    evidence_inadmissible = "evidence_inadmissible"
    forbidden_transition = "forbidden_transition"
    malformed_object = "malformed_object"
    malformed_slot = "malformed_slot"
    multiple_predecessors_unsupported = "multiple_predecessors_unsupported"
    no_eligible_predecessor = "no_eligible_predecessor"
    no_temporal_overlap = "no_temporal_overlap"
    open_contradiction = "open_contradiction"
    oversize_object = "oversize_object"
    partition_not_partial = "partition_not_partial"
    predecessor_mismatch = "predecessor_mismatch"
    reason_missing = "reason_missing"
    ref_binding_mismatch = "ref_binding_mismatch"
    referenced_claim_not_promoted = "referenced_claim_not_promoted"
    resolution_relation_invalid = "resolution_relation_invalid"
    slot_mismatch = "slot_mismatch"
    slot_occupied = "slot_occupied"
    stale_request = "stale_request"
    staleness_trigger_inadmissible = "staleness_trigger_inadmissible"
    successor_gap_not_open = "successor_gap_not_open"
    temporal_relation_indeterminate = "temporal_relation_indeterminate"
    verification_not_satisfied = "verification_not_satisfied"
    verifier_inadmissible = "verifier_inadmissible"


class MalformedSlot(ValueError):
    """Slot canonicalization violation (§5): fail closed with ReasonCode.malformed_slot."""

    reason = ReasonCode.malformed_slot
