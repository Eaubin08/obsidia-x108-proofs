"""Inverted questions keep their content.

"Paul lance-t-il le test ?": the euphonic "-t-" and the resumptive pronoun only mark the
inversion; the object after them is the object of the predication (formerly dropped while
the frame closed), the nominal subject stays the participant. Interrogative commitment:
ASKED, no request, no gate. A modifier with several readings ("automatiquement") stays open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _units(f):
    return [(u.predicate, u.pragmatic, u.polarity, u.subject, tuple(a.text for a in u.objects)) for u in f.units]


@pytest.mark.parametrize("text", ["Paul lance-t-il le test ?", "Quand Paul lance-t-il le test ?",
                                  "Paul lance-t-il vite le test ?"])
def test_inverted_question_keeps_object_and_subject(text):
    f = parse_utterance(text)
    assert _units(f) == [("EXECUTE", "ASKED", "positive", "paul", ("le test",))]
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and not f.constraints
    assert not s.get("confirmed_no_execute")
    assert f.closure


def test_inverted_question_open_modifier_keeps_object():
    f = parse_utterance("Paul lance-t-il automatiquement le test ?")
    assert _units(f) == [("EXECUTE", "ASKED", "positive", "paul", ("le test",))]
    assert [m.rsplit("=", 1)[1] for m in f.missing if ":unrepresented_modifier_of=" in m] == ["u1"]
    assert f.raw[16:31] == "automatiquement"
    assert not f.closure and not f.manner_modifiers
    assert governable_summary(f)["requested_world_actions"] == []
