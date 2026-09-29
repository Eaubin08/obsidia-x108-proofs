"""B1a: a nominal subject never extends across a WH word or a temporal introducer.

"Paul lance P quand Nadia exécute Q" gave "exécuter" the subject
"p quand nadia"; "Dis-moi comment Paul lance P" gave "moi comment paul":
the backward walk collecting a nominal subject only stopped at analysed
words, prepositions, subject pronouns and "ne". It now also stops at WH
words (quand, comment, pourquoi, où, ...) and at "lorsque". This fixes the
subject only: no clause, relation or temporal meaning is created here.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import _WH_WORDS, parse_utterance


@pytest.mark.parametrize("text,lemma,subject", [
    ("Paul lance P quand Nadia exécute Q.", "exécuter", "nadia"),
    ("Quand Nadia exécute Q, Paul lance P.", "exécuter", "nadia"),
    ("Paul lance P lorsque Nadia exécute Q.", "exécuter", "nadia"),
    ("Lorsque Nadia exécute Q, Paul lance P.", "exécuter", "nadia"),
    ("Lance P quand Nadia exécute Q.", "exécuter", "nadia"),
    ("Dis-moi quand Paul lance P.", "lancer", "paul"),
    ("Dis-moi comment Paul lance P.", "lancer", "paul"),
    ("Je sais pourquoi Paul lance P.", "lancer", "paul"),
    ("Paul a lancé P quand Nadia a exécuté Q.", "exécuter", "nadia"),
    ("Paul lance P quand le script exécute Q.", "exécuter", "script"),
])
def test_subject_stops_at_wh_and_temporal_introducers(text, lemma, subject):
    f = parse_utterance(text)
    (u,) = [x for x in f.units if x.lemma == lemma]
    assert u.subject == subject


@pytest.mark.parametrize("text", [
    "Paul lance P quand Nadia exécute Q.", "Dis-moi quand Paul lance P.", "Quand Paul lance-t-il P ?",
    "Paul lance P lorsque Nadia exécute Q.",
])
def test_no_subject_contains_a_wh_word_or_lorsque(text):
    for u in parse_utterance(text).units:
        words = set((u.subject or "").split())
        assert not words & (_WH_WORDS | {"lorsque", "lorsqu'"})


@pytest.mark.parametrize("text,subject", [
    ("Paul lance P.", "paul"),
    ("Le script lance P.", "script"),
    ("Paul lance P quand elle exécute Q.", None),
    ("Maman Paul lance P.", "maman paul"),
])
def test_other_subjects_unchanged(text, subject):
    f = parse_utterance(text)
    if subject is not None:
        assert f.units[0].subject == subject
    else:
        assert f.units[-1].subject == "elle"
