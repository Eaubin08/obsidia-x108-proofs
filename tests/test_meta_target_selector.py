"""Shared immediate meta-target selector: exactly one immediate structural
relation resolves; zero stays UNKNOWN; several are AMBIGUOUS. Never the
first, nearest or deepest candidate.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from app.semantic.lattice.event_coreference import ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_index import build_event_index, build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import MULTIPLE_TARGETS_UNSUPPORTED, select_immediate_meta_target
from app.semantic.lattice.primitives import LatticeRelation, RelationKind

REPORTS = frozenset({RelationKind.REPORTS.value})
BELIEVES = frozenset({RelationKind.BELIEVES.value})


def _unit(frame, predicate, nth=0):
    return [u for u in frame.units if u.predicate == predicate][nth]


def test_single_immediate_relation_resolves_to_indexed_event():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    index = build_frame_event_index(frame)
    say, run = _unit(frame, "SAY"), _unit(frame, "EXECUTE")
    ref = select_immediate_meta_target(frame, say.id, REPORTS, index)

    assert ref.target_kind is TargetKind.EVENT_TARGET
    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.source_event == index.event_for(say.id).event_ref.event_id
    assert ref.target_event == index.event_for(run.id).event_ref.event_id
    assert ref.target_predicate == run.id
    assert ref.provenance["parser_relation"] == "REPORTS"
    assert ref.metadata["target_occurrence_status"] == OccurrenceStatus.REPORTED.value
    assert ref.metadata["target_occurrence_promoted"] is False


def test_nested_chain_selects_immediate_not_deepest():
    frame = parse_utterance("Paul croit que Marie pense que Jean a lancé le test.")
    index = build_frame_event_index(frame)
    outer, inner = _unit(frame, "BELIEVE", 0), _unit(frame, "BELIEVE", 1)
    ref = select_immediate_meta_target(frame, outer.id, BELIEVES, index)

    assert ref.target_predicate == inner.id
    assert ref.target_event == index.event_for(inner.id).event_ref.event_id


def test_report_can_target_an_observation_meta_event():
    frame = parse_utterance("Paul dit qu'il a vu Marie lancer le test.")
    index = build_frame_event_index(frame)
    observe = _unit(frame, "OBSERVE")
    ref = select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, index)

    assert ref.target_predicate == observe.id
    assert ref.target_event == index.event_for(observe.id).event_ref.event_id


def test_no_immediate_relation_is_unknown():
    frame = parse_utterance("Paul dit bonjour.")
    index = build_frame_event_index(frame)
    ref = select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, index)

    assert ref.target_kind is TargetKind.UNKNOWN_TARGET
    assert ref.resolution_status is ResolutionStatus.UNRESOLVED
    assert ref.target_event is None and ref.target_predicate is None


def test_relation_kind_filter_is_strict():
    frame = parse_utterance("Paul croit que Marie a lancé le test.")
    index = build_frame_event_index(frame)
    ref = select_immediate_meta_target(frame, _unit(frame, "BELIEVE").id, REPORTS, index)

    assert ref.resolution_status is ResolutionStatus.UNRESOLVED


def test_multiple_immediate_relations_are_ambiguous_not_first():
    frame = parse_utterance("Paul dit que Marie a lancé le build et Jean a lancé le test.")
    say = _unit(frame, "SAY")
    runs = [u for u in frame.units if u.predicate == "EXECUTE"]
    extra = LatticeRelation(RelationKind.REPORTS.value, say.id, runs[-1].id, evidence="test")
    forked = replace(frame, relations=frame.relations + (extra,))
    index = build_event_index(forked, extract_event_candidates(forked))
    ref = select_immediate_meta_target(forked, say.id, REPORTS, index)

    assert ref.resolution_status is ResolutionStatus.AMBIGUOUS
    assert ref.target_kind is TargetKind.UNKNOWN_TARGET
    assert ref.target_event is None and ref.target_predicate is None
    assert ref.provenance["reason"] == MULTIPLE_TARGETS_UNSUPPORTED
    assert len(ref.provenance["candidate_predicate_ids"]) == 2


def test_target_without_event_is_proposition_target():
    frame = parse_utterance("Paul dit que le système s'est arrêté.")
    index = build_frame_event_index(frame)
    stop = _unit(frame, "STOP")
    assert index.event_for(stop.id) is None
    ref = select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, index)

    assert ref.target_kind is TargetKind.PROPOSITION_TARGET
    assert ref.resolution_status is ResolutionStatus.RESOLVED_STRUCTURAL
    assert ref.target_predicate == stop.id and ref.target_event is None


def test_conflicting_target_identity_stays_unresolved():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    base = extract_event_candidates(frame)
    run = _unit(frame, "EXECUTE")
    clash = tuple(replace(c, occurrence_status=OccurrenceStatus.NEGATED) for c in base if c.predicate_ref == run.id)
    index = build_event_index(frame, base, clash)
    ref = select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, index)

    assert ref.resolution_status is ResolutionStatus.UNRESOLVED
    assert ref.target_event is None
    assert ref.provenance["reason"] == "target_event_conflict"


def test_source_must_be_an_indexed_event():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    empty = build_event_index(frame)
    with pytest.raises(ValueError):
        select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, empty)


def test_selector_does_not_mutate_index_candidates():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    index = build_frame_event_index(frame)
    before = {p: c.to_dict() for p, c in index.by_predicate.items()}
    select_immediate_meta_target(frame, _unit(frame, "SAY").id, REPORTS, index)

    assert {p: c.to_dict() for p, c in index.by_predicate.items()} == before
