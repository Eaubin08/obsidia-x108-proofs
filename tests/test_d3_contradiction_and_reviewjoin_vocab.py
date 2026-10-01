"""D3 (frozen doctrine): H06 CONTRA-OCCURRENCE + H08 REVIEWJOIN-V1-STATUS-VOCAB.

H06: a canonical contradiction requires matching CONTENT, PERSPECTIVE,
TEMPORAL_ANCHOR, SCOPE and CONTEXT and an opposition within the same
engagement / action mode (today: requested_and_forbidden). Opposite
assertions of one perspective on one anchor are a named, open candidate
(occurrence_conflict_open), never a proven contradiction; different anchors,
perspectives or occurrence modes are never a contradiction. No automatic
winner. Pronoun extension: only a uniquely resolved reference may be compared;
the lattice has no subject-pronoun resolution, so "il" is never compared
(REFERENCE_RESOLVED != CONTRADICTION_PROVED; no new resolver).

H08: ReviewJoin V1 keeps the native status of each dimension (no unified
vocabulary, no ESTABLISHED / OBSERVED / TRUE / FALSE mapping), juxtaposes
readings (dimension, native status, perspective, provenance) and never
produces a truth, a winner or a fusion.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.review_join_v1 import READING_DIMENSIONS, build_review_join_v1


def test_h06_same_perspective_same_anchor_is_an_open_candidate():
    f = parse_utterance("Paul a lancé P et Paul n'a pas lancé P.")
    assert "occurrence_conflict_open:u1:u2" in f.ambiguities
    assert f.contradictions == () and not f.closure


def test_h06_different_temporal_anchors_are_not_a_contradiction():
    f = parse_utterance("Paul a lancé P hier et Paul n'a pas lancé P aujourd'hui.")
    assert f.contradictions == ()
    assert not any(a.startswith("occurrence_conflict_open") for a in f.ambiguities)


def test_h06_different_perspectives_are_not_a_contradiction():
    f = parse_utterance("Marie dit que Paul a lancé P et Nadia dit que Paul n'a pas lancé P.")
    assert f.contradictions == ()
    assert not any(a.startswith("occurrence_conflict_open") for a in f.ambiguities)


def test_h06_occurrence_mode_difference_is_not_a_contradiction():
    f = parse_utterance("Paul a lancé P et Paul ne lance pas P.")
    assert f.contradictions == ()
    assert not any(a.startswith("occurrence_conflict_open") for a in f.ambiguities)


def test_h06_opposite_directives_are_the_canonical_contradiction():
    f = parse_utterance("Lance P et ne lance pas P.")
    assert f.contradictions == ("EXECUTE(p):requested_and_forbidden:u1/u2",) and not f.closure


@pytest.mark.parametrize("text", ["Paul a lancé P et il n'a pas lancé P.",
                                  "Paul et Nadia ont lancé P et il n'a pas lancé P."])
def test_h06_unresolved_subject_pronoun_is_never_compared(text):
    f = parse_utterance(text)
    assert f.contradictions == ()
    assert not any(a.startswith("occurrence_conflict_open") for a in f.ambiguities)


_TEXTS = ["Lance P et ne lance pas P.", "Marie dit que Paul a lancé P.", "Paul lance P donc Nadia lance Q.",
          "Peux-tu lancer P et exécuter Q ?", "Lance-le."]


def test_h08_native_status_per_dimension_no_truth_no_winner():
    seen = set()
    for text in _TEXTS:
        f = parse_utterance(text)
        idx = build_frame_event_index(f)
        for event in idx.events():
            join = build_review_join_v1(f, event.event_ref.event_id, idx)
            assert join.provenance["status_vocabulary"] == "native_per_dimension (no cross-dimension mapping)"
            assert (join.metadata["truth"], join.metadata["winner"]) == (None, None)
            assert join.metadata["fusion"] == "none" and join.metadata["conflict_resolution"] == "none"
            for reading in join.readings:
                assert set(reading) >= {"dimension", "status", "perspective", "provenance"}
                assert str(reading["status"]) not in {"ESTABLISHED", "OBSERVED", "TRUE", "FALSE"}
                seen.add(reading["dimension"])
    assert seen == set(READING_DIMENSIONS)                       # every dimension keeps its native status
