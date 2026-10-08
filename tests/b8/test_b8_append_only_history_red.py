"""Class B remediation RED — append-only KnowledgeRecord history (spec §4 KnowledgeRecord immutable, §4.1
"every applied transition creates one immutable KnowledgeRecord", §5.3 RECORDED_HISTORY_IS_APPEND_ONLY_IN_LOGICAL_ORDER,
§9.3, §10 "History is append-only ... No destructive overwrite").

HISTORY_MODEL=APPEND_ONLY: an APPLIED transition keeps every pre-existing record byte-identical and appends its
successor record(s); REJECTED and NO_OP_DUPLICATE append nothing. Current state stays the unique maximal
record_version — tuple / append order is never semantic (HISTORY_ORDER != CURRENT_STATE).

T9 append role order: the spec defines none (T9_APPEND_ROLE_ORDER_SPECIFIED=NO). The implementation serializes the
two successors in §9.3 bundle field order — predecessor (old_*) then new claim (new_*). This is a non-semantic
serialization choice, not a causal or world order; the tests below only check it for determinism.
"""
from __future__ import annotations

import itertools

import pytest

from tests.b8.conftest import RECORDED_AT, candidate_snapshot, hold_request
from tests.b8.red2_support import (
    evaluate, evidence, ids, make_claim, request, verification,
)


def chain(b8, claim, states, first_rv=1):
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


def current(snap, claim_id):
    recs = [r for r in snap.records if r.claim_id == claim_id]
    top = max(r.record_version for r in recs)
    (rec,) = {r for r in recs if r.record_version == top}
    return rec


def fingerprint(records):
    return [(r.record_id, r.to_canonical()) for r in records]


def assert_appended(before, after, n_new):
    """Every pre-existing record kept byte-identical and in place; exactly n_new records appended."""
    assert len(after.records) == len(before.records) + n_new
    assert fingerprint(after.records[:len(before.records)]) == fingerprint(before.records)
    return after.records[len(before.records):]


# ---------------------------------------------------------------- ordinary transition

def test_t2_keeps_the_old_record_and_appends_its_successor(b8):
    """OLD_RECORD_REMOVED_AFTER_SUCCESS=0 on the RED-1 witness."""
    snap = candidate_snapshot(b8)
    (old,) = snap.records
    result = b8.evaluate_transition(snap, hold_request(b8), recorded_at=RECORDED_AT)
    (new,) = assert_appended(snap, result.snapshot, 1)
    assert old in result.snapshot.records
    assert new.record_version == old.record_version + 1 and new.previous_record_id == old.record_id
    assert new.state is b8.ClaimState.HELD
    assert result.receipt.from_record_id == old.record_id and result.receipt.to_record_id == new.record_id


@pytest.mark.parametrize("frm,target,artifact", [
    ("CANDIDATE", "SUPPORTED", "evidence"), ("SUPPORTED", "VERIFIED", "verification"),
    ("VERIFIED", "PROMOTED", None), ("PROMOTED", "INVALIDATED", "evidence"),
])
def test_ordinary_transitions_never_mutate_preexisting_records(b8, frm, target, artifact):
    """PREEXISTING_RECORD_MUTATIONS=0 with a history of depth > 1 and a bystander claim."""
    claim = make_claim(b8, "subject")
    other = make_claim(b8, "bystander", start=500, end=600)
    hist = chain(b8, claim, ["CANDIDATE", "HELD", frm] if frm != "CANDIDATE" else ["CANDIDATE"])
    other_hist = chain(b8, other, ["CANDIDATE", "SUPPORTED"])
    snap = snap_of(b8, [claim, other], [*hist, *other_hist])
    arts = {"evidence": [evidence(b8, claim)], "verification": [verification(b8, claim)], None: []}[artifact]
    result = evaluate(b8, snap, request(b8, claim, hist[-1], target, refs=ids(*arts)), arts)
    assert result.verdict is b8.TransitionVerdict.APPLIED
    (new,) = assert_appended(snap, result.snapshot, 1)
    assert new.previous_record_id == hist[-1].record_id and new.state is b8.ClaimState(target)
    assert current(result.snapshot, claim.claim_id) == new


def test_history_chain_r1_to_r4_is_retained_and_linked(b8):
    """HISTORY_CHAIN_GAPS=0, HISTORY_CHAIN_RECORDS_LOST=0."""
    claim = make_claim(b8, "chain")
    (r1,) = chain(b8, claim, ["CANDIDATE"])
    snap = snap_of(b8, [claim], [r1], revision=0)
    steps = [("SUPPORTED", [evidence(b8, claim)]), ("VERIFIED", [verification(b8, claim)]), ("PROMOTED", [])]
    for target, arts in steps:
        cur = current(snap, claim.claim_id)
        snap = evaluate(b8, snap, request(b8, claim, cur, target, revision=snap.slot_revision, refs=ids(*arts)),
                        arts).snapshot
    recs = sorted((r for r in snap.records if r.claim_id == claim.claim_id), key=lambda r: r.record_version)
    assert [r.record_version for r in recs] == [1, 2, 3, 4]
    assert [r.state.value for r in recs] == ["CANDIDATE", "SUPPORTED", "VERIFIED", "PROMOTED"]
    assert recs[0] == r1
    for prev, nxt in zip(recs, recs[1:]):
        assert nxt.previous_record_id == prev.record_id
    assert current(snap, claim.claim_id) == recs[-1] and snap.slot_revision == 3


@pytest.mark.parametrize("later", ["CONTESTED", "STALE", "INVALIDATED", "SUPERSEDED"])
def test_historical_promoted_stays_historical_after_appends(b8, later):
    """A1_CURRENT_STATE_REGRESSIONS=0: a retained PROMOTED record never becomes current again."""
    occ = make_claim(b8, "occupant")
    new = make_claim(b8, "newcomer", start=50, end=150)
    occ_hist = chain(b8, occ, ["VERIFIED", "PROMOTED", later], first_rv=3)
    (new_rec,) = chain(b8, new, ["VERIFIED"], first_rv=3)
    snap = snap_of(b8, [occ, new], [*occ_hist, new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
    if later == "CONTESTED":
        assert [r.value for r in result.receipt.reasons] == ["open_contradiction"]
        return
    assert result.verdict is b8.TransitionVerdict.APPLIED
    (appended,) = assert_appended(snap, result.snapshot, 1)
    assert current(result.snapshot, occ.claim_id).state is b8.ClaimState(later)
    assert current(result.snapshot, new.claim_id) == appended


# ---------------------------------------------------------------- rejected / duplicate / T1

def test_rejected_transition_appends_nothing(b8):
    """REJECTED_HISTORY_MUTATIONS=0."""
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8, reason=""), recorded_at=RECORDED_AT)
    assert result.verdict is b8.TransitionVerdict.REJECTED
    assert result.snapshot.records == snap.records


def test_duplicate_appends_nothing_and_keeps_the_revision(b8):
    """DUPLICATE_HISTORY_APPEND_CASES=0, DUPLICATE_SLOT_REVISION_INCREMENT=0."""
    snap = candidate_snapshot(b8)
    req = hold_request(b8)
    first = b8.evaluate_transition(snap, req, recorded_at=RECORDED_AT)
    again = b8.evaluate_transition(first.snapshot, req, recorded_at="2026-10-09T00:00:00Z")
    assert again.verdict is b8.TransitionVerdict.NO_OP_DUPLICATE and again.receipt == first.receipt
    assert again.snapshot.records == first.snapshot.records
    assert again.snapshot.slot_revision == first.snapshot.slot_revision
    assert len(first.snapshot.records) == 2


def test_t1_appends_exactly_one_initial_record(b8):
    """T1_HISTORY_BEHAVIOR=PASS: no fabricated predecessor."""
    claim = make_claim(b8, "t1")
    other = make_claim(b8, "already-there", start=300, end=400)
    other_hist = chain(b8, other, ["CANDIDATE", "HELD"])
    snap = snap_of(b8, [other], other_hist, revision=2)
    req = b8.TransitionRequest(claim_id=claim.claim_id, expected_claim_version=1, expected_state=None,
                               expected_record_version=0, slot_id=claim.slot_id, expected_slot_revision=2,
                               target_state=b8.ClaimState.CANDIDATE, refs=(), requester_ref="requester:test",
                               reason="capture")
    result = evaluate(b8, snap, req, [claim])
    (new,) = assert_appended(snap, result.snapshot, 1)
    assert new.record_version == 1 and new.previous_record_id is None and new.state is b8.ClaimState.CANDIDATE


# ---------------------------------------------------------------- T9

def _t9(b8, pred_states=("CANDIDATE", "VERIFIED", "PROMOTED"), new_states=("SUPPORTED", "VERIFIED")):
    pred = make_claim(b8, "pred", start=10, end=20)
    new = make_claim(b8, "new")
    p_hist = chain(b8, pred, pred_states)
    n_hist = chain(b8, new, new_states)
    return pred, new, p_hist, n_hist


def _t9_request(b8, new, n_cur, pred, p_cur, **kw):
    return request(b8, new, n_cur, "PROMOTED", supersedes_claim_id=pred.claim_id,
                   supersedes_record_id=p_cur.record_id, **kw)


def test_t9_keeps_all_history_and_appends_exactly_two_successors(b8):
    """T9_OLD_NEW_RECORD_LOSS=0, T9_PREDECESSOR_RECORD_LOSS=0, T9_DEEP_HISTORY_RECORDS_LOST=0,
    T9_PREEXISTING_RECORD_MUTATIONS=0, T9_SLOT_REVISION_INCREMENT=1."""
    pred, new, p_hist, n_hist = _t9(b8)
    snap = snap_of(b8, [pred, new], [*p_hist, *n_hist])
    result = evaluate(b8, snap, _t9_request(b8, new, n_hist[-1], pred, p_hist[-1]))
    assert result.verdict is b8.TransitionVerdict.APPLIED
    appended = assert_appended(snap, result.snapshot, 2)                     # 5 old records kept + 2 new
    p_new, n_new = appended                                                   # non-semantic role order (old, new)
    assert (p_new.claim_id, n_new.claim_id) == (pred.claim_id, new.claim_id)
    assert p_new.state is b8.ClaimState.SUPERSEDED and p_new.previous_record_id == p_hist[-1].record_id
    assert n_new.state is b8.ClaimState.PROMOTED and n_new.previous_record_id == n_hist[-1].record_id
    assert p_new.superseded_by == new.claim_id and n_new.supersedes == pred.claim_id
    assert (result.bundle.old_to_record_id, result.bundle.new_to_record_id) == (p_new.record_id, n_new.record_id)
    assert result.snapshot.slot_revision == snap.slot_revision + 1
    assert current(result.snapshot, pred.claim_id) == p_new and current(result.snapshot, new.claim_id) == n_new


@pytest.mark.parametrize("failure", ["stale", "reason", "containment", "contradiction"])
def test_t9_failure_appends_neither_successor(b8, failure):
    """T9_PARTIAL_HISTORY_APPEND_CASES=0."""
    pred, new, p_hist, n_hist = _t9(b8)
    claims, records, kw = [pred, new], [*p_hist, *n_hist], {}
    if failure == "stale":
        kw = {"revision": 4}
    elif failure == "reason":
        kw = {"reason": ""}
    elif failure == "containment":
        pred = make_claim(b8, "pred-wide", start=90, end=110)
        p_hist = chain(b8, pred, ["VERIFIED", "PROMOTED"])
        claims, records = [pred, new], [*p_hist, *n_hist]
    elif failure == "contradiction":
        contra = make_claim(b8, "contra", start=40, end=50)
        claims.append(contra)
        records += chain(b8, contra, ["SUPPORTED", "CONTESTED"])
    snap = snap_of(b8, claims, records)
    result = evaluate(b8, snap, _t9_request(b8, new, n_hist[-1], pred, p_hist[-1], **kw))
    assert result.verdict is b8.TransitionVerdict.REJECTED and result.bundle is None
    assert result.snapshot.records == snap.records and result.snapshot.slot_revision == snap.slot_revision


def test_t9_duplicate_appends_nothing(b8):
    pred, new, p_hist, n_hist = _t9(b8)
    snap = snap_of(b8, [pred, new], [*p_hist, *n_hist])
    req = _t9_request(b8, new, n_hist[-1], pred, p_hist[-1])
    first = evaluate(b8, snap, req)
    again = evaluate(b8, first.snapshot, req, recorded_at="2026-10-09T00:00:00Z")
    assert again.verdict is b8.TransitionVerdict.NO_OP_DUPLICATE and again.bundle == first.bundle
    assert again.snapshot.records == first.snapshot.records


# ---------------------------------------------------------------- input order hostility

def test_t9_input_history_order_changes_no_semantics(b8):
    """INPUT_HISTORY_ORDER_SEMANTIC_DIVERGENCES=0: supplied order is kept, successors appended deterministically."""
    pred, new, p_hist, n_hist = _t9(b8)
    prints = set()
    for perm in itertools.permutations([*p_hist, *n_hist]):
        snap = snap_of(b8, [pred, new], perm)
        result = evaluate(b8, snap, _t9_request(b8, new, n_hist[-1], pred, p_hist[-1]))
        appended = assert_appended(snap, result.snapshot, 2)
        prints.add((result.verdict, result.receipt.receipt_id, result.bundle.bundle_id,
                    tuple(r.record_id for r in appended)))
    assert len(prints) == 1


def test_ordinary_input_history_order_changes_no_semantics(b8):
    claim = make_claim(b8, "perm")
    hist = chain(b8, claim, ["CANDIDATE", "HELD", "SUPPORTED"])
    vr = verification(b8, claim)
    prints = set()
    for perm in itertools.permutations(hist):
        snap = snap_of(b8, [claim], perm)
        result = evaluate(b8, snap, request(b8, claim, hist[-1], "VERIFIED", refs=ids(vr)), [vr])
        (new,) = assert_appended(snap, result.snapshot, 1)
        prints.add((result.verdict, result.receipt.receipt_id, new.record_id))
    assert len(prints) == 1
