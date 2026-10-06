"""N1: the negated FORGET / HESITATE reminder reading is a directive only.

"Paul n'a pas oublié de tester Q", "Marie n'a pas hésité à tester Q", "Tu n'as pas oublié
de lancer P (?)": the embedded infinitive became a definitive REQUESTED (closed frame).
The reminder / invitation reading ("N'oublie pas de P", "N'hésitez pas à P") now requires the
governor to be an imperative; otherwise the infinitive is the governor's content (EMBEDDED),
never a request, never a gate.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text", ["Paul n'a pas oublié de tester Q.", "Marie n'a pas hésité à tester Q.",
                                  "Tu n'as pas oublié de lancer P.", "Tu n'as pas oublié de lancer P ?"])
def test_declarative_negated_forget_is_no_request(text):
    f = parse_utterance(text)
    gov, content = f.units
    assert content.pragmatic == "EMBEDDED" and content.embedded_under == gov.id
    assert governable_summary(f)["requested_world_actions"] == []


@pytest.mark.parametrize("text", ["N'oublie pas de lancer P.", "N'oubliez pas de lancer P.", "N'hésitez pas à lancer P."])
def test_imperative_reminder_unchanged(text):
    f = parse_utterance(text)
    assert f.units[1].pragmatic == "REQUESTED"
    assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"]
