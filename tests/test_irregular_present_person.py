"""B2: irregular (non -er) present forms carry their person, by paradigm position.

"Tu lances P et fais Q": "fais" also reads as an imperative and, unlike -er
forms, had no person feature, so the shared-subject rule could not check
agreement with "tu" and left "fais Q" an injunctive REQUESTED imperative.
The five-slot present tables of the irregular lexicon now give each form its
person from its position in the paradigm (je/tu, il/elle, nous, vous,
ils/elles), never from proximity; a form shares the host subject only when
that person agrees ("Paul lance P et fais Q" keeps its imperative).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.lexicon import lookup

PARADIGMS = {
    "faire": ("fais", "fait", "faisons", "faites", "font"),
    "dire": ("dis", "dit", "disons", "dites", "disent"),
    "écrire": ("écris", "écrit", "écrivons", "écrivez", "écrivent"),
    "attendre": ("attends", "attend", "attendons", "attendez", "attendent"),
}
SLOTS = ({"P1S", "P2S"}, {"P3S"}, {"P1P"}, {"P2P"}, {"P3P"})


@pytest.mark.parametrize("lemma,forms", PARADIGMS.items())
def test_present_person_by_paradigm_position(lemma, forms):
    for form, persons in zip(forms, SLOTS):
        feats = set().union(*(ft for lem, ft in lookup(form)[0] if lem == lemma))
        assert feats & {"P1S", "P2S", "P3S", "P1P", "P2P", "P3P"} == persons, form


@pytest.mark.parametrize("text,subject", [
    ("Tu lances P et fais Q.", "tu"),
    ("Je lance P et fais Q.", "je"),
    ("Nous lançons P et faisons Q.", "nous"),
    ("Vous lancez P et faites Q.", "vous"),
    ("Tu lances P et dis Q.", "tu"),
    ("Tu lances P et écris Q.", "tu"),
    ("Tu lances P et attends Q.", "tu"),
    ("Vous lancez P et attendez Q.", "vous"),
    ("Tu lances P puis fais Q.", "tu"),
])
def test_agreeing_irregular_form_shares_the_subject(text, subject):
    f = parse_utterance(text)
    (coord,) = [c for c in f.coordinations if c.construction == "shared_subject"]
    assert coord.members == tuple(u.id for u in f.units)
    u = f.units[-1]
    assert (u.subject, u.verb_form) == (subject, "FINITE") and u.pragmatic not in {"REQUESTED", "FORBIDDEN"}


@pytest.mark.parametrize("text", [
    "Paul lance P et fais Q.",      # fais: je/tu only, never Paul
    "Paul lance P et faites Q.",
    "Tu lances P et faites Q.",
    "Nous lançons P et fais Q.",
    "Lance P et fais Q.",           # no host subject
])
def test_disagreeing_or_subjectless_form_keeps_its_imperative(text):
    f = parse_utterance(text)
    assert not any(c.construction == "shared_subject" for c in f.coordinations)
    assert f.units[-1].verb_form == "IMPERATIVE"
