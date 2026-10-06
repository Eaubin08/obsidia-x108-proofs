"""F-B3G-1: a member coordinated to a prep-governed infinitive keeps the same governor.

"Le script sert à tester Q et à lancer R", "Paul a oublié de tester Q et de lancer R": the
second member ("et à / de + INF") lost its governor and became a root, definitive REQUESTED
(often with a closed frame). A member repeating the same preposition now continues the SAME
prep-governed chain: same governor, same negation, same open status, coordinated with its
sibling member (never with the governor), never a root request. A bare member ("et lancer
R") is not licensed to share: its attachment stays open with its possible request exposed.
The directive "N'oublie pas de lancer P et d'exécuter Q" is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _rels(f):
    return [(r.kind, r.source, r.target, r.evidence) for r in f.relations]


@pytest.mark.parametrize("text,pair", [
    ("Le script sert à tester Q et à lancer R.", ("COORDINATES", "u2", "u3", "et")),
    ("Le script sert à tester Q ou à lancer R.", ("ALTERNATIVE", "u2", "u3", "ou")),
    ("La mémoire qui sert à tester Q et à lancer R est prête.", ("COORDINATES", "u2", "u3", "et")),
])
def test_serve_for_members_are_both_purpose(text, pair):
    f = parse_utterance(text)
    assert [(u.lemma, u.pragmatic, u.role) for u in f.units[1:]] == [("tester", "EMBEDDED", "PURPOSE"),
                                                                    ("lancer", "EMBEDDED", "PURPOSE")]
    assert _rels(f) == [("EMBEDS", "u1", "u2", "servir_a"), ("EMBEDS", "u1", "u3", "servir_a"), pair]
    occ = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    assert occ.get("u3") != "ASSERTED_REALIZED"
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and not f.constraints and f.closure


@pytest.mark.parametrize("text", ["Paul apprend à tester Q et à lancer R.", "Paul a oublié de tester Q et de lancer R."])
def test_known_prep_governor_shared(text):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units[1:]] == ["EMBEDDED", "EMBEDDED"]
    assert [(k, s, t) for k, s, t, _ in _rels(f)] == [("EMBEDS", "u1", "u2"), ("EMBEDS", "u1", "u3"),
                                                      ("COORDINATES", "u2", "u3")]
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure


@pytest.mark.parametrize("text", ["Paul commence à tester Q et à lancer R.", "Paul refuse de lancer P et d'exécuter Q."])
def test_unknown_governor_both_open(text):
    f = parse_utterance(text)
    assert [u.pragmatic for u in f.units] == ["EMBEDDED", "EMBEDDED"]
    assert all(f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities for u in f.units)
    assert not f.closure


def test_bare_member_not_shared_stays_open():
    f = parse_utterance("Le script sert à tester Q et lancer R.")
    r = f.units[2]
    assert r.pragmatic == "EMBEDDED" and r.pragmatic != "REQUESTED"
    assert f"coordination_attachment_ambiguous:{r.id}" in f.ambiguities and not f.closure


def test_controls_unchanged():
    f = parse_utterance("N'oublie pas de lancer P et d'exécuter Q.")
    assert [u.pragmatic for u in f.units[1:]] == ["REQUESTED", "REQUESTED"]
    assert [u.pragmatic for u in parse_utterance("Lance P et exécute Q.").units] == ["REQUESTED", "REQUESTED"]
    assert [u.pragmatic for u in parse_utterance("Peux-tu lancer P et exécuter Q ?").units] == ["INDIRECT_REQUEST"] * 2
    assert [u.modality for u in parse_utterance("Paul doit lancer P et exécuter Q.").units] == ["OBLIGATION"] * 2
