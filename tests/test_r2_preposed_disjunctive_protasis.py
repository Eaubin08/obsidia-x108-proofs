"""R2: a preposed disjunctive protasis ("Si P ou Q, R") is one OR group conditioning R.

Formerly the "ou" member was not joined: CONDITIONS(P -> Q) was invented, R lost its
condition and Q (protasis content) became a definitive REQUESTED. Now P and Q are
HYPOTHETICAL members of one OR CoordinationRef (conditional_protasis, ALTERNATIVE between
them) and that group conditions R. Never mixed with "et"; a postposed "R si P ou Q" stays
open (coordination_attachment_ambiguous).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text", ["Si Paul lance P ou exécute Q, lance R.",
                                  "Si Paul veut lancer P ou exécuter Q, lance R."])
def test_preposed_or_protasis_conditions_r(text):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units] == ["HYPOTHETICAL", "HYPOTHETICAL", "REQUESTED"]
    (c,) = f.coordinations
    assert (c.kind, c.construction, c.members) == ("OR", "conditional_protasis", ("u1", "u2"))
    assert [(r.kind, r.source, r.target) for r in f.relations] == [("ALTERNATIVE", "u1", "u2"), ("CONDITIONS", c.id, "u3")]
    assert governable_summary(f)["requested_action_surfaces"] == ["lance"] and f.closure


def test_and_protasis_unchanged():
    f = parse_utterance("Si Paul lance P et exécute Q, lance R.")
    (c,) = f.coordinations
    assert c.kind == "AND" and ("CONDITIONS", c.id, "u3") in [(r.kind, r.source, r.target) for r in f.relations]


def test_postposed_or_stays_open():
    f = parse_utterance("Lance R si Paul peut lancer P ou exécuter Q.")
    assert "coordination_attachment_ambiguous:u3" in f.ambiguities and not f.closure
