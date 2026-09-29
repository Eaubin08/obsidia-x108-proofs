"""Semantic Closure over the event layer (master block 26): OUTPUT_EXISTS != SEMANTIC_CLOSURE.

A frame is semantically closed for its request only when nothing that its
meaning depends on is still open: the frame-level blockers (unresolved
references, contradictions, unanalysed content, structural ambiguity) and,
on the event layer, explicit event references ("ce lancement") that are
unresolved or ambiguous, meta-event targets that are ambiguous or broken
(a speech verb without a propositional complement is not open), and event
index conflicts. Every open reason is named; nothing is resolved, chosen,
promoted or authorised here. Truth values and evidence needs never block
closure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from app.semantic.lattice.event_coreference import ResolutionStatus
from app.semantic.lattice.event_index import EventIndex, build_frame_event_index
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.meta_event_relations import extract_belief_event_relations, extract_report_event_relations
from app.semantic.lattice.primitives import UtteranceFrame

SEMANTIC_CLOSURE_VERSION = "semantic_closure_v1"
_OPEN = {ResolutionStatus.UNRESOLVED, ResolutionStatus.AMBIGUOUS}
# a speech / belief verb without a propositional complement has no target to resolve
_NOT_OPEN_META_REASONS = {"no_immediate_relation"}


@dataclass(frozen=True)
class SemanticClosure:
    closed: bool
    reasons: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "reasons", tuple(self.reasons))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def semantic_closure(frame: UtteranceFrame, event_index: EventIndex | None = None) -> SemanticClosure:
    index = event_index if event_index is not None else build_frame_event_index(frame)
    reasons: list[str] = []
    if not frame.units:
        reasons.append("no_predicate_unit")
    reasons += [f"frame:{b}" for b in frame.closure_blockers]
    for ref in resolve_explicit_event_references(frame, index.events()).references:
        if ref.resolution_status in _OPEN:
            reasons.append(f"event_reference:{ref.resolution_status.value}:{ref.provenance.get('reason')}"
                           f":{ref.source_predicate}")
    for extractor in (extract_report_event_relations, extract_belief_event_relations):
        for target in extractor(frame, index).targets:
            reason = target.provenance.get("reason")
            if target.resolution_status in _OPEN and reason not in _NOT_OPEN_META_REASONS:
                reasons.append(f"meta_target:{target.resolution_status.value}:{reason}:{target.source_predicate}")
    reasons += [f"index_conflict:{c.reason}:{c.predicate_ref}" for c in index.conflicts
                if c.reason != "frame_mismatch"]
    reasons = list(dict.fromkeys(reasons))
    return SemanticClosure(
        closed=not reasons,
        reasons=tuple(reasons),
        metadata={
            "source": SEMANTIC_CLOSURE_VERSION,
            "frame_closure": frame.closure,
            "truth": None,
            "resolution": "none",
            "MEMORY_WRITE": 0,
            "KX108_CALLED": 0,
        },
    )
