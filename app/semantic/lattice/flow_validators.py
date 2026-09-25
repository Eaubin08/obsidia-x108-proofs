"""Family-specific validators for OrderedMeaningFlow V0.

The validators are deliberately small and descriptive. They reject family
leakage, authority shortcuts, and memory-write escalation without adding a
runtime engine.
"""
from __future__ import annotations

from enum import Enum
from typing import Mapping

TEMPORAL_COORDINATES = frozenset({
    "UTTERANCE_TIME",
    "EVENT_TIME",
    "OBSERVATION_TIME",
    "KNOWLEDGE_ACQUISITION_TIME",
    "MEMORY_STORAGE_TIME",
    "VALID_FROM",
    "VALID_TO",
})

TEMPORAL_RELATIONS = frozenset({
    "BEFORE",
    "AFTER",
    "SIMULTANEOUS",
    "OVERLAPS",
    "STARTS",
    "ENDS",
})

CAUSAL_CLAIM_LEVELS = frozenset({
    "LINGUISTIC_CAUSAL_CLAIM",
    "REPORTED_CAUSAL_CLAIM",
    "INFERRED_CAUSAL_RELATION",
    "OBSERVED_DEPENDENCY",
    "PHYSICAL_CAUSAL_EVIDENCE",
    "VALIDATED_CAUSAL_PROOF",
})

CAUSAL_RELATIONS = frozenset({
    "CAUSES",
    "ENABLES",
    "PREVENTS",
    "CONDITIONS",
    "CONTRIBUTES_TO",
})

EPISTEMIC_STATES = frozenset({
    "UNKNOWN",
    "UNCERTAIN",
    "HYPOTHESIS",
    "CLAIMED",
    "REPORTED",
    "BELIEVED",
    "OBSERVED",
    "SUPPORTED",
    "VERIFIED",
    "CONTRADICTED",
    "SUPERSEDED",
})

MEMORY_STATES = frozenset({
    "EPHEMERAL_TRACE",
    "SESSION_TRACE",
    "CANDIDATE_MEMORY",
    "PROMOTED_MEMORY",
    "CONSOLIDATED_MEMORY",
    "SUPERSEDED_MEMORY",
    "REJECTED_MEMORY",
})

GOVERNANCE_STATES = frozenset({
    "MENTIONED",
    "PROPOSED",
    "REQUESTED",
    "QUALIFIED",
    "HOLD",
    "BLOCK",
    "AUTHORIZED",
    "EXECUTED",
    "RECEIPTED",
    "REQUESTED_CANDIDATE",
})

STATE_RELATIONS = frozenset({"STATE", "TRACE_STATE"})
DIRECTIONS = frozenset({"source_to_target", "target_to_source", "bidirectional", "state_on_source"})
NO_PROVEN_CONNECTION = "NO_PROVEN_CONNECTION"


def _value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def validate_flow_fields(flow: object) -> None:
    family = _value(getattr(flow, "family"))
    relation_type = getattr(flow, "relation_type")
    source_object = getattr(flow, "source_object")
    target_object = getattr(flow, "target_object")
    state = getattr(flow, "state")
    direction = getattr(flow, "direction")
    provenance = getattr(flow, "provenance")
    confidence = getattr(flow, "confidence")
    metadata = getattr(flow, "metadata")

    if not source_object:
        raise ValueError("source_object is required")
    if direction not in DIRECTIONS:
        raise ValueError(f"invalid direction: {direction}")
    if provenance is None:
        raise ValueError("provenance must be explicit")
    if confidence is None:
        raise ValueError("confidence must be explicit")
    if not isinstance(metadata, Mapping):
        raise ValueError("metadata must be mapping-like")

    if family == "TEMPORAL_ORDER":
        _validate_temporal(relation_type, target_object, state)
    elif family == "CAUSAL_CLAIM":
        _validate_causal(relation_type, target_object, state)
    elif family == "EPISTEMIC_STATE":
        _validate_epistemic(relation_type, state)
    elif family == "MEMORY_LIFECYCLE":
        _validate_memory(relation_type, state, metadata)
    elif family == "GOVERNANCE_STATE":
        _validate_governance(relation_type, state, metadata, provenance)
    else:
        raise ValueError(f"unknown flow family: {family}")


def _validate_temporal(relation_type: str, target_object: object, state: object) -> None:
    allowed = TEMPORAL_COORDINATES | TEMPORAL_RELATIONS
    if relation_type not in allowed:
        raise ValueError(f"invalid temporal relation_type: {relation_type}")
    if relation_type in TEMPORAL_RELATIONS and not target_object:
        raise ValueError("temporal relation requires target_object")
    if relation_type in TEMPORAL_COORDINATES and state is None:
        raise ValueError("temporal coordinate requires state")


def _validate_causal(relation_type: str, target_object: object, state: object) -> None:
    allowed = CAUSAL_CLAIM_LEVELS | CAUSAL_RELATIONS
    if relation_type not in allowed:
        raise ValueError(f"invalid causal relation_type: {relation_type}")
    if not target_object:
        raise ValueError("causal claim requires target_object")
    if relation_type == "VALIDATED_CAUSAL_PROOF" and state != "validated":
        raise ValueError("validated causal proof requires explicit validated state")


def _validate_epistemic(relation_type: str, state: object) -> None:
    if relation_type not in STATE_RELATIONS:
        raise ValueError(f"invalid epistemic relation_type: {relation_type}")
    if state not in EPISTEMIC_STATES:
        raise ValueError(f"invalid epistemic state: {state}")


def _validate_memory(relation_type: str, state: object, metadata: Mapping[str, object]) -> None:
    if relation_type not in STATE_RELATIONS:
        raise ValueError(f"invalid memory relation_type: {relation_type}")
    if state not in MEMORY_STATES:
        raise ValueError(f"invalid memory state: {state}")
    if metadata.get("MEMORY_WRITE_AUTHORITY") is not False:
        raise ValueError("MEMORY_WRITE_AUTHORITY must remain FALSE")


def _validate_governance(
    relation_type: str,
    state: object,
    metadata: Mapping[str, object],
    provenance: Mapping[str, object],
) -> None:
    if relation_type not in STATE_RELATIONS:
        raise ValueError(f"invalid governance relation_type: {relation_type}")
    if state not in GOVERNANCE_STATES:
        raise ValueError(f"invalid governance state: {state}")
    if state in {"AUTHORIZED", "EXECUTED"}:
        authority_ref = metadata.get("authority_ref") or provenance.get("authority_ref")
        if not authority_ref:
            raise ValueError(f"{state} requires external authority reference")