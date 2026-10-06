"""A preposed protasis mixing "et" and "ou" never drops the consequent's gate.

"Si Paul lance P et Marie lance Q ou Luc lance S, lance X.": the last member left the
protasis as a root assertion, CONDITIONS was emitted to it, and "lance X" took its subject
("luc") and lost its request / gate. Now every member stays protasis content (HYPOTHETICAL),
each pair keeps its written connective (COORDINATES for "et", ALTERNATIVE for "ou"), no group
and no CONDITIONS are built on an invented precedence, the open grouping and the held
condition of X are named, frame open; X stays exactly a REQUESTED action with its gate.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _rels(f):
    return [(r.kind, r.source, r.target) for r in f.relations]


@pytest.mark.parametrize("text,pairs", [
    ("Si Paul lance P et Marie lance Q ou Luc lance S, lance X.",
     [("COORDINATES", "u1", "u2"), ("ALTERNATIVE", "u2", "u3")]),
    ("Si Paul lance P ou Marie lance Q et Luc lance S, lance X.",
     [("ALTERNATIVE", "u1", "u2"), ("COORDINATES", "u2", "u3")]),
    ("Si Paul lance P et exécute Q ou arrête S, lance X.",
     [("COORDINATES", "u1", "u2"), ("ALTERNATIVE", "u2", "u3")]),
])
def test_mixed_protasis_open_consequent_gate_kept(text, pairs):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units] == ["HYPOTHETICAL"] * 3 + ["REQUESTED"]
    x = f.units[3]
    assert (x.subject, [a.text for a in x.objects], x.request_target) == (None, ["x"], "ADDRESSEE")
    assert governable_summary(f)["requested_action_surfaces"] == ["lance"]
    assert _rels(f) == pairs and not f.coordinations                 # no group, no CONDITIONS
    assert "coordination_attachment_ambiguous:u1" in f.ambiguities
    assert "condition_scope_ambiguous:u1:host=u4" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text,kind,pair", [("Si Paul lance P et exécute Q, lance X.", "AND", "COORDINATES"),
                                            ("Si Paul lance P ou exécute Q, lance X.", "OR", "ALTERNATIVE")])
def test_pure_protasis_unchanged(text, kind, pair):
    f = parse_utterance(text)
    (c,) = f.coordinations
    assert c.kind == kind and _rels(f) == [(pair, "u1", "u2"), ("CONDITIONS", c.id, "u3")] and f.closure


def test_postposed_mixed_stays_fail_closed():
    f = parse_utterance("Lance X si Paul lance P et Marie lance Q ou Luc lance S.")
    assert governable_summary(f)["requested_action_surfaces"] == ["lance"] and not f.closure
    assert "coordination_attachment_ambiguous:u4" in f.ambiguities
