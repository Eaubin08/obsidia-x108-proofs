"""N5: a symbolic single-letter argument is never read as a missing apostrophe.

"Lance S si Paul teste Q" became "lance s' si ..." (object lost, frame closed), and "Lance D
et Q" lost "D". A missing apostrophe is restored only before a vowel / mute h, and never for
an upper-case letter inside a sentence. Genuine typed elisions are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,objs", [("Lance S si Paul teste Q.", ["s"]), ("Lance T si Paul teste Q.", ["t"]),
                                       ("Lance D et Q.", ["d", "q"]), ("Lance L à Paul.", ["l"]),
                                       ("Lance S sauf si Paul lance Q.", ["s"])])
def test_symbolic_letter_kept(text, objs):
    assert [a.text for a in parse_utterance(text).units[0].objects] == objs


@pytest.mark.parametrize("text,subject", [("J ai lancé P.", "j'"), ("Paul s est arrêté.", "paul")])
def test_typed_elision_unchanged(text, subject):
    assert parse_utterance(text).units[0].subject == subject


def test_s_il_unchanged():
    f = parse_utterance("Lance R sauf s il pleut.")
    assert [(u.lemma, u.subject) for u in f.units] == [("lancer", None), ("pleuvoir", "il")]
