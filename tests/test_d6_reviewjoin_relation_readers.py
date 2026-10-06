"""D6: ReviewJoin V1 reads the parser relations its flow projections do not carry.

TEMPORAL_ANCHOR / OVERLAPS (H05) are temporal readings; EXCEPTS (H17) is an exception
reading (its own dimension, never causal, never a condition). Each keeps the relation's
native vocabulary and provenance; no truth, winner, fusion or authority. Readers only: no
runtime wiring.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.review_join_v1 import READING_DIMENSIONS, build_review_join_v1


def _join(text):
    f = parse_utterance(text)
    idx = build_frame_event_index(f)
    host = {e.predicate_ref: e.event_ref.event_id for e in idx.events()}["u1"]
    return build_review_join_v1(f, host, idx)


@pytest.mark.parametrize("text,dimension,status", [
    ("Paul lance R quand Marie lance P.", "temporal", "TEMPORAL_ANCHOR:target"),
    ("Paul lance R pendant que Marie lance P.", "temporal", "OVERLAPS:target"),
    ("Paul lance R sauf si Marie lance P.", "exception", "EXCEPTS:target"),
])
def test_relation_is_read_in_its_dimension(text, dimension, status):
    j = _join(text)
    hits = [r for r in j.readings if r["status"] == status]
    assert len(hits) == 1 and hits[0]["dimension"] == dimension and hits[0]["perspective"] == "u2"
    assert hits[0]["provenance"]["relation_kind"] == status.split(":")[0]
    assert not any(r["dimension"] == "causal" for r in j.readings)
    assert (j.metadata["truth"], j.metadata["winner"], j.metadata["KX108_CALLED"]) == (None, None, 0)


def test_exception_dimension_declared_and_causal_unchanged():
    assert "exception" in READING_DIMENSIONS
    j = _join("Paul a lancé R parce que Marie a lancé P.")
    assert [r["status"] for r in j.readings if r["dimension"] == "causal"] == ["CAUSES:target"]


def test_no_runtime_wiring():
    import pathlib
    hits = [p for p in pathlib.Path("app").rglob("*.py")
            if "review_join" in p.read_text(encoding="utf-8", errors="ignore") and "lattice" not in p.parts]
    assert hits == []
