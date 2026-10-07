"""RED tranche 1 — pure evaluator: immutable REJECTED, APPLIED revision rule, CAS, idempotency, oversize
(spec §3, §5.2, §9.1, §9.2 T2)."""
from __future__ import annotations

from tests.b8.conftest import CLAIM, RECORDED_AT, candidate_snapshot, hold_request


def _record(snapshot, claim_id=CLAIM):
    (rec,) = [r for r in snapshot.records if r.claim_id == claim_id]
    return rec


def test_applied_t2_moves_exactly_one_claim_and_increments_slot_revision_once(b8):
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8), recorded_at=RECORDED_AT)
    assert result.verdict is b8.TransitionVerdict.APPLIED
    assert result.receipt.verdict is b8.TransitionVerdict.APPLIED and tuple(result.receipt.reasons) == ()
    after = result.snapshot
    assert after.slot_revision == snap.slot_revision + 1
    rec = _record(after)
    assert rec.state is b8.ClaimState.HELD and rec.record_version == 2 and rec.claim_version == 1
    assert rec.previous_record_id is not None
    # the input snapshot is immutable
    assert snap.slot_revision == 3 and _record(snap).state is b8.ClaimState.CANDIDATE


def _assert_rejected_unchanged(b8, snap, result):
    assert result.verdict is b8.TransitionVerdict.REJECTED
    assert result.receipt.verdict is b8.TransitionVerdict.REJECTED
    assert result.snapshot == snap
    assert result.snapshot.slot_revision == snap.slot_revision
    assert _record(result.snapshot) == _record(snap)


def test_stale_slot_revision_is_rejected_without_mutation(b8):
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8, expected_slot_revision=2), recorded_at=RECORDED_AT)
    _assert_rejected_unchanged(b8, snap, result)
    assert tuple(result.receipt.reasons) == (b8.ReasonCode.stale_request,)


def test_stale_record_version_or_state_is_stale_request(b8):
    snap = candidate_snapshot(b8)
    for kw in ({"expected_record_version": 7}, {"expected_claim_version": 2}):
        result = b8.evaluate_transition(snap, hold_request(b8, **kw), recorded_at=RECORDED_AT)
        _assert_rejected_unchanged(b8, snap, result)
        assert tuple(result.receipt.reasons) == (b8.ReasonCode.stale_request,)


def test_missing_reason_is_rejected_without_mutation(b8):
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8, reason=""), recorded_at=RECORDED_AT)
    _assert_rejected_unchanged(b8, snap, result)
    assert tuple(result.receipt.reasons) == (b8.ReasonCode.reason_missing,)


def test_forbidden_pair_is_rejected_without_mutation(b8):
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8, target_state=b8.ClaimState.PROMOTED), recorded_at=RECORDED_AT)
    _assert_rejected_unchanged(b8, snap, result)
    assert tuple(result.receipt.reasons) == (b8.ReasonCode.forbidden_transition,)


def test_current_expected_revision_lets_the_request_proceed(b8):
    snap = candidate_snapshot(b8, slot_revision=9)
    result = b8.evaluate_transition(snap, hold_request(b8, expected_slot_revision=9), recorded_at=RECORDED_AT)
    assert result.verdict is b8.TransitionVerdict.APPLIED and result.snapshot.slot_revision == 10


def test_identical_request_already_applied_is_no_op_duplicate_with_original_receipt(b8):
    snap = candidate_snapshot(b8)
    req = hold_request(b8)
    first = b8.evaluate_transition(snap, req, recorded_at=RECORDED_AT)
    again = b8.evaluate_transition(first.snapshot, req, recorded_at="2026-10-08T00:00:00Z")
    assert again.verdict is b8.TransitionVerdict.NO_OP_DUPLICATE
    assert again.receipt == first.receipt and again.receipt.receipt_id == first.receipt.receipt_id
    assert again.snapshot == first.snapshot and again.snapshot.slot_revision == first.snapshot.slot_revision


def test_oversize_request_is_rejected_not_truncated(b8):
    snap = candidate_snapshot(b8)
    big = "x" * (b8.OBJECT_TOTAL_BOUND + 1)
    result = b8.evaluate_transition(snap, hold_request(b8, reason=big), recorded_at=RECORDED_AT)
    _assert_rejected_unchanged(b8, snap, result)
    assert b8.ReasonCode.oversize_object in tuple(result.receipt.reasons)
