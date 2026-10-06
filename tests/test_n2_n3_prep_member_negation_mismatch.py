"""N2 / N3: prep-governed coordination with a negated first member or a mismatched
preposition never yields a root request.

N2: "Paul a oublié de ne pas tester Q et de lancer R": the governing preposition was read
right before the verb ("pas"), so the second member could not share and became a root
REQUESTED. The preposition is now read skipping only the infinitive's own negation (both
for the first member and for "et de ne pas + INF").
N3: "Paul apprend à tester Q et de lancer R": a mismatched preposition licenses no sharing
and no other governor; the member stays open (coordination_attachment_ambiguous), never a
request, never a gate.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _rels(f):
    return [(r.kind, r.source, r.target) for r in f.relations]


@pytest.mark.parametrize("text,polarities", [
    ("Paul a oublié de ne pas tester Q et de lancer R.", ["negative", "positive"]),
    ("Paul apprend à ne pas tester Q et à lancer R.", ["negative", "positive"]),
    ("Paul a oublié de ne pas tester Q et de ne pas lancer R.", ["negative", "negative"]),
])
def test_negated_member_keeps_shared_governor(text, polarities):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units[1:]] == ["EMBEDDED", "EMBEDDED"]
    assert [u.polarity for u in f.units[1:]] == polarities
    assert _rels(f) == [("EMBEDS", "u1", "u2"), ("EMBEDS", "u1", "u3"), ("COORDINATES", "u2", "u3")]
    assert governable_summary(f)["requested_world_actions"] == [] and not f.constraints


@pytest.mark.parametrize("text,member", [("Paul apprend à tester Q et de lancer R.", "u3"),
                                         ("Paul refuse de tester Q et à lancer R.", "u2")])
def test_mismatched_preposition_fails_closed(text, member):
    f = parse_utterance(text)
    m = f.unit(member)
    assert m.pragmatic == "EMBEDDED" and m.role != "REQUEST"
    assert f"coordination_attachment_ambiguous:{member}" in f.ambiguities and not f.closure
    assert "lancer" not in governable_summary(f)["requested_action_surfaces"]


def test_controls():
    f = parse_utterance("N'oublie pas de tester Q et de ne pas lancer R.")
    assert [u.pragmatic for u in f.units[1:]] == ["REQUESTED", "FORBIDDEN"] and f.constraints[-1] == "NO_EXECUTE(r)"
    f = parse_utterance("Paul a oublié de tester Q et de lancer R.")
    assert [u.pragmatic for u in f.units[1:]] == ["EMBEDDED", "EMBEDDED"] and f.closure
