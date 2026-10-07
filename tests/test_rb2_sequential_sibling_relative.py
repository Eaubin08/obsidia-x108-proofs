"""N4-R: "puis qui / puis que" is a sequential sibling relative (PRECEDES), never a root
request; the main predicate after it stays reported / open."""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _u(f, lemma):
    return next(u for u in f.units if u.lemma == lemma)


def test_n4r_sequential_sibling_relative():
    f = parse_utterance("Le script que Paul lance puis qui teste P échoue.")
    t = _u(f, "tester")
    assert t.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} and [a.text for a in t.objects] == ["p"]
    assert any(r.kind == "PRECEDES" and r.target == t.id for r in f.relations)
    assert governable_summary(f)["requested_world_actions"] == []
    assert any(m.endswith(f":main_predicate_after_relative_of={t.id}") for m in f.missing) and not f.closure
