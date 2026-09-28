"""Iteration 8: one written auxiliary is shared by coordinated past participles.

The auxiliary/tense scopes over the coordination (CoordinationRef
"shared_auxiliary", or the verbal ni group): every licensed member gets the
same compound tense, the derivation names the group (shared_tense), and each
member stays a distinct event. Ambiguous attachment never shares.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)


def _claims(f):
    return {c.predicate_ref: c for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text,tense,claim", [
    ("Paul a lancé et exécuté le test.", "PAST", "ASSERTED_REALIZED"),
    ("Paul avait lancé et exécuté le test.", "PLUPERFECT", "ASSERTED_REALIZED"),
    ("Paul aura lancé et exécuté le test.", "FUTURE", "PROJECTED_FUTURE"),
    ("Paul a lancé le test et exécuté le build.", "PAST", "ASSERTED_REALIZED"),
    ("Paul a lancé, exécuté et préparé le test.", "PAST", "ASSERTED_REALIZED"),
])
def test_bare_participles_share_the_written_auxiliary(text, tense, claim):
    f = parse_utterance(text)
    (coord,) = f.coordinations
    assert (coord.kind, coord.construction) == ("AND", "shared_auxiliary")
    assert len(coord.members) == len(f.units)
    units, events = {u.id: u for u in f.units}, _claims(f)
    for i, m in enumerate(coord.members):
        assert units[m].tense_aspect == tense
        assert events[m].occurrence_claim.value == claim
        assert events[m].occurrence_derivation.provenance.get("shared_tense") == (coord.id if i else None)
    assert len({events[m].event_ref.event_id for m in coord.members}) == len(coord.members)



def test_bare_participles_share_subject_and_final_object():
    f = parse_utterance("Paul a lancé et exécuté le test.")
    (coord,) = f.coordinations
    assert (coord.construction, coord.members) == ("shared_auxiliary", ("u1", "u2"))
    assert [u.subject for u in f.units] == ["paul", "paul"]
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], ["le test"]]
    assert len({u.id for u in f.units}) == 2


def test_shared_auxiliary_preserves_explicit_member_objects():
    f = parse_utterance("Paul a lancé le build et exécuté le test.")
    assert [[a.text for a in u.objects] for u in f.units] == [["le build"], ["le test"]]

@pytest.mark.parametrize("aux,tense,claim", [
    ("a", "PAST", "ASSERTED_NOT_REALIZED"),
    ("avait", "PLUPERFECT", "ASSERTED_NOT_REALIZED"),
    ("aura", "FUTURE", "PROJECTED_FUTURE"),
])
def test_ni_members_share_the_auxiliary_tense(aux, tense, claim):
    f = parse_utterance(f"Paul n{A}{aux} ni lancé le test ni exécuté le build.")
    (coord,) = f.coordinations
    events = _claims(f)
    for m in coord.members:
        assert next(u for u in f.units if u.id == m).tense_aspect == tense
        assert events[m].occurrence_claim.value == claim
        assert events[m].occurrence_derivation.provenance["shared_tense"] == coord.id


def test_conditional_auxiliary_ni_stays_out_of_scope():
    f = parse_utterance(f"Paul n{A}aurait ni lancé le test ni exécuté le build.")
    assert f.coordinations == ()
    assert all(c.occurrence_claim.value not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
               for c in _claims(f).values())


@pytest.mark.parametrize("text", [
    "Paul a lancé le test et a exécuté le build.",
    "Paul a lancé le test.",
    "Marie dit que Paul a lancé le test et exécuté le build.",
    "Luc a vu le test que Paul a lancé et exécuté.",
    "Marie a vu Paul lancer et arrêter le test.",
    "Lance et exécute le test.",
    "Paul doit lancer le test et exécuter le build.",
])
def test_controls_have_no_shared_auxiliary(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_auxiliary" for c in f.coordinations)
