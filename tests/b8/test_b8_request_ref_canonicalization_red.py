import pytest
import app.knowledge.b8 as b8
from app.knowledge.b8.core import TransitionRequest, ClaimState, KnowledgeRecord
from tests.b8.red2_support import snapshot, request, evaluate, make_claim, make_record, REVISION

def test_c1_r1_permutation_identity():
    # C1-R1: permutation identity. (A,B) vs (B,A) -> same canonical refs, same request_id
    req1 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_a", "ref_b"), "sys", "r1")
    req2 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_b", "ref_a"), "sys", "r1")
    
    assert req1.refs == req2.refs
    assert req1.request_id == req2.request_id

def test_c1_r2_duplicate_collapse():
    # C1-R2: duplicate collapse. (A,A,B) vs (A,B) -> same canonical refs, same request_id
    req1 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_a", "ref_a", "ref_b"), "sys", "r1")
    req2 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_a", "ref_b"), "sys", "r1")
    
    assert req1.refs == req2.refs
    assert req1.request_id == req2.request_id

def test_c1_r5_genuinely_different_set():
    # C1-R5: genuinely different set. (A,B) vs (A,C) -> different canonical refs, different request_id
    req1 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_a", "ref_b"), "sys", "r1")
    req2 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, ("ref_a", "ref_c"), "sys", "r1")
    
    assert req1.refs != req2.refs
    assert req1.request_id != req2.request_id

def test_empty_set():
    req1 = TransitionRequest("c1", 1, ClaimState.CANDIDATE, 1, "s1", 1, ClaimState.SUPPORTED, (), "sys", "r1")
    assert req1.refs == ()

def test_c1_r6_reason_invariance():
    # C1-R6: reason invariance. refs=(valid, wrong_bound) vs refs=(wrong_bound, valid) -> same verdict, same reason set.
    # We create a dummy snapshot and pass two unresolved refs to get NOT_FOUND or similar errors.
    claim = make_claim(b8, "lin")
    rec = make_record(b8, claim, "CANDIDATE")
    snap = snapshot(b8, [(claim, rec)], slot_id=claim.slot_id)
    
    req1 = request(b8, claim, rec, "HELD", refs=("ref_1", "ref_2"))
    req2 = request(b8, claim, rec, "HELD", refs=("ref_2", "ref_1"))
    
    res1 = evaluate(b8, snap, req1)
    res2 = evaluate(b8, snap, req2)
    
    assert res1.receipt.verdict == res2.receipt.verdict
    assert res1.receipt.reasons == res2.receipt.reasons

def test_c1_r7_t11_invariance():
    # C1-R7: T11 invariance. Permuting or duplicating request refs must not alter qualifying trigger identities,
    # T11 verdict, or canonical staleness_trigger_refs.
    claim = make_claim(b8, "lin")
    rec = make_record(b8, claim, "PROMOTED")
    snap = snapshot(b8, [(claim, rec)], slot_id=claim.slot_id)
    
    req1 = request(b8, claim, rec, "STALE", refs=("ref_1", "ref_1", "ref_2"))
    req2 = request(b8, claim, rec, "STALE", refs=("ref_2", "ref_1"))
    
    res1 = evaluate(b8, snap, req1)
    res2 = evaluate(b8, snap, req2)
    
    assert res1.receipt.verdict == res2.receipt.verdict
    assert res1.receipt.reasons == res2.receipt.reasons
    
def test_c1_r8_t9_invariance():
    # C1-R8: T9 invariance.
    claim = make_claim(b8, "lin")
    rec = make_record(b8, claim, "VERIFIED")
    snap = snapshot(b8, [(claim, rec)], slot_id=claim.slot_id)
    
    req1 = request(b8, claim, rec, "PROMOTED", refs=("ref_1", "ref_2"), supersedes_claim_id="old_claim")
    req2 = request(b8, claim, rec, "PROMOTED", refs=("ref_2", "ref_1", "ref_1"), supersedes_claim_id="old_claim")
    
    res1 = evaluate(b8, snap, req1)
    res2 = evaluate(b8, snap, req2)
    
    assert res1.receipt.verdict == res2.receipt.verdict
    assert res1.receipt.reasons == res2.receipt.reasons

def test_c1_r9_class_d_invariance():
    # C1-R9: Class D invariance.
    # T12 is Class D (STALE -> VERIFIED)
    claim = make_claim(b8, "lin")
    rec = make_record(b8, claim, "STALE")
    snap = snapshot(b8, [(claim, rec)], slot_id=claim.slot_id)
    
    req1 = request(b8, claim, rec, "VERIFIED", refs=("ref_1", "ref_2"))
    req2 = request(b8, claim, rec, "VERIFIED", refs=("ref_2", "ref_1"))
    
    res1 = evaluate(b8, snap, req1)
    res2 = evaluate(b8, snap, req2)
    
    assert res1.receipt.verdict == res2.receipt.verdict
    assert res1.receipt.reasons == res2.receipt.reasons
def test_c1_r3_r4_duplicate_replay():
    # C1-R3: apply (A,B), replay (B,A) -> NO_OP_DUPLICATE
    # C1-R4: apply (A,B), replay (A,A,B) -> NO_OP_DUPLICATE
    claim = make_claim(b8, "lin")
    rec = make_record(b8, claim, "CANDIDATE")
    
    req1 = request(b8, claim, rec, "HELD", refs=("ref_1", "ref_2"))
    req_r3 = request(b8, claim, rec, "HELD", refs=("ref_2", "ref_1"))
    req_r4 = request(b8, claim, rec, "HELD", refs=("ref_1", "ref_1", "ref_2"))
    
    # We must apply req1 and create a receipt
    res1 = evaluate(b8, snapshot(b8, [(claim, rec)], slot_id=claim.slot_id), req1)
    
    # Now simulate the applied receipt in a new snapshot
    snap2 = b8.SlotSnapshot(slot_id=claim.slot_id, slot_revision=REVISION, records=(rec,),
                            applied_requests={req1.request_id: res1.receipt}, claims=(claim,))
                            
    res_r3 = evaluate(b8, snap2, req_r3)
    res_r4 = evaluate(b8, snap2, req_r4)
    
    assert res_r3.verdict == b8.TransitionVerdict.NO_OP_DUPLICATE
    assert res_r3.receipt == res1.receipt
    
    assert res_r4.verdict == b8.TransitionVerdict.NO_OP_DUPLICATE
    assert res_r4.receipt == res1.receipt
