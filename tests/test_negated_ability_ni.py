"""G4: "Ne peux-tu ni lancer P ni exécuter Q ?" never requests its members.

A second-person negated "pouvoir" over verbal "ni" was left out of the shared
ni analysis (its act is a negated question / reproach / suggestion, held as
H10) but nothing replaced it: each "ni" infinitive fell back to a subject-less
injunctive infinitive, two independent REQUESTED units, two gates, closure
True, nothing named.

Like the negated "vouloir" ("Ne veux-tu ni ... ?"), each member now stays
represented as content under that exact "pouvoir" unit (negated_scope_open),
never REQUESTED, never FORBIDDEN; in a question the open act of the operator
itself is named (negated_speech_act_open). Closure stays open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

_REQ = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text,question", [
    ("Ne peux-tu ni lancer P ni exécuter Q ?", True),
    ("Ne pouvez-vous ni lancer P ni exécuter Q ?", True),
    ("Ne pourrais-tu ni lancer P ni exécuter Q ?", True),
    ("Ne pourriez-vous ni lancer P ni exécuter Q ?", True),
    ("Ne peux-tu ni lancer P, ni exécuter Q ?", True),
    ("Tu ne peux ni lancer P ni exécuter Q ?", True),
    ("Tu ne peux ni lancer P ni exécuter Q.", False),
])
def test_negated_second_person_ability_ni_members_are_open_content(text, question):
    f = parse_utterance(text)
    op, p, q = f.units
    gate = _gate(f)
    assert (op.lemma, op.polarity) == ("pouvoir", "negative")
    assert [(u.lemma, [a.head for a in u.objects]) for u in (p, q)] == [("lancer", ["p"]), ("exécuter", ["q"])]
    for u in (p, q):
        assert u.pragmatic == "EMBEDDED" and u.pragmatic not in _REQ and not gate[u.id]
        assert u.embedded_under == op.id
        assert f"negated_scope_open:{u.id}" in f.ambiguities
    assert (f"negated_speech_act_open:{op.id}" in f.ambiguities) is question
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False
    assert f.constraints == () and not f.closure


def test_negated_desire_ni_is_unchanged():
    f = parse_utterance("Ne veux-tu ni lancer P ni exécuter Q ?")
    assert f.ambiguities == ("negated_scope_open:u2", "negated_scope_open:u3")


def test_declarative_third_person_ni_under_pouvoir_keeps_its_shared_operator():
    f = parse_utterance("Paul ne peut ni lancer P ni exécuter Q.")
    assert f.operator_scopes and f.operator_scopes[0].speech_act == "NONE"
    assert all(u.pragmatic == "ASSERTED" and u.polarity == "negative" for u in f.units)
    assert not any(a.startswith(("negated_scope_open", "negated_speech_act_open")) for a in f.ambiguities)


def test_positive_shared_ability_question_is_unchanged():
    f = parse_utterance("Peux-tu lancer P et exécuter Q ?")
    gate = _gate(f)
    assert all(u.pragmatic == "INDIRECT_REQUEST" and gate[u.id] for u in f.units)
