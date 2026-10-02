"""A verbless connective tail is preserved ("Lance P puis R"), never dropped with a closed frame.

"Lance P puis R" / "Lance P, puis R" lost R entirely; "Lance P avec Q, puis R" kept the
oblique but lost R (only one remainder per unit was conserved). Each successive remainder
is now conserved: the tail is reported with its span
(unanalyzed_predicative_content:<span>:unattached_connective_content_of=<unit>), frame
open. No sequence relation is invented: PRECEDES stays for two predications
("Lance P puis exécute R").
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


def _tails(f):
    out = []
    for m in f.missing:
        if ":unattached_connective_content_of=" in m:
            a, b = map(int, m.split(":")[1].split("-"))
            out.append(f.raw[a:b])
    return out


@pytest.mark.parametrize("text", ["Lance P puis R.", "Lance P, puis R.", "Lance P avec Q, puis R."])
def test_connective_tail_preserved_open(text):
    f = parse_utterance(text)
    assert _tails(f) == ["puis R"] and not f.closure
    assert not any(r.kind == "PRECEDES" for r in f.relations) and len(f.units) == 1


def test_oblique_and_tail_both_conserved():
    f = parse_utterance("Lance P avec Q, puis R.")
    assert [(o.marker, o.argument.text) for o in f.oblique_arguments] == [("avec", "q")]


def test_two_predications_keep_precedes():
    f = parse_utterance("Lance P puis exécute R.")
    assert [r.kind for r in f.relations] == ["PRECEDES"] and not _tails(f) and f.closure
