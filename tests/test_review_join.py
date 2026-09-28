"""ReviewJoin V0: read-only envelope around a caller-chosen center event.

It aggregates the connected meta-event component (OBSERVES, LEARNS_ABOUT,
REPORTS_ABOUT, BELIEVES_ABOUT) with occurrence and epistemic states copied as
they are. No truth scalar, no conflict resolution, no temporal enrichment, no
coreference between distinct events.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.review_join import ReviewEnvelope, build_review_envelope


def _eid(frame, predicate, nth=0):
    index = build_frame_event_index(frame)
    unit = [u for u in frame.units if u.predicate == predicate][nth]
    return index.event_for(unit.id).event_ref.event_id


def test_envelope_collects_connected_chain_without_flattening():
    frame = parse_utterance("Paul croit que Marie a dit que Jean a lancé le test.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE"))

    assert isinstance(env, ReviewEnvelope)
    assert [(e["predicate"], e["occurrence_status"]) for e in env.events] == [
        ("BELIEVE", "ASSERTED_OCCURRED"), ("SAY", "UNKNOWN"), ("EXECUTE", "REPORTED")]
    assert sorted(r.relation_kind.value for r in env.relations) == ["BELIEVES_ABOUT", "REPORTS_ABOUT"]
    run = next(e for e in env.events if e["predicate"] == "EXECUTE")
    assert "REPORTED" in run["epistemic_states"]


def test_center_choice_does_not_change_component():
    frame = parse_utterance("Paul croit que Marie a dit que Jean a lancé le test.")
    by_run = build_review_envelope(frame, _eid(frame, "EXECUTE"))
    by_say = build_review_envelope(frame, _eid(frame, "SAY"))

    assert [e["event_id"] for e in by_run.events] == [e["event_id"] for e in by_say.events]
    assert by_run.center_event != by_say.center_event


def test_observation_and_learning_chains_are_included():
    frame = parse_utterance("Paul dit que Marie a appris que Jean a lancé le test.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE"))

    assert sorted(r.relation_kind.value for r in env.relations) == ["LEARNS_ABOUT", "REPORTS_ABOUT"]
    frame = parse_utterance("Paul croit que Marie a vu Jean lancer le test.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE"))
    assert sorted(r.relation_kind.value for r in env.relations) == ["BELIEVES_ABOUT", "OBSERVES"]


def test_distinct_events_are_never_merged():
    frame = parse_utterance("Paul dit que Marie a lancé le test. Luc croit que Marie n'a pas lancé le test.")
    first = build_review_envelope(frame, _eid(frame, "EXECUTE", 0))
    second = build_review_envelope(frame, _eid(frame, "EXECUTE", 1))

    assert {e["predicate"] for e in first.events} == {"SAY", "EXECUTE"}
    assert {e["predicate"] for e in second.events} == {"BELIEVE", "EXECUTE"}
    assert not {e["event_id"] for e in first.events} & {e["event_id"] for e in second.events}
    assert [e["occurrence_status"] for e in second.events] == ["ASSERTED_OCCURRED", "NEGATED"]


def test_unrelated_event_stays_outside():
    frame = parse_utterance("Paul a lancé le build. Marie croit que Jean a lancé le test.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE", 0))

    assert [e["predicate"] for e in env.events] == ["EXECUTE"]
    assert env.relations == ()


def test_unresolved_and_non_event_targets_are_preserved():
    frame = parse_utterance("Paul dit bonjour.")
    env = build_review_envelope(frame, _eid(frame, "SAY"))
    assert [t.resolution_status.value for t in env.unresolved] == ["UNRESOLVED"]

    frame = parse_utterance("Paul dit que le système s'est arrêté.")
    env = build_review_envelope(frame, _eid(frame, "SAY"))
    assert [t.target_kind.value for t in env.non_event_targets] == ["PROPOSITION_TARGET"]


def test_envelope_has_no_truth_scalar_or_authority():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE"))

    assert env.metadata["truth"] is None
    assert env.metadata["conflict_resolution"] == "none"
    assert env.metadata["temporal_enrichment"] == "none"
    for key in ("MEMORY_WRITE", "AUTHORIZED_FLOW_CREATED", "EXECUTED_FLOW_CREATED", "VERIFIED_FLOW_CREATED", "KX108_CALLED"):
        assert env.metadata[key] == 0
    assert env.to_dict() == build_review_envelope(frame, _eid(frame, "EXECUTE")).to_dict()


def test_center_must_be_indexed():
    frame = parse_utterance("Paul dit que Marie a lancé le test.")
    with pytest.raises(ValueError):
        build_review_envelope(frame, "event:unknown")


# Nominal reference relations (R11 adapter) join several perspectives on one event.

def test_shared_target_join_through_explicit_nominal_references():
    frame = parse_utterance("Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE"))

    assert [e["predicate"] for e in env.events] == ["EXECUTE", "OBSERVE", "SAY"]
    assert sorted((r.relation_kind.value, r.status) for r in env.relations) == [
        ("OBSERVES", "nominal_reference"), ("REPORTS_ABOUT", "nominal_reference")]
    assert {r.target_event for r in env.relations} == {_eid(frame, "EXECUTE")}
    assert env.provenance["nominal_reference_adapter"] == "wired"


def test_ambiguous_nominal_reference_does_not_join():
    frame = parse_utterance("Paul a lancé le build et Paul a lancé le test. J'ai observé cet événement.")
    env = build_review_envelope(frame, _eid(frame, "EXECUTE", 1))

    assert [e["predicate"] for e in env.events] == ["EXECUTE"]
    assert env.relations == ()
