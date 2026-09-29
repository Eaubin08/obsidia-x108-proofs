"""Iteration 11A: one written directive keeps its scope across coordinated actions.

"Veuillez lancer P et exécuter Q": one directive scope (CoordinationRef
"shared_directive") over distinct event candidates; each member is the
directive "Veuillez V X." would be, never an assertion or a mention.
Imperatives stay directives member by member; descriptive coordinations gain
no gate; the shared "pouvoir" question is only a control here.
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
    return (u.polarity, u.modality, u.pragmatic, u.role, u.action_agent, u.request_target,
            gate[u.id], e.occurrence_claim.value if e else None)


def test_polite_directive_is_a_gated_request():
    f, gate, _ = _view("Veuillez lancer le test.")
    (u,) = f.units
    assert (u.pragmatic, u.role, u.request_target, u.politeness) == ("REQUESTED", "REQUEST", "ADDRESSEE", True)
    assert u.modality != "DESIRE" and gate[u.id]


def test_polite_prohibition_is_forbidden():
    f, gate, _ = _view("Veuillez ne pas lancer le test.")
    (u,) = f.units
    assert (u.polarity, u.pragmatic, u.role) == ("negative", "FORBIDDEN", "NEGATED") and not gate[u.id]


@pytest.mark.parametrize("text,verbs", [
    ("Veuillez lancer le build et exécuter le test.", ("lancer", "exécuter")),
    ("Veuillez lancer le build, vérifier le lot et arrêter le test.", ("lancer", "vérifier", "arrêter")),
])
def test_coordinated_members_share_one_directive_scope(text, verbs):
    f, gate, events = _view(text)
    (coord,) = f.coordinations
    assert coord.construction == "shared_directive" and coord.kind == "AND"
    assert coord.members == tuple(u.id for u in f.units) and len(f.units) == len(verbs)
    assert coord.evidence[0] == "veuillez"
    for u, verb in zip(f.units, verbs):
        obj = u.objects[0].text
        ref_f, ref_gate, ref_events = _view(f"Veuillez {verb} {obj}.")
        assert _signature(u, gate, events) == _signature(ref_f.units[0], ref_gate, ref_events)
        assert u.pragmatic == "REQUESTED" and u.politeness
        if u.id in events:
            assert events[u.id].occurrence_derivation.provenance["shared_directive"] == coord.id
    ids = [events[u.id].event_ref.event_id for u in f.units if u.id in events]
    assert len(ids) == len(set(ids))
    assert coord.id not in events


def test_true_request_and_gate_not_lost_for_first_member():
    f, gate, _ = _view("Veuillez lancer P et exécuter Q.")
    assert [u.pragmatic for u in f.units] == ["REQUESTED", "REQUESTED"]
    assert all(gate[u.id] for u in f.units)


def test_shared_final_object_under_directive():
    f, gate, _ = _view("Veuillez lancer, vérifier et arrêter le test.")
    (coord,) = f.coordinations
    assert coord.construction == "shared_directive" and len(coord.members) == 3
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"]] * 3
    assert all(u.pragmatic == "REQUESTED" for u in f.units)
    ref_f, ref_gate, _ = _view("Veuillez lancer le test.")
    assert gate["u1"] == ref_gate["u1"] is True


@pytest.mark.parametrize("text", [
    "Lance P et exécute Q.",
    "Lance P, vérifie Q et arrête R.",
])
def test_imperative_coordination_stays_directive(text):
    f, gate, _ = _view(text)
    assert all(u.pragmatic == "REQUESTED" and u.role == "REQUEST" for u in f.units)
    assert gate["u1"]
    assert not any(c.construction == "shared_directive" for c in f.coordinations)


def test_negated_imperative_coordination_stays_forbidden():
    f, gate, _ = _view("Ne lance pas P et n'exécute pas Q.")
    assert all(u.pragmatic == "FORBIDDEN" and not gate[u.id] for u in f.units)


@pytest.mark.parametrize("text", [
    "Paul veut lancer P et exécuter Q.",
    "Paul doit lancer P et exécuter Q.",
    "Je veux lancer P.",
])
def test_descriptive_controls_gain_no_directive_scope(text):
    f, gate, _ = _view(text)
    assert not any(c.construction == "shared_directive" for c in f.coordinations)
    assert not gate["u1"]


def test_question_control_has_no_directive_scope():
    f = parse_utterance("Peux-tu lancer P et exécuter Q ?")
    assert not any(c.construction == "shared_directive" for c in f.coordinations)
    assert f.units[0].pragmatic == "INDIRECT_REQUEST"
