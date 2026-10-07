"""B7 mechanical unresolved detector (runtime determinism contract §4-§6).

Reads only explicit B6 / SENS markers of a StateEntry (field + marker prefix / link token); never the
user text, never a model. One explicit marker -> one CognitiveResolutionRequest, in canonical order
(field order below, then marker string); request ids derive from (origin state id, full origin digest, field, marker).
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from app.cognition.b7.contracts import (CognitiveResolutionRequest, UnresolvedKind, origin_full_digest,
                                        forbidden_operations_for, request_identity, required_candidate_kind_for)
from app.cognition.b7.router import eligible_roles
from app.harness.state_explicit.contracts import StateEntry, StateStatus

K = UnresolvedKind
FIELD_ORDER = ("unresolved_references", "contradictions", "ambiguities", "missing", "semantic_closure.reasons",
               "semantic_frame.oblique_arguments")
_AMBIGUITY = {
    "ambiguous_antecedent": K.COREFERENCE,                                                         # M2
    "condition_scope_ambiguous": K.CONDITIONAL_ATTACHMENT, "exception_condition_open": K.CONDITIONAL_ATTACHMENT,  # M5
    "temporal_scope_ambiguous": K.TEMPORAL_REFERENCE, "temporal_subordinate_open": K.TEMPORAL_REFERENCE,         # M6
    "occurrence_conflict_open": K.CONTRADICTION,                                                    # M8
    "infinitive_under_unrecognized_governor": K.UNKNOWN_TERM_OR_PREDICATE,                          # M9
    "complement_under_unresolved_governor": K.UNKNOWN_TERM_OR_PREDICATE,
    "unresolved_complement_governance": K.UNKNOWN_TERM_OR_PREDICATE,
}


def _missing_link(marker: str) -> str:
    parts = marker.split(":", 2)
    return re.split(r"[=:]", parts[2], maxsplit=1)[0] if len(parts) == 3 else ""


def classify_marker(field: str, marker: str) -> UnresolvedKind:
    """M1-M10: deterministic, explicit-marker-only classification (M10 = fail-closed fallback)."""
    if field == "unresolved_references":
        return K.COREFERENCE                                                                       # M1
    if field == "contradictions":
        return K.CONTRADICTION                                                                     # M7
    if field == "ambiguities":
        return _AMBIGUITY.get(marker.split(":", 1)[0], K.OTHER_EXPLICIT_UNRESOLVED)
    if field == "semantic_closure.reasons" and marker.startswith("event_reference:"):
        return K.COREFERENCE                                                                       # M3
    if field == "missing" and _missing_link(marker) == "detached_source_of":
        return K.SOURCE_SCOPE                                                                      # M4
    return K.OTHER_EXPLICIT_UNRESOLVED                                                             # M10


def make_request(entry: StateEntry, kind: UnresolvedKind, field: str, marker: str) -> CognitiveResolutionRequest:
    kind = UnresolvedKind(kind)
    origin_digest = entry.content_digest
    origin_full = origin_full_digest(entry)
    return CognitiveResolutionRequest(
        request_id=request_identity(entry.state_id, origin_full, field, marker),
        origin_state_id=entry.state_id, origin_state_type=entry.state_type, unresolved_kind=kind,
        problem_refs=(f"{field}:{marker}",), source_refs=(entry.source_ref,), provenance_refs=tuple(entry.provenance),
        context_refs=(), allowed_role_ids=eligible_roles(kind), forbidden_operations=forbidden_operations_for(kind),
        required_candidate_kind=required_candidate_kind_for(kind), uncertainty=tuple(entry.uncertainty),
        why_resolution_needed=f"explicit unresolved marker {field}:{marker}", original_state_digest=origin_digest,
        origin_full_digest=origin_full)


def _markers(payload: Any) -> Iterable[tuple[str, str]]:
    if not isinstance(payload, dict):
        return []
    found: dict[str, list[str]] = {f: [] for f in FIELD_ORDER}
    for field in ("unresolved_references", "contradictions", "ambiguities", "missing"):
        found[field] = [str(m) for m in payload.get(field) or []]
    closure = payload.get("semantic_closure") or {}
    # "frame:" reasons restate the frame fields above: skipped (deduplication, not loss)
    found["semantic_closure.reasons"] = [str(r) for r in closure.get("reasons") or [] if not str(r).startswith("frame:")]
    frame = payload.get("semantic_frame") or {}
    found["semantic_frame.oblique_arguments"] = [f"oblique_role_unresolved:{o.get('id')}"
                                                 for o in frame.get("oblique_arguments") or []
                                                 if isinstance(o, dict) and o.get("role") == "UNRESOLVED"]
    return [(f, m) for f in FIELD_ORDER for m in sorted(set(found[f]))]


def detect_unresolved(entry: StateEntry) -> tuple[CognitiveResolutionRequest, ...]:
    if entry.status == StateStatus.ERROR:
        return ()           # operational failure, not a cognitive problem (stays visible in B6)
    markers = list(_markers(entry.payload))
    if markers:
        return tuple(make_request(entry, classify_marker(f, m), f, m) for f, m in markers)
    if entry.status in (StateStatus.OPEN, StateStatus.UNKNOWN):
        return (make_request(entry, K.OTHER_EXPLICIT_UNRESOLVED, "status", entry.status.value),)
    return ()
