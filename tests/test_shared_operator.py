"""Iteration 11B: one written "pouvoir" scopes over coordinated infinitives.

"Peux-tu lancer P et exécuter Q ?": one OperatorScopeRef (ABILITY_OR_PERMISSION)
over the CoordinationRef; its speech act (INDIRECT_REQUEST here, NONE for
"Paul peut ...", QUESTION for "Paul peut-il ...") is derived once, from the
modal's own context, and every member carries provenance shared_operator.
Each member is exactly what "<modal> V X" alone would be; no member becomes a
REQUESTED bare infinitive. The operator is neither an event, nor a
coordination, nor an occurrence claim, nor an authority object.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project


def _view(text):
    f = parse_utterance(text)
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    events = {c.predicate_ref: c for c in build_frame_event_index(f).events()}
    return f, gate, events


def _signature(u, gate, events):
    e = events.get(u.id)
    return (u.polarity, u.modality, u.subject, u.pragmatic, u.role, u.action_agent, u.request_target,
            gate[u.id], e.occurrence_claim.value if e else None)


def _operator(f):
    (op,) = f.operator_scopes
    coord = f.coordination(op.scope)
    assert coord is not None and coord.construction == "shared_modality"
    return op, coord


def _members_match_references(text, lead, tail):
    f, gate, events = _view(text)
    op, coord = _operator(f)
    assert coord.members == tuple(u.id for u in f.units)
    for u in f.units:
        obj = u.objects[0].text if u.objects else ""
        ref_f, ref_gate, ref_events = _view(f"{lead} {u.lemma} {obj}".rstrip() + tail)
        assert _signature(u, gate, events) == _signature(ref_f.units[0], ref_gate, ref_events)
        if u.id in events:
            assert events[u.id].occurrence_derivation.provenance["shared_operator"] == op.id
    ids = [events[m].event_ref.event_id for m in coord.members if m in events]
    assert len(ids) == len(set(ids))
    assert op.id not in events and coord.id not in events
    return f, gate, op


@pytest.mark.parametrize("text,lead", [
    ("Peux-tu lancer P et exécuter Q ?", "Peux-tu"),
    ("Pouvez-vous lancer P et exécuter Q ?", "Pouvez-vous"),
    ("Est-ce que tu peux lancer P et exécuter Q ?", "Est-ce que tu peux"),
    ("Pourrais-tu lancer P et exécuter Q ?", "Pourrais-tu"),
    ("Peux-tu lancer P, exécuter Q et arrêter R ?", "Peux-tu"),
])
def test_indirect_request_is_one_shared_speech_act(text, lead):
    f, gate, op = _members_match_references(text, lead, " ?")
    assert (op.kind, op.speech_act, op.target) == (
        "ABILITY_OR_PERMISSION", "INDIRECT_REQUEST", "ADDRESSEE_OR_POSSIBLE_ADDRESSEE")
    assert all(u.pragmatic == "INDIRECT_REQUEST" and u.modality == "ABILITY_OR_PERMISSION" for u in f.units)
    assert all(u.pragmatic != "REQUESTED" for u in f.units)
    assert gate["u1"] and gate["u2"]


@pytest.mark.parametrize("modal", ["peut", "pouvait", "pourra"])
def test_descriptive_ability_is_never_a_request(modal):
    f, gate, op = _members_match_references(f"Paul {modal} lancer P et exécuter Q.", f"Paul {modal}", ".")
    assert (op.speech_act, op.target, op.source) == ("NONE", "NONE", modal)
    assert all(u.pragmatic == "ASSERTED" and u.subject == "paul" and not gate[u.id] for u in f.units)


@pytest.mark.parametrize("text", ["Paul peut-il lancer P et exécuter Q ?", "Marie peut-elle lancer P et exécuter Q ?"])
def test_third_person_question_is_asked_not_requested(text):
    f, gate, events = _view(text)
    op, _ = _operator(f)
    assert op.speech_act == "QUESTION"
    assert all(u.pragmatic == "ASKED" and not gate[u.id] for u in f.units)


def test_negated_member_keeps_its_own_polarity_under_the_shared_operator():
    f, gate, events = _view("Peux-tu ne pas lancer P et exécuter Q ?")
    op, coord = _operator(f)
    assert op.speech_act == "INDIRECT_REQUEST" and coord.members == ("u1", "u2")
    u1, u2 = f.units
    assert (u1.polarity, u1.pragmatic, gate["u1"]) == ("negative", "FORBIDDEN", False)
    assert (u2.polarity, u2.pragmatic, gate["u2"]) == ("positive", "INDIRECT_REQUEST", True)


def test_declarative_ni_under_pouvoir_matches_single_negated_ability():
    f, gate, events = _view("Paul ne peut ni lancer le test ni exécuter le build.")
    ref_f, ref_gate, ref_events = _view("Paul ne peut pas lancer le test.")
    ref = _signature(ref_f.units[0], ref_gate, ref_events)
    op, coord = f.operator_scopes[0], f.coordinations[0]
    assert coord.construction == "ni_negative_coordination" and op.scope == coord.id
    assert op.speech_act == "NONE" and len(f.units) == 2
    assert all(_signature(u, gate, events)[:5] == ref[:5] and not gate[u.id] for u in f.units)


@pytest.mark.parametrize("text", [
    "Ne peux-tu ni lancer P ni exécuter Q ?",   # negated 2nd-person pouvoir: left open
    "Paul ne peut pas lancer P et exécuter Q.",  # negated pouvoir over "et": left open
    "Lance R si tu peux lancer P et exécuter Q.",
])
def test_open_negative_or_conditional_pouvoir_gets_no_operator(text):
    assert parse_utterance(text).operator_scopes == ()


@pytest.mark.parametrize("text,kind", [
    ("Marie dit que Paul peut lancer P et exécuter Q.", "REPORTED"),
    ("Marie croit que Paul peut lancer P et exécuter Q.", "BELIEVED"),
])
def test_report_and_belief_are_never_requests(text, kind):
    f, gate, _ = _view(text)
    assert f.operator_scopes == ()
    assert f.units[1].pragmatic == kind
    assert all(u.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} and not gate[u.id] for u in f.units)


@pytest.mark.parametrize("text", [
    "Veuillez lancer P et exécuter Q.",
    "Lance P et exécute Q.",
    "Paul doit lancer P et exécuter Q.",
])
def test_directive_and_obligation_controls_have_no_ability_operator(text):
    assert parse_utterance(text).operator_scopes == ()


def test_shared_final_object_under_pouvoir():
    f, gate, _ = _view("Peux-tu lancer et exécuter le test ?")
    _operator(f)
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], ["le test"]]
    assert all(u.pragmatic == "INDIRECT_REQUEST" and gate[u.id] for u in f.units)


def test_object_before_coordination_is_not_shared_under_pouvoir():
    f, _, _ = _view("Peux-tu lancer le test et attendre ?")
    _operator(f)
    assert [[a.text for a in u.objects] for u in f.units] == [["le test"], []]
    assert all(u.pragmatic == "INDIRECT_REQUEST" for u in f.units)


def test_ir_serializes_operator_scope():
    f = parse_utterance("Peux-tu lancer P et exécuter Q ?")
    ir = governable_summary(f)
    op = f.operator_scopes[0]
    assert ir["operator_scopes"] == [[op.id, "ABILITY_OR_PERMISSION", op.scope, "INDIRECT_REQUEST",
                                      "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"]]
