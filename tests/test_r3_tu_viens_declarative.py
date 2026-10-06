"""R3: "Tu viens lancer P." never drops its written subject into a bare injunction.

venir + infinitive has no construction here (statement or directive): the subject "tu" is
kept, the content stays under that governor (infinitive_under_unrecognized_governor, frame
open), its possible addressee request stays exposed fail-closed, never a definitive REQUESTED.
"""
from __future__ import annotations

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def test_tu_viens_keeps_subject_and_possible_request():
    f = parse_utterance("Tu viens lancer P.")
    (u,) = f.units
    assert (u.subject, u.pragmatic, u.role, u.request_target) == ("tu", "EMBEDDED", "REQUEST", "ADDRESSEE")
    assert [a.text for a in u.objects] == ["p"] and u.pragmatic != "REQUESTED"
    assert governable_summary(f)["requested_action_surfaces"] == ["lancer"]
    assert "infinitive_under_unrecognized_governor:u1" in f.ambiguities and not f.closure


def test_controls_unchanged():
    assert [u.pragmatic for u in parse_utterance("Viens lancer P.").units] == ["REQUESTED"]
    assert [u.pragmatic for u in parse_utterance("Tu viens lancer P ?").units] == ["INDIRECT_REQUEST"]
    f = parse_utterance("Tu viens de lancer P.")
    assert [(u.subject, u.tense_aspect) for u in f.units] == [("tu", "RECENT_PAST")]
    assert governable_summary(parse_utterance("Paul vient lancer P.")).get("requested_action_surfaces") == []
