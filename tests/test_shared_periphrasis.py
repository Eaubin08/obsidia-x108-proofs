"""Coordination P2: one written near-future "aller" is shared by coordinated infinitives.

"Paul va lancer P et exécuter Q": the periphrasis (NEAR_FUTURE, its subject)
scopes over the coordination (CoordinationRef "shared_periphrasis", provenance
shared_tense); "exécuter Q" is exactly "Paul va exécuter Q", never an
injunctive REQUESTED infinitive. Imperative "Va lancer ...", a negated "aller"
(negative scope held) and a subordinated host are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


def _signature(u, gate, events):
    e = events.get(u.id)
    return (u.verb_form, u.polarity, u.subject, u.tense_aspect, u.pragmatic, u.role, u.action_agent,
            u.request_target, gate[u.id], e.occurrence_claim.value if e else None)


@pytest.mark.parametrize("text,lead,tail", [
    ("Paul va lancer P et exécuter Q.", "Paul va", "."),
    ("Je vais lancer P et exécuter Q.", "Je vais", "."),
    ("Tu vas lancer P et exécuter Q.", "Tu vas", "."),
    ("Paul allait lancer P et exécuter Q.", "Paul allait", "."),
    ("Vas-tu lancer P et exécuter Q ?", "Vas-tu", " ?"),
    ("Paul va lancer P, vérifier Q et arrêter R.", "Paul va", "."),
])
def test_infinitives_share_the_near_future_periphrasis(text, lead, tail):
    f, gate, events = _view(text)
    (coord,) = f.coordinations
    assert coord.construction == "shared_periphrasis" and coord.members == tuple(u.id for u in f.units)
    for u in f.units:
        obj = u.objects[0].text if u.objects else ""
        ref_f, ref_gate, ref_events = _view(f"{lead} {u.lemma} {obj}".rstrip() + tail)
        assert _signature(u, gate, events) == _signature(ref_f.units[0], ref_gate, ref_events)
        assert u.pragmatic != "REQUESTED" and not gate[u.id]
    for u in f.units[1:]:
        if u.id in events:
            assert events[u.id].occurrence_derivation.provenance["shared_tense"] == coord.id
    ids = [events[u.id].event_ref.event_id for u in f.units if u.id in events]
    assert len(ids) == len(set(ids)) and coord.id not in events
    assert f.operator_scopes == ()


def test_shared_final_object_under_periphrasis():
    f, _, _ = _view("Paul va lancer et exécuter le test.")
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], ["le test"]]


@pytest.mark.parametrize("text", [
    "Va lancer P et exécuter Q.",                  # imperative "va": no subject, still a request
    "Paul ne va pas lancer P et exécuter Q.",      # negated operator scope: held doctrine
    "Lance R si Paul va lancer P et exécuter Q.",  # subordinated host stays open
])
def test_periphrasis_not_shared_outside_the_contract(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_periphrasis" for c in f.coordinations)


def test_imperative_aller_stays_a_gated_request():
    f, gate, _ = _view("Va lancer P et exécuter Q.")
    assert all(u.pragmatic == "REQUESTED" and gate[u.id] for u in f.units)
