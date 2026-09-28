"""Iteration 7: verbal "ne [AUX] ni V1 ... ni V2" shares its negation structurally.

Each member is negated by the ni coordination itself (negator "ni"), not
copied from the first member; members stay distinct units/events grouped by
a structural CoordinationRef (construction "ni_negative_coordination", no
occurrence, no event). Nominal "ni" (one event, coordinated objects) is
unchanged; modal and clausal "ni" belong to the shared-operator iteration.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)
ASSERTED_REALIZED = "ASSERTED_REALIZED"


@pytest.mark.parametrize("text,n", [
    ("Paul n" + A + "a ni lancé le test ni arrêté le build.", 2),
    ("Paul n" + A + "a ni lancé le test ni exécuté le build.", 2),
    ("Paul n" + A + "a ni lancé le test, ni exécuté le build, ni arrêté le lot.", 3),
    ("Paul n" + A + "a ni lancé le test ni exécuté le build ni arrêté le lot.", 3),
    ("Nadia n" + A + "est ni partie ni revenue.", None),
])
def test_verbal_ni_members_are_negated_by_the_coordination(text, n):
    f = parse_utterance(text)
    if n is None:
        return
    (coord,) = f.coordinations
    assert (coord.kind, coord.construction, len(coord.members)) == ("AND", "ni_negative_coordination", n)
    units = {u.id: u for u in f.units}
    for m in coord.members:
        assert (units[m].polarity, units[m].negator) == ("negative", "ni")
    assert [(r.source, r.target, r.evidence) for r in f.relations if r.kind == "COORDINATES"] == \
        [(a, b, "ni") for a, b in zip(coord.members, coord.members[1:])]
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    assert coord.id not in events
    for m in coord.members:
        if m in events:
            assert events[m].occurrence_claim.value != ASSERTED_REALIZED
            assert events[m].occurrence_derivation.provenance["shared_negation"] == coord.id


@pytest.mark.parametrize("text", [
    "Paul ne lance ni le test ni le build.",
    "Ne lance ni le test ni le build.",
    "Si Paul ne lance ni le test ni le build, Luc attend.",
    "Ni Paul ni Nadia n" + A + "ont lancé le test.",
])
def test_nominal_ni_is_one_negated_event_unchanged(text):
    f = parse_utterance(text)
    assert f.coordinations == ()
    assert f.units[0].polarity == "negative"


@pytest.mark.parametrize("text", [
    "Il ne doit ni lancer le test ni arrêter le build.",
    "Marie n" + A + "a ni appris que Paul a lancé le test ni dit que Nadia a lancé le build.",
])
def test_modal_and_clausal_ni_are_out_of_scope_and_unchanged(text):
    f = parse_utterance(text)
    assert not any(c.construction == "ni_negative_coordination" for c in f.coordinations)


@pytest.mark.parametrize("text,expected", [
    ("Paul a lancé le test et arrêté le build.", "positive"),
    ("Paul n" + A + "a pas lancé le test.", "negative"),
    ("Paul a lancé le test et Nadia n" + A + "a pas lancé le build.", None),
])
def test_controls(text, expected):
    f = parse_utterance(text)
    assert not any(c.construction == "ni_negative_coordination" for c in f.coordinations)
    if expected is not None:
        assert f.units[0].polarity == expected


@pytest.mark.parametrize("text", [
    "Il n" + A + "a ni lancer le test ni arrêter le build.",
    "Il n" + A + "a ni lancé le test ni arrêter le build.",
    "Paul n" + A + "a ni lancé le test ni le build.",
])
def test_non_participle_members_leave_the_group_unchanged(text):
    f = parse_utterance(text)
    assert f.coordinations == ()
    assert not any(u.negator == "ni" and u.pragmatic == "FORBIDDEN" for u in f.units)


def test_future_or_conditional_auxiliary_is_in_scope_with_its_tense():
    # the shared auxiliary tense is rebuilt on each member (iteration 8)
    f = parse_utterance("Paul n" + A + "aura ni lancé le test ni arrêté le build.")
    (coord,) = f.coordinations
    for c in build_frame_event_index(f).events():
        assert c.occurrence_claim.value == "PROJECTED_FUTURE"


def test_pluperfect_auxiliary_is_in_scope():
    f = parse_utterance("Paul n" + A + "avait ni lancé le test ni arrêté le build.")
    (coord,) = f.coordinations
    assert all(u.polarity == "negative" for u in f.units if u.id in coord.members)
