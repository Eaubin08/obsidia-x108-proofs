"""Class A1 remediation RED — current claim state is derived from record history (spec §9.2 T6, §9.3, §9.5 SA7, §10).

LATEST_RECORD(claim_id) = the unique KnowledgeRecord with maximal record_version for that claim in the canonical
pre-transition snapshot (MULTIPLE_RECORDS_PER_CLAIM=EXPECTED, CURRENT_STATE_SOURCE=UNIQUE_MAX_RECORD_VERSION).
Two distinct records sharing the maximal record_version make the history ambiguous: fail closed, never a
tie-break by list order, recorded_at or record id.
"""
from __future__ import annotations

import itertools

import pytest

from tests.b8.red2_support import (
    FRAME_A, FRAME_B, assert_rejected, evaluate, make_claim, reason_values, request,
)


def history(b8, claim, states, first_rv=1):
    """An append-only chain of records for one claim, linked by previous_record_id."""
    out, prev = [], None
    for i, state in enumerate(states):
        rec = b8.KnowledgeRecord(claim_id=claim.claim_id, claim_version=claim.claim_version,
                                 record_version=first_rv + i, state=b8.ClaimState(state), previous_record_id=prev)
        out.append(rec)
        prev = rec.record_id
    return out


def snap_of(b8, claims, records, revision=5):
    return b8.SlotSnapshot(slot_id=claims[0].slot_id, slot_revision=revision, records=tuple(records),
                           applied_requests={}, claims=tuple(claims))


def current(snap, claim):
    recs = [r for r in snap.records if r.claim_id == claim.claim_id]
    top = max(r.record_version for r in recs)
    (rec,) = [r for r in recs if r.record_version == top]
    return rec


def _fp(result):
    return (result.verdict, tuple(reason_values(result)), result.receipt.canonical_json(), result.receipt.receipt_id)


def _occupied_world(b8, occupant_states=("VERIFIED", "PROMOTED"), occupant_fid=FRAME_A):
    occ = make_claim(b8, "occupant", fid=occupant_fid)
    new = make_claim(b8, "newcomer", start=50, end=150)
    occ_hist = history(b8, occ, occupant_states, first_rv=3)
    (new_rec,) = history(b8, new, ["VERIFIED"], first_rv=3)
    return occ, new, occ_hist, new_rec


# ---------------------------------------------------------------- primary reproducer

def test_second_promotion_with_historical_current_occupant_is_rejected(b8):
    """SECOND_PROMOTION_WITH_HISTORICAL_CURRENT_OCCUPANT=0 (rv3 VERIFIED, rv4 PROMOTED occupies the slot)."""
    occ, new, occ_hist, new_rec = _occupied_world(b8)
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
    assert_rejected(b8, snap, result, ["slot_occupied"])
    assert current(result.snapshot, occ).state is b8.ClaimState.PROMOTED
    assert current(result.snapshot, new).state is b8.ClaimState.VERIFIED


def test_cross_frame_historical_current_occupant_is_indeterminate_not_free(b8):
    occ, new, occ_hist, new_rec = _occupied_world(b8, occupant_fid=FRAME_B)
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")),
                    ["temporal_relation_indeterminate"])


def test_current_state_and_outcome_are_independent_of_record_order(b8):
    """HISTORY_INPUT_ORDER_DIVERGENCES=0: rv3 never replaces rv4, whatever the tuple order."""
    occ, new, occ_hist, new_rec = _occupied_world(b8, ("SUPPORTED", "VERIFIED", "PROMOTED"))
    prints = set()
    for perm in itertools.permutations([*occ_hist, new_rec]):
        snap = snap_of(b8, [occ, new], perm)
        prints.add(_fp(evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))))
    assert len(prints) == 1
    (fp,) = prints
    assert fp[0] is b8.TransitionVerdict.REJECTED and fp[1] == ("slot_occupied",)


# ---------------------------------------------------------------- historical PROMOTED no longer current

@pytest.mark.parametrize("later", ["STALE", "INVALIDATED", "SUPERSEDED"])
def test_historical_promoted_whose_latest_state_moved_on_does_not_occupy(b8, later):
    occ, new, occ_hist, new_rec = _occupied_world(b8, ("VERIFIED", "PROMOTED", later))
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)
    assert current(result.snapshot, new).state is b8.ClaimState.PROMOTED
    assert result.snapshot.slot_revision == snap.slot_revision + 1


def test_historical_promoted_now_contested_is_an_open_contradiction_not_an_occupant(b8):
    occ, new, occ_hist, new_rec = _occupied_world(b8, ("VERIFIED", "PROMOTED", "CONTESTED"))
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")), ["open_contradiction"])


# ---------------------------------------------------------------- contradiction history

def test_current_contested_is_seen_through_history(b8):
    """CURRENT_CONTESTED_LOST_FROM_HISTORY=0."""
    occ, new, occ_hist, new_rec = _occupied_world(b8, ("CANDIDATE", "SUPPORTED", "CONTESTED"))
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")), ["open_contradiction"])


def test_historical_contested_is_not_current(b8):
    """HISTORICAL_CONTESTED_FALSE_CURRENT=0: CONTESTED followed by SUPPORTED no longer blocks."""
    occ, new, occ_hist, new_rec = _occupied_world(b8, ("SUPPORTED", "CONTESTED", "SUPPORTED"))
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)


# ---------------------------------------------------------------- CAS on the latest record

def test_cas_compares_against_the_unique_latest_record(b8):
    """CAS_USES_LATEST_RECORD_VERSION=YES."""
    claim = make_claim(b8, "subject")
    rv3, rv4 = history(b8, claim, ["SUPPORTED", "VERIFIED"], first_rv=3)
    snap = snap_of(b8, [claim], [rv3, rv4])
    stale = evaluate(b8, snap, request(b8, claim, rv3, "VERIFIED"))
    assert_rejected(b8, snap, stale, ["stale_request", "verification_not_satisfied"])
    ok = evaluate(b8, snap, request(b8, claim, rv4, "PROMOTED"))
    assert ok.verdict is b8.TransitionVerdict.APPLIED, reason_values(ok)
    after = current(ok.snapshot, claim)
    assert after.state is b8.ClaimState.PROMOTED and after.record_version == 5
    assert after.previous_record_id == rv4.record_id


# ---------------------------------------------------------------- T9 with predecessor history

def _t9_world(b8):
    pred = make_claim(b8, "pred", start=10, end=20)
    new = make_claim(b8, "new")
    p2, p3 = history(b8, pred, ["VERIFIED", "PROMOTED"], first_rv=2)
    (n3,) = history(b8, new, ["VERIFIED"], first_rv=3)
    return pred, new, [p2, p3, n3]


def test_t9_sees_predecessor_with_history_as_current_promoted(b8):
    """T9_HISTORY_PREDECESSOR_LOST=0."""
    pred, new, recs = _t9_world(b8)
    p2, p3, n3 = recs
    snap = snap_of(b8, [pred, new], recs)
    req = request(b8, new, n3, "PROMOTED", supersedes_claim_id=pred.claim_id, supersedes_record_id=p3.record_id)
    result = evaluate(b8, snap, req)
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)
    assert result.bundle.old_from_record_id == p3.record_id
    old_now = current(result.snapshot, pred)
    assert old_now.state is b8.ClaimState.SUPERSEDED and old_now.record_version == 4
    assert old_now.previous_record_id == p3.record_id
    assert p2 in result.snapshot.records                                   # older history is not collapsed
    assert current(result.snapshot, new).state is b8.ClaimState.PROMOTED
    assert result.snapshot.slot_revision == snap.slot_revision + 1


def test_t9_designating_a_historical_predecessor_record_is_predecessor_mismatch(b8):
    pred, new, recs = _t9_world(b8)
    p2, p3, n3 = recs
    snap = snap_of(b8, [pred, new], recs)
    req = request(b8, new, n3, "PROMOTED", supersedes_claim_id=pred.claim_id, supersedes_record_id=p2.record_id)
    assert_rejected(b8, snap, evaluate(b8, snap, req), ["predecessor_mismatch"])


def test_t9_history_outcome_is_independent_of_record_order(b8):
    pred, new, recs = _t9_world(b8)
    p3, n3 = recs[1], recs[2]
    prints = set()
    for perm in itertools.permutations(recs):
        snap = snap_of(b8, [pred, new], perm)
        req = request(b8, new, n3, "PROMOTED", supersedes_claim_id=pred.claim_id, supersedes_record_id=p3.record_id)
        result = evaluate(b8, snap, req)
        prints.add((_fp(result), result.bundle.bundle_id if result.bundle else None))
    assert len(prints) == 1


# ---------------------------------------------------------------- ambiguous maximum

def test_ambiguous_maximal_record_version_of_an_occupant_fails_closed(b8):
    """AMBIGUOUS_HISTORY_APPLIED=0: no tie-break by order, recorded_at or record id."""
    occ, new, occ_hist, new_rec = _occupied_world(b8)
    rival = b8.KnowledgeRecord(claim_id=occ.claim_id, claim_version=1, record_version=4,
                               state=b8.ClaimState.STALE, previous_record_id=occ_hist[0].record_id,
                               recorded_at="2099-01-01T00:00:00Z")
    for perm in itertools.permutations([*occ_hist, rival, new_rec]):
        snap = snap_of(b8, [occ, new], perm)
        result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
        assert "malformed_object" in assert_rejected(b8, snap, result)


def test_ambiguous_maximal_record_version_of_the_subject_fails_closed(b8):
    claim = make_claim(b8, "subject")
    rv3, rv4 = history(b8, claim, ["SUPPORTED", "VERIFIED"], first_rv=3)
    twin = b8.KnowledgeRecord(claim_id=claim.claim_id, claim_version=1, record_version=4,
                              state=b8.ClaimState.CONTESTED, previous_record_id=rv3.record_id)
    for perm in itertools.permutations([rv3, rv4, twin]):
        snap = snap_of(b8, [claim], perm)
        result = evaluate(b8, snap, request(b8, claim, rv4, "PROMOTED"))
        assert "malformed_object" in assert_rejected(b8, snap, result)
