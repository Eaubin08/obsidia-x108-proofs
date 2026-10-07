"""WH_REQUEST: a clause-initial interrogative "qui" is the subject of its verb.

"Qui lance Q ?" asks WHO performs the action: "lance" has a subject ("qui", 3rd person),
so it is never an imperative, never REQUESTED, never an addressee request, and EXECUTE(Q)
never enters requested_world_actions. "Dis-moi, qui lance Q ?": only "dis-moi" is a
directive. A genuine imperative stays a request.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _unit(f, lemma):
    (u,) = [u for u in f.units if u.lemma == lemma]
    return u


@pytest.mark.parametrize("text,lemma", [("Qui lance Q ?", "lancer"), ("Qui exécute Q ?", "exécuter"),
                                        ("Dis-moi, qui lance Q ?", "lancer"),
                                        ("Dis-moi : qui lance Q ?", "lancer"),
                                        ("Qui doit lancer Q ?", "lancer")])
def test_who_question_is_never_a_request(text, lemma):
    f = parse_utterance(text)
    u = _unit(f, lemma)
    assert u.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST", "EMBEDDED"}
    assert u.request_target == "NONE" and u.role != "REQUEST"
    assert governable_summary(f)["requested_world_actions"] == []


@pytest.mark.parametrize("text", ["Qui lance Q ?", "Qui exécute Q ?"])
def test_who_question_is_asked(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == "ASKED" and [a.text for a in u.objects] == ["q"]


@pytest.mark.parametrize("text", ["Dis-moi, qui lance Q ?", "Dis-moi : qui lance Q ?"])
def test_only_the_tell_request_is_directive(text):
    f = parse_utterance(text)
    assert _unit(f, "dire").pragmatic == "REQUESTED"
    assert _unit(f, "lancer").pragmatic == "ASKED"


@pytest.mark.parametrize("text,actions", [("Dis-moi, lance Q.", ["EXECUTE"]), ("Lance Q.", ["EXECUTE"]),
                                          ("Qui a lancé Q ?", []), ("Dis-moi qui lance Q.", [])])
def test_controls(text, actions):
    assert governable_summary(parse_utterance(text))["requested_world_actions"] == actions
