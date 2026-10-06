"""N8: an object relative on the sentence-initial NP never swallows the main predicate.

"Le test que Paul lance échoue": "échoue" (unknown verb) was read as the relative verb's
object, and "est prêt" / "demain échoue" were dropped while the frame closed. In an object
relative ("que") on the sentence-initial NP, the relative verb's object slot is the
antecedent (gap): material after its last verb is the antecedent's main predicate, reported
as unanalyzed content (main_predicate_after_relative_of), frame open. An utterance with no
unit holding a relative followed by content is reported too. Verbless NPs are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


def _kept(f):
    return [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":", 2)[2])
            for m in f.missing]


@pytest.mark.parametrize("text,span,unit", [
    ("Le test que Paul lance échoue.", "échoue", "u1"),
    ("Le build que Marie teste échoue.", "échoue", "u1"),
    ("La tâche que Paul lance réussit.", "réussit", "u1"),
    ("Le test que Paul lance est prêt.", "est prêt", "u1"),
    ("Le test que Paul lance demain échoue.", "demain échoue", "u1"),
    ("Le test que Paul lance et que Marie observe échoue.", "échoue", "u2"),
])
def test_main_predicate_reported_never_object(text, span, unit):
    f = parse_utterance(text)
    assert all(not u.objects for u in f.units)
    assert _kept(f) == [(span, f"main_predicate_after_relative_of={unit}")] and not f.closure


def test_fully_unknown_relative_utterance_reported():
    f = parse_utterance("Le fichier que Marie ouvre disparaît.")
    assert _kept(f) == [("Le fichier que Marie ouvre disparaît", "root")] and not f.closure


@pytest.mark.parametrize("text", ["Le test rouge.", "Merci Paul."])
def test_np_unchanged(text):
    assert parse_utterance(text).missing == ()


def test_object_relative_inside_main_clause_unchanged():
    f = parse_utterance("Paul lance le test que Marie a préparé.")
    assert [(u.lemma, [a.text for a in u.objects]) for u in f.units] == [("lancer", ["le test"]), ("préparer", [])]
