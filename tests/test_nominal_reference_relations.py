"""R11 adapter: explicit nominal event reference -> meta-event relation.

The hardened resolver stays pure; this adapter only turns a RESOLVED_STRUCTURAL
reference governed by an indexed meta-event into the matching typed relation.
Ambiguous / unresolved / occurrence-conflict references are never bound, a
structural target takes precedence, and target occurrence is never promoted.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.events import EventReferenceRelation, EventRelationKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.meta_event_relations import extract_nominal_reference_relations


def _run(text: str, **kwargs):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    return frame, index, extract_nominal_reference_relations(frame, index, **kwargs)


def _eid(frame, index, predicate, nth=0):
    unit = [u for u in frame.units if u.predicate == predicate][nth]
    return index.event_for(unit.id).event_ref.event_id


@pytest.mark.parametrize("text, governor, kind", [
    ("Paul a lancé le test. J'ai observé ce lancement.", "OBSERVE", EventRelationKind.OBSERVES),
    ("Paul a lancé le test. Marie a mentionné ce lancement.", "SAY", EventRelationKind.REPORTS_ABOUT),
    ("Paul a lancé le test. J'ai appris ce lancement.", "LEARN", EventRelationKind.LEARNS_ABOUT),
    ("Paul a lancé le test. Je crois ce lancement.", "BELIEVE", EventRelationKind.BELIEVES_ABOUT),
])
def test_resolved_nominal_reference_becomes_typed_relation(text, governor, kind):
    frame, index, result = _run(text)

    assert len(result.relations) == 1
    rel = result.relations[0]
    assert rel.relation_kind is kind
    assert rel.source_event == _eid(frame, index, governor)
    assert rel.target_event == _eid(frame, index, "EXECUTE")
    assert rel.metadata["target_rule"] == "explicit_nominal_reference"
    assert rel.metadata["coreference_calibrated"] is False
    assert 0 < rel.metadata["coreference_confidence"] < 1
    assert rel.metadata["target_occurrence_status"] == "ASSERTED_OCCURRED"
    assert rel.metadata["target_occurrence_promoted"] is False
    assert rel.provenance["surface_reference"] == "ce lancement"


def test_meta_event_nominal_targets_the_observation_not_the_inner_action():
    frame, index, result = _run("Paul dit qu'il a vu Marie lancer le test. Luc a mentionné cette observation.")

    assert [(r.relation_kind, r.target_event) for r in result.relations] == [
        (EventRelationKind.REPORTS_ABOUT, _eid(frame, index, "OBSERVE"))]


@pytest.mark.parametrize("text, reason", [
    ("Paul a lancé le test. Marie a rapporté ce lancement.", "no_governing_event"),
    ("Paul a lancé le test. Luc a vérifié ce lancement.", "governor_not_meta_event"),
    ("Paul n'a pas lancé le test. J'ai observé ce lancement.", "reference_not_resolved"),
    ("Paul a lancé le build et Paul a lancé le test. J'ai observé cet événement.", "reference_not_resolved"),
])
def test_unbindable_references_create_no_relation(text, reason):
    _, _, result = _run(text)

    assert result.relations == ()
    assert result.metadata["SKIPPED"] == {reason: 1}


def test_structural_target_takes_precedence():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    index = build_frame_event_index(frame)
    observe = _eid(frame, index, "OBSERVE")
    structural = (EventReferenceRelation(EventRelationKind.OBSERVES, observe, "event:structural"),)
    result = extract_nominal_reference_relations(frame, index, structural_relations=structural)

    assert result.relations == ()
    assert result.metadata["SKIPPED"] == {"structural_target_precedence": 1}


def test_adapter_is_non_mutating_and_non_authoritative():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement.")
    index = build_frame_event_index(frame)
    before = {p: c.to_dict() for p, c in index.by_predicate.items()}
    result = extract_nominal_reference_relations(frame, index)

    assert {p: c.to_dict() for p, c in index.by_predicate.items()} == before
    for key in ("VERIFIED_FLOW_CREATED", "MEMORY_WRITE", "AUTHORIZED_FLOW_CREATED", "TARGET_OCCURRENCE_PROMOTIONS",
                "CROSS_MESSAGE_BINDINGS", "LATEST_EVENT_BINDINGS"):
        assert result.metadata[key] == 0


def test_cross_frame_references_are_never_bound():
    frame = parse_utterance("J'ai observé ce lancement.")
    index = build_frame_event_index(frame)
    result = extract_nominal_reference_relations(frame, index)

    assert result.relations == ()
