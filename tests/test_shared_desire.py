"""Coordination P3: one written "vouloir" (DESIRE) is shared by coordinated infinitives.

"Paul veut lancer P et exécuter Q": the desire modal chain (modality, tense,
subject) scopes over the coordination (CoordinationRef "shared_modality"),
so "exécuter Q" is exactly "Paul veut exécuter Q", never an injunctive
REQUESTED infinitive. First person keeps the single-form reading
(DESIRE_ASSERTION with its desire_or_request ambiguity), questions stay
ASKED. "Veuillez" (directive), a negated "vouloir" (negative scope held)
and a subordinated host are unchanged.
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
    return (u.polarity, u.modality, u.subject, u.tense_aspect, u.pragmatic, u.role, u.action_agent,
            u.request_target, gate[u.id], e.occurrence_claim.value if e else None)


@pytest.mark.parametrize("text,lead,tail", [
    ("Paul veut lancer P et exécuter Q.", "Paul veut", "."),
    ("Paul voudrait lancer P et exécuter Q.", "Paul voudrait", "."),
    ("Je veux lancer P et exécuter Q.", "Je veux", "."),
    ("Je voudrais lancer P et exécuter Q.", "Je voudrais", "."),
    ("Voulez-vous lancer P et exécuter Q ?", "Voulez-vous", " ?"),
    ("Tu veux lancer P et exécuter Q ?", "Tu veux", " ?"),
    ("Paul veut lancer P, vérifier Q et arrêter R.", "Paul veut", "."),
])
def test_infinitives_share_the_desire_modal(text, lead, tail):
    f, gate, events = _view(text)
    (coord,) = f.coordinations
    assert coord.construction == "shared_modality" and coord.members == tuple(u.id for u in f.units)
    for u in f.units:
        obj = u.objects[0].text if u.objects else ""
        ref_f, ref_gate, ref_events = _view(f"{lead} {u.lemma} {obj}".rstrip() + tail)
        assert _signature(u, gate, events) == _signature(ref_f.units[0], ref_gate, ref_events)
        assert u.modality == "DESIRE" and u.pragmatic != "REQUESTED" and not gate[u.id]
    for u in f.units[1:]:
        if u.id in events:
            assert events[u.id].occurrence_derivation.provenance["shared_modality"] == coord.id
    ids = [events[u.id].event_ref.event_id for u in f.units if u.id in events]
    assert len(ids) == len(set(ids)) and coord.id not in events


def test_first_person_desire_keeps_its_request_ambiguity_on_every_member():
    f = parse_utterance("Je voudrais lancer P et exécuter Q.")
    assert {f"desire_or_request:{u.id}" for u in f.units} <= set(f.ambiguities)


@pytest.mark.parametrize("text", [
    "Paul ne veut pas lancer P et exécuter Q.",     # negated operator scope: held doctrine
    "Lance R si Paul veut lancer P et exécuter Q.",  # subordinated host stays open
    "Veuillez lancer P et exécuter Q.",              # directive, not a desire
])
def test_desire_not_shared_outside_the_contract(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_modality" for c in f.coordinations)
