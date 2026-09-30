"""N6: a postposed protasis with an unknown verb is never silently dropped.

"Lance R si Paul valide P.": "si" + proper-noun subject + a verb unknown to
the lexicon opened no clause, so "si Paul valide P" vanished: R looked like
an unconditional request and closure was True, while the same content
preposed ("Si Paul valide P, lance R.") or with a pronoun subject ("si tu
valides P") is reported (M8-0b).

The content after "si" is reported as unanalyzed_predicative_content with its
conditional_protasis link: no unit and no CONDITIONS target are invented, no
lexicon entry is added, and closure stays open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,span", [
    ("Lance R si Paul valide P.", "Paul valide P"),
    ("Lance R si Paul frobnique.", "Paul frobnique"),
    ("Paul lance R si Nadia valide.", "Nadia valide"),
    ("Lance R et exécute Q si Paul valide P.", "Paul valide P"),
    ("Lance le test si Paul approuve le build.", "Paul approuve le build"),
    ("Lance R, si Paul valide P.", "Paul valide P"),
])
def test_postposed_unknown_protasis_is_reported(text, span):
    f = parse_utterance(text)
    entries = [m for m in f.missing if m.startswith("unanalyzed_predicative_content:")]
    assert len(entries) == 1 and entries[0].endswith(":conditional_protasis")
    start, end = map(int, entries[0].split(":")[1].split("-"))
    assert text[start:end] == span
    assert not any(r.kind == "CONDITIONS" for r in f.relations)        # no target invented
    assert all(u.lemma in {"lancer", "exécuter"} for u in f.units)     # no unit invented
    assert not f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul lance P.", "Lance R si tu lances P."])
def test_known_protasis_is_unchanged(text):
    f = parse_utterance(text)
    assert f.missing == () and any(r.kind == "CONDITIONS" for r in f.relations) and f.closure


def test_degree_si_is_not_a_protasis():
    assert parse_utterance("C'est si important pour Paul.").missing == ()
