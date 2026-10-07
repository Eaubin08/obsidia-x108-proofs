"""RED tranche 2 — temporal V1 SAME_FRAME_ONLY, half-open valid-time algebra, TEMPORALLY_INDETERMINATE != EMPTY
and the hostility of transform-like data (spec §5.1, §9.5 SA7; TEMPORAL_ORDER_AND_TRANSFORM_HOLD_V1)."""
from __future__ import annotations

import pytest

from tests.b8.red2_support import (
    FRAME_A, FRAME_B, assert_applied, assert_rejected, evaluate, interval, latest, make_claim, make_record, request,
    snapshot,
)


def test_spec_freezes_half_open_same_frame_only(spec_text):
    assert "half-open `[start, end)`, `start` may be −∞, `end` may be +∞" in spec_text
    assert "`TEMPORALLY_COMPARABLE(A, B) =\n  (A.temporal_frame_ref == B.temporal_frame_ref)`" in spec_text
    assert "`overlaps(a, b)` = a.start < b.end ∧ b.start < a.end" in spec_text
    assert "`contains(a, b)` =\n  a.start ≤ b.start ∧ b.end ≤ a.end" in spec_text


def test_temporally_comparable_iff_same_frame_ref(b8):
    assert b8.temporally_comparable(interval(b8, 0, 10), interval(b8, 50, 60)) is True
    assert b8.temporally_comparable(interval(b8, 0, 10), interval(b8, 0, 10, FRAME_B)) is False
    # identity is explicit: no name / case / label similarity
    assert b8.temporally_comparable(interval(b8, 0, 10, "frame:UTC"), interval(b8, 0, 10, "frame:utc")) is False


@pytest.mark.parametrize("a,b,expected", [
    ((0, 10), (10, 20), False),        # boundary-touching half-open intervals do not overlap
    ((10, 20), (0, 10), False),
    ((0, 10), (9, 20), True),
    ((0, 10), (20, 30), False),
    ((0, 10), (0, 10), True),
    ((None, 0), (-5, 5), True),        # −∞ start
    ((None, 0), (0, None), False),     # −∞ / +∞ touching at 0
    ((5, None), (100, 200), True),     # +∞ end
])
def test_overlaps_same_frame_half_open(b8, a, b, expected):
    assert b8.overlaps(interval(b8, *a), interval(b8, *b)) is expected


@pytest.mark.parametrize("a,b,expected", [
    ((0, 10), (0, 10), True),
    ((0, 10), (2, 8), True),
    ((0, 10), (0, 11), False),
    ((0, 10), (-1, 10), False),
    ((None, None), (3, 4), True),
    ((0, None), (None, 4), False),
])
def test_contains_same_frame(b8, a, b, expected):
    assert b8.contains(interval(b8, *a), interval(b8, *b)) is expected


@pytest.mark.parametrize("relation", ["overlaps", "contains"])
def test_cross_frame_relations_are_indeterminate_not_false(b8, relation):
    a, b = interval(b8, 0, 10, FRAME_A), interval(b8, 0, 10, FRAME_B)    # numerically identical values
    got = getattr(b8, relation)(a, b)
    assert got is b8.TEMPORALLY_INDETERMINATE
    assert got is not False and got is not True and got is not None


def test_no_transform_admission_surface_in_v1(b8):
    """CROSS_FRAME_TRANSFORM_ADMISSION=NONE: TemporalTransformRef is reserved, nothing converts frames."""
    exposed = [n for n in dir(b8) if any(w in n.lower() for w in ("transform", "convert", "offset"))
               and callable(getattr(b8, n))]
    assert exposed == []


def _cross_frame_occupied(b8, occupant_state="PROMOTED"):
    cand = make_claim(b8, "candidate", start=0, end=100, fid=FRAME_A)
    occ = make_claim(b8, "occupant", start=0, end=100, fid=FRAME_B)
    snap = snapshot(b8, [(cand, make_record(b8, cand, "VERIFIED")), (occ, make_record(b8, occ, occupant_state))],
                    slot_id=cand.slot_id)
    return cand, occ, snap


def test_cross_frame_occupied_slot_is_never_free(b8):
    """TEMPORALLY_INDETERMINATE != EMPTY: incomparability never yields 'free slot' or 'no overlap'."""
    cand, occ, snap = _cross_frame_occupied(b8)
    result = evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED"))
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])
    assert latest(result.snapshot, cand).state is b8.ClaimState.VERIFIED
    assert latest(result.snapshot, occ).state is b8.ClaimState.PROMOTED


@pytest.mark.parametrize("fake_ref", [
    "temporal_transform:frame:lab-b->frame:lab-a",
    "b8ttx_" + "1" * 64,
    "offset:+0",
    "convert:identity",
])
def test_transform_like_refs_have_zero_effect(b8, fake_ref):
    cand, occ, snap = _cross_frame_occupied(b8)
    result = evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED", refs=(fake_ref,)))
    reasons = assert_rejected(b8, snap, result)
    assert "temporal_relation_indeterminate" in reasons and "slot_occupied" not in reasons


def test_transform_like_claim_content_has_zero_effect(b8):
    cand = b8.KnowledgeClaim(lineage_id="candidate", claim_version=1, previous_claim_id=None,
                             claim_class=b8.ClaimClass.CODE_BUILD_CLAIM,
                             slot_id=make_claim(b8, "x").slot_id, valid_time=interval(b8, 0, 100, FRAME_A),
                             content={"temporal_transform": {"from": FRAME_B, "to": FRAME_A, "offset": 0}})
    occ = make_claim(b8, "occupant", fid=FRAME_B)
    snap = snapshot(b8, [(cand, make_record(b8, cand, "VERIFIED")), (occ, make_record(b8, occ, "PROMOTED"))],
                    slot_id=cand.slot_id)
    result = evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED"))
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])


@pytest.mark.parametrize("state", ["SUPERSEDED", "INVALIDATED", "STALE", "REJECTED"])
def test_cross_frame_non_current_claim_does_not_block(b8, state):
    """Only claims whose latest state is PROMOTED (or CONTESTED, open contradiction) take part."""
    cand, occ, snap = _cross_frame_occupied(b8, state)
    result = evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED"))
    assert_applied(b8, snap, result, cand, "PROMOTED")
