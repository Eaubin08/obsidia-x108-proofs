"""DETAIL / COMPARE: distinct predicates, never collapsed into EXPLAIN.

"détailler" and "comparer" produced no unit at all. They are now their own canonical
predicates (text_production, like EXPLAIN but lexically distinct). Objects, coordination
(AND / OR kept) and directive force follow the existing machinery; one predication each,
no world action, no gate. SPEAK ("parler") is held: making "parler" known turned "parle
du fait que P" into a relative and asserted P (lost-governor fail-closed broken).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text,pred,objs", [
    ("Détaille la mémoire.", "DETAIL", ("la mémoire",)), ("Détaille P.", "DETAIL", ("p",)),
    ("Compare P et Q.", "COMPARE", ("p", "q")),
])
def test_distinct_text_operations(text, pred, objs):
    f = parse_utterance(text)
    (u,) = f.units
    assert (u.predicate, u.pragmatic, tuple(a.text for a in u.objects)) == (pred, "REQUESTED", objs)
    assert u.predicate != "EXPLAIN" and governable_summary(f)["requested_world_actions"] == [] and f.closure


@pytest.mark.parametrize("text,kind", [("Compare P et Q.", "AND"), ("Compare P ou Q.", "OR")])
def test_compare_keeps_its_coordination(text, kind):
    f = parse_utterance(text)
    assert [(c.construction, c.kind, c.member_texts) for c in f.coordinations] == [("coordinated_object", kind, ("p", "q"))]
    assert len(build_frame_event_index(f).events()) <= 1 and len(f.units) == 1


def test_detail_never_closes_over_an_unanalyzed_relative():
    # the gate that made 299be951 unsafe: the unit-less relative must stay preserved and open
    f = parse_utterance("Détaille la mémoire qui te sert à parler.")
    u = f.units[0]
    assert (u.predicate, [a.text for a in u.objects]) == ("DETAIL", ["la mémoire"])
    # since SERVE_FOR the relative is SERVE_FOR -> PURPOSE SPEAK; its "te" stays unresolved, kept
    s = next(x for x in f.units if x.predicate == "SERVE_FOR")
    assert any(m.endswith(f":unresolved_clitic_of={s.id}") for m in f.missing) and not f.closure
