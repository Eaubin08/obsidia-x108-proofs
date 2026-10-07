"""N3-R: an initial "si" before a coordinated antecedent stays the condition marker: the
main predicate after the relative is the protasis predicate (subject = the coordinated
antecedent, H14 CoordinationRef) and conditions the consequent, which keeps its gate."""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _u(f, lemma):
    return next(u for u in f.units if u.lemma == lemma)


@pytest.mark.parametrize("text,kind", [("Si Paul et Nadia qui testent P lancent Q, lance R.", "AND"),
                                       ("Si Paul ou Nadia qui testent P lancent Q, lance R.", "OR")])
def test_n3r_conditional_coordinated_antecedent(text, kind):
    f = parse_utterance(text)
    main = next(u for u in f.units if [a.text for a in u.objects] == ["q"])
    cons = next(u for u in f.units if [a.text for a in u.objects] == ["r"])
    assert main.subject != "p" and "paul" in main.subject and main.pragmatic == "HYPOTHETICAL"
    (c,) = [c for c in f.coordinations if c.construction == "coordinated_subject"]
    assert (c.kind, c.member_texts, c.host) == (kind, ("paul", "nadia"), main.id)
    assert ("CONDITIONS", main.id, cons.id) in [(r.kind, r.source, r.target) for r in f.relations]
    assert cons.pragmatic == "REQUESTED"
