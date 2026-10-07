"""N1-R / N2-R: a modifier or a negation between the relative verb and its object never
detaches the object, and the object keeps its full nominal extent ("le build rouge"); the
object never becomes the main subject. Undeterminable extent stays open."""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _u(f, lemma):
    return next(u for u in f.units if u.lemma == lemma)


@pytest.mark.parametrize("text,polarity", [("Le script qui teste rapidement P lance Q.", "positive"),
                                           ("Le script qui ne teste pas P lance Q.", "negative")])
def test_n1r_object_kept_across_modifier(text, polarity):
    f = parse_utterance(text)
    t = _u(f, "tester")
    assert [a.text for a in t.objects] == ["p"] and t.polarity == polarity
    main = next(u for u in f.units if [a.text for a in u.objects] == ["q"])
    assert main.subject == "script"


def test_n1r_manner_kept():
    f = parse_utterance("Le script qui teste rapidement P lance Q.")
    t = _u(f, "tester")
    assert [(m.unit, m.value) for m in f.manner_modifiers] == [(t.id, "FAST")]


def test_n2r_object_extent():
    f = parse_utterance("Le script qui teste le build rouge lance Q.")
    assert [a.text for a in _u(f, "tester").objects] == ["le build rouge"]
    main = next(u for u in f.units if [a.text for a in u.objects] == ["q"])
    assert main.subject == "script"
