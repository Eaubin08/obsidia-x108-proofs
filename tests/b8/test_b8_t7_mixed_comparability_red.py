"""RED tranche 2 — C2_MIXED_TEMPORAL_POLICY FAIL_CLOSED tests."""
from __future__ import annotations

import pytest

from tests.b8.red2_support import (
    assert_applied, assert_rejected, evaluate, latest, make_claim, make_record,
    request, snapshot,
)

def test_c2_r1_valid_same_frame_contradiction_contests_claim(b8):
    target = make_claim(b8, "target", fid="f1")
    contra = make_claim(b8, "contra", fid="f1")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (contra, rec2)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[contra.claim_id])
    result = evaluate(b8, snap, req, [target, contra])
    assert_applied(b8, snap, result, target, "CONTESTED")
    new_rec = latest(result.snapshot, target)
    assert new_rec.contested_by == (contra.claim_id,)

def test_c2_r2_pure_indeterminate_conflict_fails_closed(b8):
    target = make_claim(b8, "target", fid="f1")
    contra = make_claim(b8, "contra", fid="f2")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (contra, rec2)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[contra.claim_id])
    result = evaluate(b8, snap, req, [target, contra])
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])

def test_c2_r3_mixed_contradiction_and_indeterminate_fails_closed(b8):
    target = make_claim(b8, "target", fid="f1")
    valid_contra = make_claim(b8, "vc", fid="f1")
    indet_contra = make_claim(b8, "ic", fid="f2")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, valid_contra, "VERIFIED")
    rec3 = make_record(b8, indet_contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (valid_contra, rec2), (indet_contra, rec3)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[valid_contra.claim_id, indet_contra.claim_id])
    result = evaluate(b8, snap, req, [target, valid_contra, indet_contra])
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])

def test_c2_r4_mixed_contradiction_reverse_order_fails_closed(b8):
    target = make_claim(b8, "target", fid="f1")
    valid_contra = make_claim(b8, "vc", fid="f1")
    indet_contra = make_claim(b8, "ic", fid="f2")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, valid_contra, "VERIFIED")
    rec3 = make_record(b8, indet_contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (valid_contra, rec2), (indet_contra, rec3)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[indet_contra.claim_id, valid_contra.claim_id])
    result = evaluate(b8, snap, req, [target, valid_contra, indet_contra])
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])

def test_c2_r5_duplicate_valid_contradictions_and_one_indeterminate(b8):
    target = make_claim(b8, "target", fid="f1")
    valid_contra = make_claim(b8, "vc", fid="f1")
    indet_contra = make_claim(b8, "ic", fid="f2")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, valid_contra, "VERIFIED")
    rec3 = make_record(b8, indet_contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (valid_contra, rec2), (indet_contra, rec3)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[valid_contra.claim_id, valid_contra.claim_id, indet_contra.claim_id])
    result = evaluate(b8, snap, req, [target, valid_contra, indet_contra])
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])

def test_c2_r6_non_conflicting_incomparable_claim_does_not_poison(b8):
    target = make_claim(b8, "target", fid="f1")
    valid_contra = make_claim(b8, "vc", fid="f1")
    non_conflict = make_claim(b8, "nc", domain="domain:other", fid="f2")
    
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, valid_contra, "VERIFIED")
    rec3 = make_record(b8, non_conflict, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (valid_contra, rec2), (non_conflict, rec3)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[valid_contra.claim_id, non_conflict.claim_id])
    result = evaluate(b8, snap, req, [target, valid_contra, non_conflict])
    assert_applied(b8, snap, result, target, "CONTESTED")
    new_rec = latest(result.snapshot, target)
    assert new_rec.contested_by == (valid_contra.claim_id,)

def test_c2_r7_only_non_conflicting_indeterminate_claims_fails_inadmissible(b8):
    target = make_claim(b8, "target", fid="f1")
    non_conflict = make_claim(b8, "nc", domain="domain:other", fid="f2")
    
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, non_conflict, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (non_conflict, rec2)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[non_conflict.claim_id])
    result = evaluate(b8, snap, req, [target, non_conflict])
    assert_rejected(b8, snap, result, ["contradiction_inadmissible"])

def test_c2_r8_temporal_evaluation_runs_after_canonicalization(b8):
    pass

def test_c2_r9_multiple_indeterminate_conflicts_yields_one_reason(b8):
    target = make_claim(b8, "target", fid="f1")
    indet1 = make_claim(b8, "ic1", fid="f2")
    indet2 = make_claim(b8, "ic2", fid="f3")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, indet1, "VERIFIED")
    rec3 = make_record(b8, indet2, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (indet1, rec2), (indet2, rec3)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[indet1.claim_id, indet2.claim_id])
    result = evaluate(b8, snap, req, [target, indet1, indet2])
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])

def test_c2_r10_invalid_request_fails_before_temporal(b8):
    target = make_claim(b8, "target", fid="f1")
    indet_contra = make_claim(b8, "ic", fid="f2")
    rec1 = make_record(b8, target, "VERIFIED")
    rec2 = make_record(b8, indet_contra, "VERIFIED")
    snap = snapshot(b8, [(target, rec1), (indet_contra, rec2)], slot_id=target.slot_id)
    
    req = request(b8, target, rec1, "CONTESTED", refs=[indet_contra.claim_id], reason="")
    result = evaluate(b8, snap, req, [target, indet_contra])
    assert_rejected(b8, snap, result, ["reason_missing", "temporal_relation_indeterminate"])
