"""RED tranche 2 — T9 atomic supersession through the single gate (spec §5.2, §9.2 T9, §9.3, §9.4, §9.5 SA6 / SA7).

New claim N (VERIFIED, FRAME_A, [0, 100)). E = claims whose latest state is PROMOTED in the request snapshot, on the
slot, same frame, overlapping N. E is evaluable only when every latest-PROMOTED claim on the slot is in N's frame.
"""
from __future__ import annotations

import itertools
import re

import pytest

from tests.b8.red2_support import (
    FRAME_A, FRAME_B, WRONG_RECORD_ID, assert_rejected, attestation, evaluate, ids, latest, make_claim, make_record,
    reason_values, request, snapshot,
)

E_CODES = {"no_eligible_predecessor", "multiple_predecessors_unsupported", "predecessor_mismatch",
           "containment_not_satisfied"}


def _t9_request(b8, new, snap, designated_id, record_id, *, artifacts=(), **kw):
    return request(b8, new, latest(snap, new), "PROMOTED", supersedes_claim_id=designated_id,
                   supersedes_record_id=record_id, refs=ids(*artifacts), **kw)


def _simple(b8, *, pred=(10, 20), pred_fid=FRAME_A, cls="CODE_BUILD_CLAIM", extra=()):
    new = make_claim(b8, "new", cls=cls)
    pred_claim = make_claim(b8, "pred", cls=cls, start=pred[0], end=pred[1], fid=pred_fid)
    entries = [(new, make_record(b8, new, "VERIFIED")), (pred_claim, make_record(b8, pred_claim, "PROMOTED"))]
    for lineage, state, s, e, fid in extra:
        c = make_claim(b8, lineage, cls=cls, start=s, end=e, fid=fid)
        entries.append((c, make_record(b8, c, state)))
    snap = snapshot(b8, entries, slot_id=new.slot_id)
    return new, pred_claim, snap


# ---------------------------------------------------------------- atomic success

def test_t9_applies_one_atomic_bundle_with_one_revision_increment(b8):
    new, pred, snap = _simple(b8)
    req = _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id)
    result = evaluate(b8, snap, req)
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)
    bundle = result.bundle
    assert isinstance(bundle, b8.SupersessionTransitionBundle)
    after = result.snapshot
    assert after.slot_revision == snap.slot_revision + 1                     # §5.2: a T9 bundle increments once
    new_rec, old_rec = latest(after, new), latest(after, pred)
    assert new_rec.state is b8.ClaimState.PROMOTED and old_rec.state is b8.ClaimState.SUPERSEDED
    assert new_rec.record_version == latest(snap, new).record_version + 1
    assert old_rec.record_version == latest(snap, pred).record_version + 1
    assert new_rec.supersedes == pred.claim_id and old_rec.superseded_by == new.claim_id
    assert (bundle.new_claim_id, bundle.old_claim_id) == (new.claim_id, pred.claim_id)
    assert bundle.new_from_record_id == latest(snap, new).record_id and bundle.new_to_record_id == new_rec.record_id
    assert bundle.old_from_record_id == latest(snap, pred).record_id and bundle.old_to_record_id == old_rec.record_id
    assert bundle.request_id == req.request_id
    assert bundle.new_transition_receipt.to_state is b8.ClaimState.PROMOTED
    assert bundle.old_transition_receipt.to_state is b8.ClaimState.SUPERSEDED
    assert bundle.new_transition_receipt.verdict is bundle.old_transition_receipt.verdict is b8.TransitionVerdict.APPLIED
    assert bundle.supersedes_link and bundle.superseded_by_link
    assert re.fullmatch(r"b8bundle_[0-9a-f]{64}", bundle.bundle_id)
    # never two CURRENT PROMOTED: current record = unique max record_version per claim (historical != current)
    by_claim = {}
    for r in after.records:
        by_claim.setdefault(r.claim_id, []).append(r)
    current_records = {}
    for cid, recs in by_claim.items():
        top = max(r.record_version for r in recs)
        (current_records[cid],) = {r for r in recs if r.record_version == top}   # ambiguous maximum fails
    promoted = [r for r in current_records.values() if r.state is b8.ClaimState.PROMOTED]
    assert promoted == [new_rec]
    assert current_records[pred.claim_id] == old_rec and old_rec.state is b8.ClaimState.SUPERSEDED
    # input snapshot untouched
    assert latest(snap, new).state is b8.ClaimState.VERIFIED and latest(snap, pred).state is b8.ClaimState.PROMOTED


def test_t9_identical_request_is_no_op_duplicate_with_the_original_bundle(b8):
    new, pred, snap = _simple(b8)
    req = _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id)
    first = evaluate(b8, snap, req)
    again = evaluate(b8, first.snapshot, req, recorded_at="2026-10-09T00:00:00Z")
    assert again.verdict is b8.TransitionVerdict.NO_OP_DUPLICATE
    assert again.bundle == first.bundle and again.bundle.bundle_id == first.bundle.bundle_id
    assert again.snapshot == first.snapshot


# ---------------------------------------------------------------- all-or-nothing

def _assert_no_partial(b8, snap, result, new, pred):
    assert result.bundle is None
    assert latest(result.snapshot, new) == latest(snap, new) and latest(result.snapshot, pred) == latest(snap, pred)
    assert latest(result.snapshot, pred).superseded_by is None and latest(result.snapshot, new).supersedes is None


@pytest.mark.parametrize("case,expected", [
    ("partial_overlap", ["containment_not_satisfied"]),
    ("stale_revision", ["stale_request"]),
    ("open_contradiction", ["open_contradiction"]),
    ("missing_reason", ["reason_missing"]),
    ("review_missing", ["attestation_missing"]),
])
def test_t9_late_failure_applies_nothing(b8, case, expected):
    kw, extra, cls, pred = {}, (), "CODE_BUILD_CLAIM", (10, 20)
    if case == "partial_overlap":
        pred = (90, 110)
    elif case == "stale_revision":
        kw = {"revision": 4}
    elif case == "open_contradiction":
        extra = (("contradictor", "CONTESTED", 40, 50, FRAME_A),)
    elif case == "missing_reason":
        kw = {"reason": ""}
    elif case == "review_missing":
        cls = "HUMAN_DECLARATION"
    new, pred_claim, snap = _simple(b8, pred=pred, cls=cls, extra=extra)
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred_claim.claim_id, latest(snap, pred_claim).record_id, **kw))
    assert_rejected(b8, snap, result, expected)
    _assert_no_partial(b8, snap, result, new, pred_claim)


def test_t9_review_class_with_valid_authorization_applies(b8):
    new, pred, snap = _simple(b8, cls="HUMAN_DECLARATION")
    att = attestation(b8, new, kind="REVIEW_AUTHORIZATION")
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id,
                                            artifacts=[att]), [att])
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)


def test_t9_new_claim_must_be_verified(b8):
    new, pred, snap = _simple(b8)
    supported = make_record(b8, new, "SUPPORTED")
    snap2 = snapshot(b8, [(new, supported), (pred, latest(snap, pred))], slot_id=new.slot_id)
    result = evaluate(b8, snap2, _t9_request(b8, new, snap2, pred.claim_id, latest(snap2, pred).record_id))
    assert_rejected(b8, snap2, result, ["forbidden_transition"])


# ---------------------------------------------------------------- eligible set E

def test_t9_e_not_evaluable_asserts_no_cardinality(b8):
    """CARDINALITY_ASSIGNED_WHEN_E_NOT_EVALUABLE=0: a cross-frame current PROMOTED claim makes E indeterminate."""
    new, pred, snap = _simple(b8, extra=(("foreign-frame", "PROMOTED", 0, 100, FRAME_B),))
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id))
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])


def test_t9_historical_cross_frame_promoted_does_not_affect_evaluability(b8):
    new, pred, snap = _simple(b8, extra=(("old-foreign", "SUPERSEDED", 0, 100, FRAME_B),
                                         ("stale-foreign", "STALE", 0, 100, FRAME_B)))
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id))
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)


def test_t9_zero_eligible_is_not_converted_to_t6(b8):
    """T9_ZERO_ELIGIBLE_AUTO_CONVERTS_TO_T6=NO: designated PROMOTED claim outside N's valid_time."""
    new, pred, snap = _simple(b8, pred=(100, 200))
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id))
    assert_rejected(b8, snap, result, ["no_eligible_predecessor"])
    assert latest(result.snapshot, new).state is b8.ClaimState.VERIFIED


def test_t9_two_independent_facts(b8):
    """SA6 witness: designated claim not PROMOTED and E evaluable and empty."""
    new, pred, snap = _simple(b8)
    stale_pred = make_record(b8, pred, "STALE")
    snap2 = snapshot(b8, [(new, latest(snap, new)), (pred, stale_pred)], slot_id=new.slot_id)
    result = evaluate(b8, snap2, _t9_request(b8, new, snap2, pred.claim_id, stale_pred.record_id))
    assert_rejected(b8, snap2, result, ["no_eligible_predecessor", "referenced_claim_not_promoted"])


def test_t9_multi_cause_stale_and_not_evaluable(b8):
    new, pred, snap = _simple(b8, extra=(("foreign-frame", "PROMOTED", 0, 100, FRAME_B),))
    result = evaluate(b8, snap, _t9_request(b8, new, snap, pred.claim_id, latest(snap, pred).record_id, revision=3))
    assert_rejected(b8, snap, result, ["stale_request", "temporal_relation_indeterminate"])


# ---------------------------------------------------------------- SA6 / SA7 semantic matrix

DESIGNATIONS = ("member", "promoted_not_member", "not_promoted", "other_slot")
CARDINALITIES = (0, 1, 2)
BINDINGS = ("current", "wrong")
EVALUABILITY = ("evaluable", "not_evaluable")
MEMBER_INTERVALS = ((10, 20), (30, 40))


def _matrix_cases():
    for d, k, binding, ev in itertools.product(DESIGNATIONS, CARDINALITIES, BINDINGS, EVALUABILITY):
        if d == "member" and k == 0:
            continue  # impossible: D cannot be a member of an empty E
        yield d, k, binding, ev


MATRIX = list(_matrix_cases())


def _expected(d, k, binding, ev):
    reasons = set()
    if d == "not_promoted":
        reasons.add("referenced_claim_not_promoted")
    if d == "other_slot":
        reasons.add("slot_mismatch")
    if ev == "not_evaluable":
        return reasons | {"temporal_relation_indeterminate"}
    if k == 0:
        reasons.add("no_eligible_predecessor")
    elif k > 1:
        reasons.add("multiple_predecessors_unsupported")
    elif d == "promoted_not_member" or (d == "member" and binding == "wrong"):
        reasons.add("predecessor_mismatch")
    return reasons


def _matrix_world(b8, d, k, binding, ev):
    new = make_claim(b8, "new")
    entries = [(new, make_record(b8, new, "VERIFIED"))]
    members = []
    for i in range(k):
        c = make_claim(b8, f"member-{i}", start=MEMBER_INTERVALS[i][0], end=MEMBER_INTERVALS[i][1])
        entries.append((c, make_record(b8, c, "PROMOTED")))
        members.append(c)
    if d == "member":
        designated = members[0]
    else:
        spec = {"promoted_not_member": dict(state="PROMOTED", start=100, end=200, domain="domain:x"),
                "not_promoted": dict(state="STALE", start=50, end=60, domain="domain:x"),
                "other_slot": dict(state="PROMOTED", start=10, end=20, domain="domain:other")}[d]
        designated = make_claim(b8, "designated", start=spec["start"], end=spec["end"], domain=spec["domain"])
        entries.append((designated, make_record(b8, designated, spec["state"])))
    if ev == "not_evaluable":
        foreign = make_claim(b8, "foreign-frame", start=0, end=100, fid=FRAME_B)
        entries.append((foreign, make_record(b8, foreign, "PROMOTED")))
    snap = snapshot(b8, entries, slot_id=new.slot_id)
    designated_rec = next(r for r in snap.records if r.claim_id == designated.claim_id)
    record_id = designated_rec.record_id if binding == "current" else WRONG_RECORD_ID
    return new, designated, snap, _t9_request(b8, new, snap, designated.claim_id, record_id)


def test_matrix_covers_every_semantic_class():
    covered = {(d, k if ev == "evaluable" else "n/a", ev) for d, k, _, ev in MATRIX}
    for d in DESIGNATIONS:
        for ev in EVALUABILITY:
            for k in CARDINALITIES:
                if d == "member" and k == 0:
                    continue
                assert (d, k if ev == "evaluable" else "n/a", ev) in covered
    assert len(MATRIX) == 44                                                 # uncovered semantic cases = 0


@pytest.mark.parametrize("d,k,binding,ev", MATRIX, ids=lambda v: str(v))
def test_t9_predecessor_partition_matrix(b8, d, k, binding, ev):
    new, designated, snap, req = _matrix_world(b8, d, k, binding, ev)
    result = evaluate(b8, snap, req)
    expected = _expected(d, k, binding, ev)
    if not expected:
        assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)
        assert latest(result.snapshot, designated).state is b8.ClaimState.SUPERSEDED
        return
    got = assert_rejected(b8, snap, result, sorted(expected))           # empty-reason REJECTED = 0, unique codes
    if ev == "not_evaluable":
        assert not (set(got) & E_CODES)                                  # no cardinality asserted
    assert result.bundle is None
