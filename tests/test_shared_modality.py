"""Iteration 9: one written obligation modal is shared by coordinated infinitives.

"Paul doit lancer P et exécuter Q": the modal chain (modality, its tense, its
subject) scopes over the coordination (CoordinationRef "shared_modality");
the second infinitive is never an independent REQUESTED action. "Paul ne doit
ni lancer P ni arrêter Q" gives every member exactly the representation of
"Paul ne doit pas lancer P" (no must-not / not-required choice is made).
True directives ("Tu dois ...", "Il faut ...", imperatives) stay directives.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project

A = chr(39)


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


def _signature(u, gate, events):
    e = events.get(u.id)
    return (u.polarity, u.modality, u.tense_aspect, u.subject, u.pragmatic, gate[u.id],
            e.occurrence_claim.value if e else None, e.occurrence_derivation.rule if e else None)


@pytest.mark.parametrize("modal,tense", [("doit", "PRESENT"), ("devait", "PAST"), ("devra", "FUTURE")])
def test_bare_infinitives_share_the_obligation_modal(modal, tense):
    f, gate, events = _view(f"Paul {modal} lancer le test et exécuter le build.")
    (coord,) = f.coordinations
    assert (coord.construction, coord.members) == ("shared_modality", ("u1", "u2"))
    u1, u2 = f.units
    assert (u2.modality, u2.tense_aspect, u2.subject) == ("OBLIGATION", tense, "paul")
    assert u2.pragmatic != "REQUESTED" and not gate[u2.id]
    assert _signature(u2, gate, events) == _signature(u1, gate, events)
    assert events["u2"].occurrence_derivation.provenance["shared_modality"] == coord.id
    assert events["u1"].event_ref.event_id != events["u2"].event_ref.event_id



def test_bare_infinitives_share_final_object():
    f, gate, events = _view("Paul doit lancer et exécuter le test.")
    (coord,) = f.coordinations
    assert (coord.construction, coord.members) == ("shared_modality", ("u1", "u2"))
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], ["le test"]]
    assert _signature(f.units[0], gate, events) == _signature(f.units[1], gate, events)
    assert events["u1"].event_ref.event_id != events["u2"].event_ref.event_id


def test_shared_modality_preserves_explicit_member_objects():
    f, _, _ = _view("Paul doit lancer le build et exécuter le test.")
    assert [[a.text for a in u.objects] for u in f.units] == [["le build"], ["le test"]]


@pytest.mark.parametrize("text", [
    "Paul doit lancer le test et attendre.",
    "Paul devait lancer le test et attendre.",
    "Paul devra lancer le test et attendre.",
])
def test_object_before_modal_coordination_is_not_shared(text):
    f, _, _ = _view(text)
    (coord,) = f.coordinations
    assert coord.construction == "shared_modality"
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], []]
    assert [u.subject for u in f.units] == ["paul", "paul"]

def test_three_infinitives_share_the_modal():
    f, gate, _ = _view("Paul doit lancer le test, exécuter le build et arrêter le lot.")
    (coord,) = f.coordinations
    assert len(coord.members) == 3
    assert all(u.modality == "OBLIGATION" and u.pragmatic == "ASSERTED" and not gate[u.id] for u in f.units)


@pytest.mark.parametrize("modal", ["doit", "devait"])
def test_ni_under_obligation_matches_single_negated_obligation(modal):
    f, gate, events = _view(f"Paul ne {modal} ni lancer le test ni exécuter le build.")
    ref_f, ref_gate, ref_events = _view(f"Paul ne {modal} pas lancer le test.")
    ref = _signature(ref_f.units[0], ref_gate, ref_events)
    (coord,) = f.coordinations
    assert coord.construction == "ni_negative_coordination" and len(f.units) == 2
    for u in f.units:
        assert _signature(u, gate, events) == ref
        assert events[u.id].occurrence_derivation.provenance["shared_modality"] == coord.id


@pytest.mark.parametrize("text", [
    "Tu dois lancer le test et exécuter le build.",
    "Il faut lancer le test et exécuter le build.",
])
def test_true_directive_obligations_stay_directives_and_gated(text):
    f, gate, _ = _view(text)
    assert all(u.pragmatic == "REQUESTED" and gate[u.id] for u in f.units)


@pytest.mark.parametrize("text", [
    "Lance le test et exécute le build.",
    "Lancer le test et exécuter le build.",
    "Peux-tu lancer le test et exécuter le build ?",
    "Marie dit que Paul doit lancer le test et exécuter le build.",
])
def test_controls_have_no_shared_modality(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_modality" for c in f.coordinations)


@pytest.mark.parametrize("modal", ["faut", "fallait"])
def test_impersonal_obligation_ni_matches_single_negated_obligation(modal):
    f, gate, events = _view(f"Il ne {modal} ni lancer le test ni exécuter le build.")
    ref_f, ref_gate, ref_events = _view(f"Il ne {modal} pas lancer le test.")
    ref = _signature(ref_f.units[0], ref_gate, ref_events)
    assert all(_signature(u, gate, events) == ref for u in f.units)
