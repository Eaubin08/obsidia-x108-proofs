"""B7 Validation / Retranslation Gate (non-sovereign), derived working state, trusted-context admission.

Verdicts: ACCEPT_AS_STRUCTURED_CONTEXT | REJECT | STILL_UNRESOLVED — cognitive validation results, never
ALLOW / HOLD / BLOCK. Checks run in a fixed order; the first failure decides. ACCEPT creates a NEW
B6-compatible StateEntry (the origin is never mutated). Multiple surviving candidates never produce a
winner (no confidence, majority or provider priority). Only a typed B6 ContextPacket or an accepted
B7 result is admissible as trusted context; an arbitrary mapping never is.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from app.cognition.b7.contracts import (CandidateStatus, CognitiveResolutionCandidate, CognitiveResolutionRequest,
                                        CognitiveValidationVerdict, RequiredCandidateKind)
from app.harness.state_explicit.context_assembly import ContextPacket
from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility
from app.harness.state_explicit.registry import WorkingStateRegistry

V = CognitiveValidationVerdict
_REFERENT_SCALARS = ("antecedent",)
_REFERENT_LISTS = ("participants", "sources")
_TIME_SCALARS = ("anchor",)
_TIME_LISTS = ("times",)
_WORD = re.compile(r"[^\W_]+", re.UNICODE)
_NON_PHRASE = re.compile(r"[^\w\s'’-]", re.UNICODE)     # a claimed phrase never spans punctuation
_BLOCKER_FORM = {"unresolved_references": "unresolved_reference", "contradictions": "contradiction",
                 "ambiguities": "ambiguity", "missing": "missing"}
# closed proposed_resolution schema: every key is either validated below or explicitly descriptive
# (quoted_text / characterization / hypothesis never ground a referent); any other key is an
# unvalidated claim and is rejected (it would otherwise enter accepted context unchecked)
_VALIDATED_KEYS = frozenset({"mention", "antecedent", "participants", "sources", "anchor", "times", "relations"})
_DESCRIPTIVE_KEYS = frozenset({"quoted_text", "characterization", "hypothesis"})
_FORBIDDEN_CLAIMS = ("physical_chronology_established", "world_fact_established", "emits_act", "memory_write",
                     "kernel_mutation", "allowed_to_act", "allowed_to_decide", "decision_authority")


@dataclass(frozen=True)
class ValidationResult:
    verdict: CognitiveValidationVerdict
    reasons: tuple[str, ...]
    candidates: tuple[CognitiveResolutionCandidate, ...]
    derived_state: StateEntry | None = None


def _origin_raw(origin: StateEntry) -> str:
    payload = origin.payload if isinstance(origin.payload, dict) else {}
    return unicodedata.normalize("NFC", str(payload.get("raw") or (payload.get("semantic_frame") or {}).get("raw") or ""))


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(_WORD.findall(unicodedata.normalize("NFC", text).casefold()))


def _contains_phrase(haystack: tuple[str, ...], phrase: tuple[str, ...]) -> bool:
    n = len(phrase)
    return n > 0 and any(haystack[i:i + n] == phrase for i in range(len(haystack) - n + 1))


def _structured_referents(origin: StateEntry, anaphor_units: frozenset[str] = frozenset()) -> set[tuple[str, ...]]:
    """Referent phrases SENS already structured (unit subjects, object texts, coordination members).

    The objects of the unit carrying the mention being resolved are the anaphor itself ("Lance-le":
    object "le"), not candidate referents, and are not counted."""
    payload = origin.payload if isinstance(origin.payload, dict) else {}
    frame = payload.get("semantic_frame") or {}
    out: set[tuple[str, ...]] = set()
    for u in frame.get("units") or []:
        if isinstance(u, dict):
            out.add(_tokens(str(u.get("subject") or "")))
            if str(u.get("id")) not in anaphor_units:
                out.update(_tokens(str(o.get("text") or "")) for o in u.get("objects") or [] if isinstance(o, dict))
    for c in frame.get("coordinations") or []:
        if isinstance(c, dict):
            out.update(_tokens(str(t)) for t in c.get("member_texts") or [])
    out.discard(())
    return out


def _referent_admissible(value: Any, origin: StateEntry, anaphor_units: frozenset[str] = frozenset()) -> bool:
    """STRUCTURED_REFERENT_ONLY (human doctrine, docs/architecture/B7_STRUCTURED_REFERENT_ONLY_AMENDMENT_20261007.md):
    a referent is admissible only as an exact member of the origin's structured referent set. Raw text,
    lexicon, determiners or capitalization never establish a referent; no structure -> not admissible."""
    if not isinstance(value, str) or _NON_PHRASE.search(value):
        return False
    phrase = _tokens(value)
    return bool(phrase) and phrase in _structured_referents(origin, anaphor_units)


def _time_admissible(value: Any, origin: StateEntry) -> bool:
    """Linguistic temporal cue: exact token / phrase present in the original text, nothing more."""
    if not isinstance(value, str) or _NON_PHRASE.search(value):
        return False
    return _contains_phrase(_tokens(_origin_raw(origin)), _tokens(value))


def _origin_units(origin: StateEntry) -> set[str]:
    frame = (origin.payload or {}).get("semantic_frame") or {} if isinstance(origin.payload, dict) else {}
    return {str(u.get("id")) for u in frame.get("units") or [] if isinstance(u, dict)}


def _problem_markers(request: CognitiveResolutionRequest) -> list[str]:
    return [p.split(":", 1)[1] if ":" in p else p for p in request.problem_refs]


def _resolved_forms(request: CognitiveResolutionRequest) -> frozenset[str]:
    """Exact canonical forms of the unresolved item(s) this request addresses (no containment)."""
    forms: set[str] = set()
    for ref in request.problem_refs:
        field, _, marker = ref.partition(":")
        forms.update({ref, marker})
        if field in _BLOCKER_FORM:
            blocker = f"{_BLOCKER_FORM[field]}:{marker}"
            forms.update({blocker, f"frame:{blocker}"})
    forms.discard("")
    return frozenset(forms)


def _check(request: CognitiveResolutionRequest, cand: CognitiveResolutionCandidate, origin: StateEntry,
           provider_roles: Mapping[str, Iterable[Any]]) -> str | None:
    """First failing structural / conservation check, or None."""
    if cand.candidate_status != CandidateStatus.READY_FOR_VALIDATION:
        return "candidate_not_translated"
    if cand.request_id != request.request_id:
        return "request_id_mismatch"
    if cand.origin_state_id != request.origin_state_id or origin.state_id != request.origin_state_id:
        return "origin_state_id_mismatch"
    if cand.original_state_digest != request.original_state_digest or origin.content_digest != request.original_state_digest:
        return "original_state_digest_mismatch"
    if cand.candidate_kind != request.required_candidate_kind:
        return "candidate_kind_mismatch"
    if cand.proposer_role not in request.allowed_role_ids:
        return "role_not_eligible"
    roles = {getattr(r, "value", r) for r in provider_roles.get(cand.provider_ref, ())}
    if cand.proposer_role.value not in roles:
        return "provider_not_eligible_for_role"
    if cand.resolves != request.problem_refs:
        return "question_changed"
    if not set(request.provenance_refs) <= set(cand.provenance_refs):
        return "provenance_dropped"
    markers = _problem_markers(request)
    resolved = _resolved_forms(request)
    for item in request.uncertainty:
        # only the exact canonical item addressed by the request may disappear
        if item not in resolved and item not in cand.remaining_unknowns:
            return "unresolved_content_lost"
    origin_contradictions = (origin.payload or {}).get("contradictions") or [] if isinstance(origin.payload, dict) else []
    if not set(origin_contradictions) <= set(cand.contradictions):
        return "contradiction_hidden"
    proposal = cand.proposed_resolution
    if any(proposal.get(k) not in (None, False) for k in _FORBIDDEN_CLAIMS):
        return "forbidden_claim"
    if set(proposal) - _VALIDATED_KEYS - _DESCRIPTIVE_KEYS - set(_FORBIDDEN_CLAIMS):
        return "unvalidated_claim_key"
    referents = [proposal[k] for k in _REFERENT_SCALARS if k in proposal]
    referents += [v for k in _REFERENT_LISTS for v in proposal.get(k) or []]
    anaphor_units = frozenset(m.split(":", 1)[0] for m in markers if ":" in m)
    if not all(_referent_admissible(v, origin, anaphor_units) for v in referents):
        return "unsupported_content_invented"
    times = [proposal[k] for k in _TIME_SCALARS if k in proposal]
    times += [v for k in _TIME_LISTS for v in proposal.get(k) or []]
    if not all(_time_admissible(v, origin) for v in times):
        return "unsupported_content_invented"
    units = _origin_units(origin)
    for rel in proposal.get("relations") or []:
        if not isinstance(rel, dict) or {str(rel.get("source")), str(rel.get("target"))} - units:
            return "unsupported_relation_invented"
    if "mention" in proposal and proposal["mention"] not in markers:
        return "mention_not_in_request"
    return None


def _derive(request: CognitiveResolutionRequest, cand: CognitiveResolutionCandidate) -> StateEntry:
    payload = {
        "derived_from_state_id": request.origin_state_id, "resolution_request_id": request.request_id,
        "resolution_candidate_id": cand.candidate_id, "provider_ref": cand.provider_ref,
        "role_ref": cand.proposer_role.value, "unresolved_kind": request.unresolved_kind.value,
        "candidate_kind": cand.candidate_kind.value, "proposed_resolution": cand.proposed_resolution,
        "evidence_refs": list(cand.evidence_refs), "context_refs": list(cand.context_refs),
        "confidence_class": cand.confidence_class.value, "assumptions": list(cand.assumptions),
        "contradictions": list(cand.contradictions),
        "validation_verdict": V.ACCEPT_AS_STRUCTURED_CONTEXT.value,
        "physical_chronology_established": False, "world_fact_established": False,
        "structured_context_is_truth": False,
    }
    provenance = tuple(dict.fromkeys((*request.provenance_refs, *cand.provenance_refs,
                                      "app.cognition.b7.validation")))
    return StateEntry(state_id=f"b7:{cand.candidate_id}", state_type="B7_STRUCTURED_CONTEXT",
                      source_ref=f"app.cognition.b7:{request.request_id}", payload=payload, provenance=provenance,
                      uncertainty=cand.remaining_unknowns,
                      status=StateStatus.OPEN if cand.remaining_unknowns else StateStatus.KNOWN,
                      visibility=Visibility.LONG, tags=("b7", "derived"),
                      summary=f"B7 {request.unresolved_kind.value} candidate (validated context, not truth)")


def validate_candidate(request: CognitiveResolutionRequest, candidate: CognitiveResolutionCandidate, *,
                       origin: StateEntry, provider_roles: Mapping[str, Iterable[Any]]) -> ValidationResult:
    failure = _check(request, candidate, origin, provider_roles)
    if failure is not None:
        return ValidationResult(V.REJECT, (failure,), (candidate,))
    if candidate.candidate_kind == RequiredCandidateKind.CHARACTERIZATION_ONLY:
        return ValidationResult(V.STILL_UNRESOLVED, ("characterization_only_never_accepted",), (candidate,))
    if candidate.candidate_kind == RequiredCandidateKind.WORLD_REFERENCE_HYPOTHESIS:
        # B7 V1 has no admissible world / domain evidence source: a hypothesis never becomes context
        return ValidationResult(V.STILL_UNRESOLVED, ("no_admissible_world_evidence",), (candidate,))
    return ValidationResult(V.ACCEPT_AS_STRUCTURED_CONTEXT, (), (candidate,), _derive(request, candidate))


def validate_candidates(request: CognitiveResolutionRequest, candidates: Iterable[CognitiveResolutionCandidate], *,
                        origin: StateEntry, provider_roles: Mapping[str, Iterable[Any]]) -> ValidationResult:
    candidates = tuple(candidates)
    results = [validate_candidate(request, c, origin=origin, provider_roles=provider_roles) for c in candidates]
    accepted = [r for r in results if r.verdict == V.ACCEPT_AS_STRUCTURED_CONTEXT]
    if len(accepted) == 1 and len(candidates) == 1:
        return accepted[0]
    if len(accepted) >= 2 or (accepted and len(candidates) > 1):
        # JOIN != RESOLVE: surviving candidates are kept, never ranked into a winner
        return ValidationResult(V.STILL_UNRESOLVED, ("multiple_candidates_no_winner",), candidates)
    if any(r.verdict == V.STILL_UNRESOLVED for r in results):
        return ValidationResult(V.STILL_UNRESOLVED, ("no_acceptable_candidate",), candidates)
    return ValidationResult(V.REJECT, tuple(r.reasons[0] for r in results if r.reasons), candidates)


def register_derived(registry: WorkingStateRegistry, result: ValidationResult) -> StateEntry:
    """Register the NEW derived working entry; duplicate ids fail closed (no overwrite)."""
    if result.verdict != V.ACCEPT_AS_STRUCTURED_CONTEXT or result.derived_state is None:
        raise ValueError("only an accepted result produces working state")
    return registry.register(result.derived_state)


def admit_trusted_context(obj: Any) -> Any:
    """ARBITRARY_DICT != TRUSTED_CONTEXT: only a typed B6 ContextPacket or an accepted B7 result."""
    if isinstance(obj, ContextPacket):
        return obj
    if isinstance(obj, ValidationResult) and obj.verdict == V.ACCEPT_AS_STRUCTURED_CONTEXT \
            and isinstance(obj.derived_state, StateEntry):
        return obj.derived_state
    raise ValueError("not admissible as trusted context (typed B6 packet or accepted B7 result required)")
