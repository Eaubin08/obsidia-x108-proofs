"""RED tranche 1 — multi-cause reasons (SA3–SA5), atomic-fact partition witness, receipt determinism
(spec §3, §9.1, §9.5)."""
from __future__ import annotations

import itertools
import re

from tests.b8.conftest import RECORDED_AT, candidate_snapshot, hold_request


def test_independent_failures_accumulate_once_in_code_point_order(b8):
    snap = candidate_snapshot(b8)
    req = hold_request(b8, expected_slot_revision=1, reason="")
    result = b8.evaluate_transition(snap, req, recorded_at=RECORDED_AT)
    assert result.verdict is b8.TransitionVerdict.REJECTED
    assert [r.value for r in result.receipt.reasons] == ["reason_missing", "stale_request"]


def test_one_atomic_fact_one_code_forbidden_pair_vs_stale_snapshot(b8):
    """§9.5: forbidden_transition is evaluated on the request alone, a snapshot mismatch is stale_request;
    one fact never yields both codes."""
    snap = candidate_snapshot(b8)
    illegal_pair = b8.evaluate_transition(snap, hold_request(b8, target_state=b8.ClaimState.PROMOTED),
                                          recorded_at=RECORDED_AT)
    assert [r.value for r in illegal_pair.receipt.reasons] == ["forbidden_transition"]
    wrong_expected_state = b8.evaluate_transition(snap, hold_request(b8, expected_state=b8.ClaimState.HELD,
                                                                     target_state=b8.ClaimState.REJECTED),
                                                  recorded_at=RECORDED_AT)
    assert [r.value for r in wrong_expected_state.receipt.reasons] == ["stale_request"]


def _permuted_requests(b8, **overrides):
    base = dict(claim_id=None, expected_claim_version=1, expected_state=b8.ClaimState.CANDIDATE,
                expected_record_version=1, slot_id=None, expected_slot_revision=3,
                target_state=b8.ClaimState.HELD, refs=("ref:b", "ref:a"), requester_ref="requester:test",
                reason="awaiting evidence")
    from tests.b8.conftest import CLAIM, SLOT
    base.update(claim_id=CLAIM, slot_id=SLOT)
    base.update(overrides)
    keys = list(base)
    for order in itertools.islice(itertools.permutations(keys), 0, 720, 97):
        yield b8.TransitionRequest(**{k: base[k] for k in order})


def test_request_identity_is_independent_of_construction_order(b8):
    ids = {r.request_id for r in _permuted_requests(b8)}
    assert len(ids) == 1
    (rid,) = ids
    assert re.fullmatch(r"b8treq_[0-9a-f]{64}", rid)


def test_rejection_receipt_bytes_and_digest_are_order_independent(b8):
    snap = candidate_snapshot(b8)
    outs = {(b8.evaluate_transition(snap, r, recorded_at=RECORDED_AT).receipt.canonical_json(),
             b8.evaluate_transition(snap, r, recorded_at=RECORDED_AT).receipt.receipt_id)
            for r in _permuted_requests(b8, expected_slot_revision=0, reason="")}
    assert len(outs) == 1
    (body, rid), = outs
    assert re.fullmatch(r"b8rcpt_[0-9a-f]{64}", rid)
    assert rid == b8.full_identity("b8rcpt_", __import__("json").loads(body))


def test_snapshot_record_order_does_not_change_the_receipt(b8):
    other = b8.KnowledgeRecord(claim_id="b8claim_" + "c" * 64, claim_version=1, record_version=1,
                               state=b8.ClaimState.CANDIDATE, previous_record_id=None)
    snap_a = candidate_snapshot(b8, extra_records=(other,))
    snap_b = b8.SlotSnapshot(slot_id=snap_a.slot_id, slot_revision=snap_a.slot_revision,
                             records=tuple(reversed(snap_a.records)), applied_requests={})
    req = hold_request(b8)
    ra = b8.evaluate_transition(snap_a, req, recorded_at=RECORDED_AT).receipt
    rb = b8.evaluate_transition(snap_b, req, recorded_at=RECORDED_AT).receipt
    assert ra.canonical_json() == rb.canonical_json() and ra.receipt_id == rb.receipt_id


def test_same_request_state_and_contract_give_byte_identical_receipts(b8):
    snap = candidate_snapshot(b8)
    req = hold_request(b8)
    a = b8.evaluate_transition(snap, req, recorded_at=RECORDED_AT).receipt
    b = b8.evaluate_transition(snap, req, recorded_at=RECORDED_AT).receipt
    assert a.canonical_json() == b.canonical_json() and a.receipt_id == b.receipt_id
    assert a.request_id == req.request_id
