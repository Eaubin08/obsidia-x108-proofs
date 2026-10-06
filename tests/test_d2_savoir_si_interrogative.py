"""D2: "savoir si P" is an interrogative complement of savoir, never a condition.

"Paul sait si Marie lance P" was parsed as CONDITIONS(P -> savoir). It now takes the H13
channel (EMBEDS interrogative_complement): P is question content (not asserted, no
condition, no request). A copula complement ("Je sais si / quand P est prêt") is reported,
never dropped. Ordinary "si" after other verbs and "savoir + infinitive" are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


def _rels(f):
    return [(r.kind, r.source, r.target, r.evidence) for r in f.relations]


@pytest.mark.parametrize("text", ["Paul sait si Marie lance P.", "Paul ne sait pas si Marie a lancé P.",
                                  "Sais-tu si Marie a lancé P ?"])
def test_savoir_si_is_interrogative_complement(text):
    f = parse_utterance(text)
    know, p = f.units
    assert know.predicate == "KNOW" and p.pragmatic == "EMBEDDED"
    assert _rels(f) == [("EMBEDS", know.id, p.id, "interrogative_complement")]


@pytest.mark.parametrize("text", ["Je sais si P est prêt.", "Je sais quand P est prêt."])
def test_copula_complement_is_reported(text):
    f = parse_utterance(text)
    assert any(m.endswith(":wh_complement") for m in f.missing) and not f.closure


@pytest.mark.parametrize("text", ["Lance R si Paul sait lancer P.", "Paul sait lancer P si Marie lance Q."])
def test_ordinary_condition_unchanged(text):
    assert [r.kind for r in parse_utterance(text).relations] == ["CONDITIONS"]
