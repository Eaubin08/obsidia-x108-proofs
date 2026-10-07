"""B7 proposal intake and TRANSLATOR: raw provider mapping -> typed candidate, or ValueError (REJECT).

No model call, no inference: every field must be supplied (nothing is invented), the schema is closed
(an unknown or authority-bearing field is rejected), enums are closed, content is strict JSON and
bounded. Identity mismatches with the request are left to the validation gate.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

from app.cognition.b7.contracts import (MAX_CANDIDATE_CHARS, CandidateStatus, CognitiveResolutionCandidate,
                                        CognitiveResolutionRequest, CognitiveRole, ConfidenceClass,
                                        RequiredCandidateKind, candidate_identity)
from app.harness.state_explicit.contracts import canonical_json

_STR = ("request_id", "origin_state_id", "original_state_digest", "provider_ref")
_LISTS = ("resolves", "evidence_refs", "context_refs", "provenance_refs", "remaining_unknowns", "contradictions",
          "assumptions")
_FIELDS = frozenset(_STR + _LISTS + ("candidate_kind", "proposer_role", "confidence_class", "proposed_resolution"))


def _build(raw: Mapping[str, Any], request: CognitiveResolutionRequest,
           status: CandidateStatus) -> CognitiveResolutionCandidate:
    if not isinstance(raw, Mapping):
        raise ValueError("candidate must be a mapping")
    extra = set(raw) - _FIELDS
    if extra:
        raise ValueError(f"unknown or authority-bearing candidate fields: {sorted(extra)}")
    missing = _FIELDS - set(raw)
    if missing:
        raise ValueError(f"missing candidate fields (never invented): {sorted(missing)}")
    text = canonical_json(dict(raw))                       # strict JSON before anything else
    if len(text) > MAX_CANDIDATE_CHARS:
        raise ValueError(f"candidate exceeds {MAX_CANDIDATE_CHARS} chars")
    for name in _STR:
        if not isinstance(raw[name], str) or not raw[name]:
            raise ValueError(f"{name} must be a non-empty string")
    for name in _LISTS:
        if not isinstance(raw[name], list) or not all(isinstance(v, str) for v in raw[name]):
            raise ValueError(f"{name} must be a list of strings")
    if not isinstance(raw["proposed_resolution"], Mapping):
        raise ValueError("proposed_resolution must be a mapping")
    draft = CognitiveResolutionCandidate(
        candidate_id="b7cand_pending", request_id=raw["request_id"], origin_state_id=raw["origin_state_id"],
        original_state_digest=raw["original_state_digest"],
        candidate_kind=RequiredCandidateKind(raw["candidate_kind"]), proposer_role=CognitiveRole(raw["proposer_role"]),
        provider_ref=raw["provider_ref"], resolves=tuple(raw["resolves"]),
        proposed_resolution_json=canonical_json(dict(raw["proposed_resolution"])),
        evidence_refs=tuple(raw["evidence_refs"]), context_refs=tuple(raw["context_refs"]),
        provenance_refs=tuple(raw["provenance_refs"]), confidence_class=ConfidenceClass(raw["confidence_class"]),
        remaining_unknowns=tuple(raw["remaining_unknowns"]), contradictions=tuple(raw["contradictions"]),
        assumptions=tuple(raw["assumptions"]), candidate_status=status, candidate_digest="b7dig_pending")
    candidate_id, candidate_digest = candidate_identity(draft)     # the single canonical identity path
    return dataclasses.replace(draft, candidate_id=candidate_id, candidate_digest=candidate_digest)


def propose(raw: Mapping[str, Any], request: CognitiveResolutionRequest) -> CognitiveResolutionCandidate:
    """Typed proposal as emitted by a proposing role: status PROPOSED (not yet translated)."""
    return _build(raw, request, CandidateStatus.PROPOSED)


def translate(raw: Mapping[str, Any], request: CognitiveResolutionRequest) -> CognitiveResolutionCandidate:
    """TRANSLATOR: normalized typed candidate, status READY_FOR_VALIDATION; invalid input -> ValueError."""
    return _build(raw, request, CandidateStatus.READY_FOR_VALIDATION)
