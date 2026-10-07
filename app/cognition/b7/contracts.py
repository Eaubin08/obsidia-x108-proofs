"""B7 closed vocabularies and typed objects (B7 spec V1 + runtime determinism contract V1).

Every vocabulary is a closed str Enum: an unknown value raises ValueError (fail closed, never
coerced). Requests and candidates are immutable, strict-JSON, bounded and non-sovereign; strict JSON
and digests reuse the B6 canonical serializer. Nothing here decides, authorizes or acts:
decision authority stays KX108_ONLY.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from app.harness.state_explicit.contracts import BOUNDARY, canonical_json

MAX_REQUEST_CHARS = 32_768
MAX_CANDIDATE_CHARS = 32_768


class CandidateStatus(str, Enum):
    """Cognitive lifecycle only (never truth, authority or a validation verdict)."""
    PROPOSED = "PROPOSED"
    READY_FOR_VALIDATION = "READY_FOR_VALIDATION"


class CognitiveValidationVerdict(str, Enum):
    ACCEPT_AS_STRUCTURED_CONTEXT = "ACCEPT_AS_STRUCTURED_CONTEXT"
    REJECT = "REJECT"
    STILL_UNRESOLVED = "STILL_UNRESOLVED"


class UnresolvedKind(str, Enum):
    COREFERENCE = "COREFERENCE"
    SOURCE_SCOPE = "SOURCE_SCOPE"
    CONDITIONAL_ATTACHMENT = "CONDITIONAL_ATTACHMENT"
    TEMPORAL_REFERENCE = "TEMPORAL_REFERENCE"
    DEIXIS = "DEIXIS"
    ENTITY_IDENTITY = "ENTITY_IDENTITY"
    CONTRADICTION = "CONTRADICTION"
    UNKNOWN_TERM_OR_PREDICATE = "UNKNOWN_TERM_OR_PREDICATE"
    DOMAIN_SPECIFIC_AMBIGUITY = "DOMAIN_SPECIFIC_AMBIGUITY"
    WORLD_OR_PHYSICAL_REFERENCE = "WORLD_OR_PHYSICAL_REFERENCE"
    OTHER_EXPLICIT_UNRESOLVED = "OTHER_EXPLICIT_UNRESOLVED"


class RequiredCandidateKind(str, Enum):
    REFERENCE_BINDING = "REFERENCE_BINDING"
    SOURCE_SCOPE_INTERPRETATION = "SOURCE_SCOPE_INTERPRETATION"
    CONDITIONAL_ATTACHMENT_INTERPRETATION = "CONDITIONAL_ATTACHMENT_INTERPRETATION"
    TEMPORAL_REFERENCE_INTERPRETATION = "TEMPORAL_REFERENCE_INTERPRETATION"
    DEICTIC_BINDING = "DEICTIC_BINDING"
    ENTITY_BINDING = "ENTITY_BINDING"
    CONTRADICTION_ANALYSIS = "CONTRADICTION_ANALYSIS"
    TERM_OR_PREDICATE_INTERPRETATION = "TERM_OR_PREDICATE_INTERPRETATION"
    DOMAIN_INTERPRETATION = "DOMAIN_INTERPRETATION"
    WORLD_REFERENCE_HYPOTHESIS = "WORLD_REFERENCE_HYPOTHESIS"
    CHARACTERIZATION_ONLY = "CHARACTERIZATION_ONLY"


class ForbiddenOperation(str, Enum):
    """Structural restrictions of the cognitive path (never a KX108 verdict)."""
    DECIDE = "DECIDE"
    ACT = "ACT"
    SELF_AUTHORIZE = "SELF_AUTHORIZE"
    WRITE_DURABLE_MEMORY = "WRITE_DURABLE_MEMORY"
    WRITE_WORKING_STATE = "WRITE_WORKING_STATE"
    MUTATE_KERNEL = "MUTATE_KERNEL"
    MUTATE_ORIGIN_STATE = "MUTATE_ORIGIN_STATE"
    PROMOTE_TO_KNOWLEDGE = "PROMOTE_TO_KNOWLEDGE"
    BYPASS_VALIDATION = "BYPASS_VALIDATION"
    SELECT_WINNER = "SELECT_WINNER"
    PROPOSE_RESOLUTION = "PROPOSE_RESOLUTION"
    ESTABLISH_WORLD_FACT = "ESTABLISH_WORLD_FACT"
    ESTABLISH_PHYSICAL_CHRONOLOGY = "ESTABLISH_PHYSICAL_CHRONOLOGY"


class ConfidenceClass(str, Enum):
    """Descriptive only: HIGH != TRUE, LOW != FALSE."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class CognitiveRole(str, Enum):
    """Cognitive functions (ROLE != PROVIDER). Every role: no decision, no action, no durable write."""
    UNDERSTANDER = "UNDERSTANDER"
    INVESTIGATOR = "INVESTIGATOR"
    RESOLVER = "RESOLVER"
    CRITIC = "CRITIC"
    TRANSLATOR = "TRANSLATOR"
    COMPARATOR = "COMPARATOR"
    BUILDER_PROPOSER = "BUILDER_PROPOSER"


ROLE_RIGHTS: Mapping[str, Any] = {"may_decide": False, "may_act": False, "may_write_durable_memory": False,
                                  "authority": "NONE"}

_REQUIRED_KIND = {
    UnresolvedKind.COREFERENCE: RequiredCandidateKind.REFERENCE_BINDING,
    UnresolvedKind.SOURCE_SCOPE: RequiredCandidateKind.SOURCE_SCOPE_INTERPRETATION,
    UnresolvedKind.CONDITIONAL_ATTACHMENT: RequiredCandidateKind.CONDITIONAL_ATTACHMENT_INTERPRETATION,
    UnresolvedKind.TEMPORAL_REFERENCE: RequiredCandidateKind.TEMPORAL_REFERENCE_INTERPRETATION,
    UnresolvedKind.DEIXIS: RequiredCandidateKind.DEICTIC_BINDING,
    UnresolvedKind.ENTITY_IDENTITY: RequiredCandidateKind.ENTITY_BINDING,
    UnresolvedKind.CONTRADICTION: RequiredCandidateKind.CONTRADICTION_ANALYSIS,
    UnresolvedKind.UNKNOWN_TERM_OR_PREDICATE: RequiredCandidateKind.TERM_OR_PREDICATE_INTERPRETATION,
    UnresolvedKind.DOMAIN_SPECIFIC_AMBIGUITY: RequiredCandidateKind.DOMAIN_INTERPRETATION,
    UnresolvedKind.WORLD_OR_PHYSICAL_REFERENCE: RequiredCandidateKind.WORLD_REFERENCE_HYPOTHESIS,
    UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED: RequiredCandidateKind.CHARACTERIZATION_ONLY,
}

DEFAULT_FORBIDDEN_OPERATIONS: frozenset[ForbiddenOperation] = frozenset({
    ForbiddenOperation.DECIDE, ForbiddenOperation.ACT, ForbiddenOperation.SELF_AUTHORIZE,
    ForbiddenOperation.WRITE_DURABLE_MEMORY, ForbiddenOperation.WRITE_WORKING_STATE,
    ForbiddenOperation.MUTATE_KERNEL, ForbiddenOperation.MUTATE_ORIGIN_STATE,
    ForbiddenOperation.PROMOTE_TO_KNOWLEDGE, ForbiddenOperation.BYPASS_VALIDATION})

_ADDED_FORBIDDEN = {
    UnresolvedKind.CONTRADICTION: {ForbiddenOperation.SELECT_WINNER},
    UnresolvedKind.TEMPORAL_REFERENCE: {ForbiddenOperation.ESTABLISH_PHYSICAL_CHRONOLOGY},
    UnresolvedKind.WORLD_OR_PHYSICAL_REFERENCE: {ForbiddenOperation.ESTABLISH_WORLD_FACT,
                                                 ForbiddenOperation.ESTABLISH_PHYSICAL_CHRONOLOGY},
    UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED: {ForbiddenOperation.PROPOSE_RESOLUTION},
}


def required_candidate_kind_for(kind: UnresolvedKind) -> RequiredCandidateKind:
    return _REQUIRED_KIND[UnresolvedKind(kind)]


def forbidden_operations_for(kind: UnresolvedKind) -> frozenset[ForbiddenOperation]:
    return DEFAULT_FORBIDDEN_OPERATIONS | frozenset(_ADDED_FORBIDDEN.get(UnresolvedKind(kind), ()))


def digest(value: Any, prefix: str = "") -> str:
    return prefix + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:16]


def full_digest(value: Any, prefix: str = "") -> str:
    """B7 identity digest: full SHA-256 (64 hex, 256 bits) over strict canonical JSON; never truncated."""
    return prefix + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (frozenset, set)):
        return sorted(_plain(v) for v in value)
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    return value


@dataclass(frozen=True)
class CognitiveResolutionRequest:
    request_id: str
    origin_state_id: str
    origin_state_type: str
    unresolved_kind: UnresolvedKind
    problem_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    context_refs: tuple[str, ...]
    allowed_role_ids: frozenset[CognitiveRole]
    forbidden_operations: frozenset[ForbiddenOperation]
    required_candidate_kind: RequiredCandidateKind
    uncertainty: tuple[str, ...]
    why_resolution_needed: str
    original_state_digest: str

    def __post_init__(self) -> None:
        if len(canonical_json(self.to_dict())) > MAX_REQUEST_CHARS:
            raise ValueError(f"request exceeds {MAX_REQUEST_CHARS} chars")

    def to_dict(self) -> dict[str, Any]:
        return {f: _plain(getattr(self, f)) for f in self.__dataclass_fields__}


@dataclass(frozen=True)
class CognitiveResolutionCandidate:
    candidate_id: str
    request_id: str
    origin_state_id: str
    original_state_digest: str
    candidate_kind: RequiredCandidateKind
    proposer_role: CognitiveRole
    provider_ref: str
    resolves: tuple[str, ...]
    proposed_resolution_json: str
    evidence_refs: tuple[str, ...]
    context_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    confidence_class: ConfidenceClass
    remaining_unknowns: tuple[str, ...]
    contradictions: tuple[str, ...]
    assumptions: tuple[str, ...]
    candidate_status: CandidateStatus
    candidate_digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_status", CandidateStatus(self.candidate_status))
        if len(canonical_json(self.to_dict())) > MAX_CANDIDATE_CHARS:
            raise ValueError(f"candidate exceeds {MAX_CANDIDATE_CHARS} chars")

    @property
    def proposed_resolution(self) -> dict[str, Any]:
        return json.loads(self.proposed_resolution_json)       # a fresh copy on every read

    def to_dict(self) -> dict[str, Any]:
        d = {f: _plain(getattr(self, f)) for f in self.__dataclass_fields__ if f != "proposed_resolution_json"}
        d["proposed_resolution"] = self.proposed_resolution
        return d


_IDENTITY_EXCLUDED = frozenset({"candidate_id", "candidate_digest", "candidate_status", "proposed_resolution_json"})


def candidate_identity(candidate: "CognitiveResolutionCandidate") -> tuple[str, str]:
    """(candidate_id, candidate_digest) bound to the canonical typed candidate content.

    Identity payload = every typed field except the identity fields themselves and the lifecycle
    status (gate-checked separately); proposed_resolution is included in parsed canonical form.
    Strict canonical JSON + sha256 (same digest helper as the rest of B7); no repr, no randomness."""
    payload = {f: _plain(getattr(candidate, f)) for f in candidate.__dataclass_fields__ if f not in _IDENTITY_EXCLUDED}
    payload["proposed_resolution"] = candidate.proposed_resolution
    candidate_digest = full_digest(payload, "b7dig_")
    return "b7cand_" + candidate_digest[len("b7dig_"):], candidate_digest


__all__ = ["BOUNDARY", "MAX_CANDIDATE_CHARS", "MAX_REQUEST_CHARS", "CandidateStatus", "CognitiveValidationVerdict",
           "UnresolvedKind", "RequiredCandidateKind", "ForbiddenOperation", "ConfidenceClass", "CognitiveRole",
           "ROLE_RIGHTS", "DEFAULT_FORBIDDEN_OPERATIONS", "required_candidate_kind_for", "forbidden_operations_for",
           "CognitiveResolutionRequest", "CognitiveResolutionCandidate", "digest", "full_digest", "candidate_identity"]
