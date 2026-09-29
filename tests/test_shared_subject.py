"""Coordination P1: a bare present verb shares the explicit subject it agrees with.

"Paul lance P et exécute Q": "exécute" is the present of Paul (CoordinationRef
"shared_subject"), exactly what "Paul exécute Q." would be; it is never an
imperative request of the addressee. A form without an imperative reading
("exécutes", "exécutent") always shares; an imperative-ambiguous form shares
only when its person agrees ("Paul lance P et exécutez Q" stays imperative).
Subordinated hosts (si, que, relative) never share.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.lexicon import lookup
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


@pytest.mark.parametrize("text,subject,refs", [
    ("Paul lance P et exécute Q.", "Paul", ("exécute Q",)),
    ("Paul lance P, vérifie Q et arrête R.", "Paul", ("vérifie Q", "arrête R")),
    ("Je lance P et exécute Q.", "Je", ("exécute Q",)),
    ("Tu lances P et exécutes Q.", "Tu", ("exécutes Q",)),
    ("Nous lançons P et exécutons Q.", "Nous", ("exécutons Q",)),
    ("Vous lancez P et exécutez Q.", "Vous", ("exécutez Q",)),
    ("Les tests lancent P et exécutent Q.", "Les tests", ("exécutent Q",)),
    ("Paul a lancé P et exécute Q.", "Paul", ("exécute Q",)),
    ("Paul lance P et exécute Q ?", "Paul", ("exécute Q ?",)),
])
def test_bare_present_verb_shares_the_agreeing_subject(text, subject, refs):
    f, gate, events = _view(text)
    (coord,) = f.coordinations
    assert coord.construction == "shared_subject" and coord.kind == "AND"
    assert coord.members == tuple(u.id for u in f.units)
    for u, ref in zip(f.units[1:], refs):
        tail = "" if ref.endswith("?") else "."
        ref_f, ref_gate, ref_events = _view(f"{subject} {ref}{tail}")
        assert _signature(u, gate, events) == _signature(ref_f.units[0], ref_gate, ref_events)
        assert u.pragmatic != "REQUESTED" and not gate[u.id]
        if u.id in events:
            assert events[u.id].occurrence_derivation.provenance["shared_subject"] == coord.id
    ids = [events[u.id].event_ref.event_id for u in f.units if u.id in events]
    assert len(ids) == len(set(ids)) and coord.id not in events


def test_member_negation_stays_local():
    f, gate, _ = _view("Paul ne lance pas P et exécute Q.")
    u1, u2 = f.units
    assert (u1.polarity, u2.polarity) == ("negative", "positive")
    assert u2.subject == "paul" and u2.pragmatic == "ASSERTED" and not gate[u2.id]


@pytest.mark.parametrize("text", [
    "Paul lance P et exécutez Q.",          # person clash: only the imperative reading agrees
    "Lance P et exécute Q.",                # imperative host: no subject to share
    "Lance R si Paul lance P et exécute Q.",  # subordinated host stays open
    "Marie dit que Paul lance P et exécute Q.",  # ambiguous attachment stays open
])
def test_no_subject_sharing_outside_the_contract(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_subject" for c in f.coordinations)


def test_imperative_after_person_clash_stays_a_gated_request():
    f, gate, _ = _view("Paul lance P et exécutez Q.")
    assert f.units[1].pragmatic == "REQUESTED" and gate[f.units[1].id]


def test_present_person_features_follow_er_paradigm():
    feats = lambda w: set().union(*(ft for _, ft in lookup(w)[0]))
    assert {"P1S", "P3S"} <= feats("exécute") and "P2P" not in feats("exécute")
    assert feats("exécutez") >= {"P2P", "IMP"} and "P3S" not in feats("exécutez")
    assert "IMP" not in feats("exécutes") and "P2S" in feats("exécutes")
