"""N4: a preposed protasis keeps a prep-governed chain under its governor.

"Si Paul apprend à tester Q et à lancer R, lance S.": protasis joining ran before the
prep-chain sharing, so "à lancer R" became a protasis predicate of its own (governance under
"apprendre" lost). A member continuing the protasis' prep chain (same preposition +
infinitive) is no longer joined as a protasis member; it shares the governor; the governor
conditions the consequent, which keeps its request and gate. True coordinated protasis
predicates are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text,pair", [
    ("Si Paul apprend à tester Q et à lancer R, lance S.", "COORDINATES"),
    ("Si Paul apprend à tester Q ou à lancer R, lance S.", "ALTERNATIVE"),
    ("Si Paul a oublié de tester Q et de lancer R, lance S.", "COORDINATES"),
])
def test_prep_chain_stays_under_governor(text, pair):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units] == ["HYPOTHETICAL", "EMBEDDED", "EMBEDDED", "REQUESTED"]
    rels = sorted((r.kind, r.source, r.target) for r in f.relations)
    assert rels == sorted([("EMBEDS", "u1", "u2"), ("EMBEDS", "u1", "u3"), ("CONDITIONS", "u1", "u4"), (pair, "u2", "u3")])
    assert not f.coordinations
    assert governable_summary(f)["requested_action_surfaces"] == ["lance"] and f.closure


@pytest.mark.parametrize("text", ["Si Paul lance P et exécute Q, lance R.", "Si Paul lance P ou exécute Q, lance R."])
def test_true_protasis_coordination_unchanged(text):
    f = parse_utterance(text)
    (c,) = f.coordinations
    assert c.construction == "conditional_protasis" and ("CONDITIONS", c.id, "u3") in [(r.kind, r.source, r.target) for r in f.relations]
