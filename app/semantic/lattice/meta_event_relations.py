"""Meta-event target selection and relations over an EventIndex.

A meta-event (REPORT, BELIEF, ...) targets exactly its IMMEDIATE structural
complement, read from typed parser relations. Zero relations leave the target
UNKNOWN; several are AMBIGUOUS (MULTIPLE_TARGETS_UNSUPPORTED). The selector
never falls back to the first, nearest or deepest candidate, never mints an
EventRef, and never touches target occurrence, truth, evidence or authority.
"""
from __future__ import annotations

from typing import AbstractSet, Any, Mapping

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_index import EventIndex
from app.semantic.lattice.primitives import UtteranceFrame

_SOURCE = "semantic_meta_event_relations"
MULTIPLE_TARGETS_UNSUPPORTED = "MULTIPLE_TARGETS_UNSUPPORTED"


def select_immediate_meta_target(
    frame: UtteranceFrame,
    source_predicate: str,
    relation_kinds: AbstractSet[str],
    event_index: EventIndex,
) -> EventTargetReference:
    """Resolve the immediate target of `source_predicate` through `relation_kinds`."""
    source = event_index.event_for(source_predicate)
    if source is None:
        raise ValueError(f"source predicate {source_predicate!r} has no indexed EventRef")
    units = {unit.id: unit for unit in frame.units}
    relations = [r for r in frame.relations if r.source == source_predicate and r.kind in relation_kinds]
    targets = list(dict.fromkeys(r.target for r in relations))
    base = {
        "source": _SOURCE,
        "source_frame": event_index.frame_ref,
        "source_span": units[source_predicate].span if source_predicate in units else None,
        "relation_kinds": sorted(relation_kinds),
        "target_rule": "immediate_structural",
    }

    if not targets:
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "no_immediate_relation")
    if len(targets) > 1:
        base["candidate_predicate_ids"] = targets
        return _unresolved(source, source_predicate, base, ResolutionStatus.AMBIGUOUS, MULTIPLE_TARGETS_UNSUPPORTED)

    target_predicate = targets[0]
    relation = next(r for r in relations if r.target == target_predicate)
    base.update({
        "parser_relation": relation.kind,
        "parser_evidence": relation.evidence,
        "target_predicate": target_predicate,
        "target_span": units[target_predicate].span if target_predicate in units else None,
    })
    if target_predicate not in units:
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "target_not_in_frame")
    if any(conflict.predicate_ref == target_predicate for conflict in event_index.conflicts):
        return _unresolved(source, source_predicate, base, ResolutionStatus.UNRESOLVED, "target_event_conflict")

    target = event_index.event_for(target_predicate)
    if target is None:
        base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
        return EventTargetReference(
            source_event=source.event_ref.event_id,
            source_predicate=source_predicate,
            target_kind=TargetKind.PROPOSITION_TARGET,
            resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
            target_predicate=target_predicate,
            target_event=None,
            provenance=base,
            confidence={"value": None, "calibrated": False},
            metadata=_metadata(None),
        )
    base["resolution_status"] = ResolutionStatus.RESOLVED_STRUCTURAL.value
    return EventTargetReference(
        source_event=source.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.EVENT_TARGET,
        resolution_status=ResolutionStatus.RESOLVED_STRUCTURAL,
        target_predicate=target_predicate,
        target_event=target.event_ref.event_id,
        provenance=base,
        confidence={"value": None, "calibrated": False},
        metadata=_metadata(target.occurrence_status.value),
    )


def _unresolved(source, source_predicate: str, provenance: dict[str, Any], status: ResolutionStatus,
                reason: str) -> EventTargetReference:
    provenance = dict(provenance, reason=reason, resolution_status=status.value)
    return EventTargetReference(
        source_event=source.event_ref.event_id,
        source_predicate=source_predicate,
        target_kind=TargetKind.UNKNOWN_TARGET,
        resolution_status=status,
        target_predicate=None,
        target_event=None,
        provenance=provenance,
        confidence={"value": None, "calibrated": False},
        metadata=_metadata(None),
    )


def _metadata(target_occurrence: str | None) -> Mapping[str, Any]:
    return {
        "target_rule": "immediate_structural",
        "target_occurrence_status": target_occurrence,
        "target_occurrence_promoted": False,
        "nearest_event_fallback": False,
        "first_candidate_fallback": False,
        "evidence_validated": False,
        "truth": None,
    }
