"""Class A3 remediation RED — T6 / T9 need a complete canonical slot claim registry (spec §9.2 T6 / T9, §9.3,
§9.5 malformed_object, SA7 "incomparability never yields ... free slot").

CURRENT_RECORD_WITHOUT_CLAIM_OBJECT = SLOT_SEMANTICS_NOT_EVALUABLE: for T6 / T9 every current record of the
snapshot must have exactly one KnowledgeClaim in ``snapshot.claims`` (the canonical registry for this tranche);
otherwise REJECTED ``malformed_object``. A KnowledgeClaim supplied only through ``artifacts=`` never completes the
slot view (UNREFERENCED_ARTIFACT_CREATES_SLOT_OCCUPANT=NO), no claim is reconstructed from records, and
transitions that do not need the slot-wide view are unaffected (GLOBAL_MISSING_CLAIM_REJECTION=NO).
"""
from __future__ import annotations

import dataclasses
import itertools

import pytest

from tests.b8.conftest import RECORDED_AT, candidate_snapshot, hold_request
from tests.b8.red2_support import assert_rejected, evaluate, make_claim, make_record, reason_values, request


def _world(b8, occupant_state="PROMOTED"):
    occ = make_claim(b8, "occupant")
    new = make_claim(b8, "newcomer", start=50, end=150)
    return occ, new, make_record(b8, occ, occupant_state, rv=4), make_record(b8, new, "VERIFIED")


def _slot_snap(b8, slot_id, claims, records):
    return b8.SlotSnapshot(slot_id=slot_id, slot_revision=5, records=tuple(records), applied_requests={},
                           claims=tuple(claims))


# ---------------------------------------------------------------- primary reproducer

def test_second_promotion_with_missing_occupant_claim_object_is_rejected(b8):
    """SECOND_PROMOTION_WITH_MISSING_OCCUPANT_CLAIM=0."""
    occ, new, occ_rec, new_rec = _world(b8)
    snap = _slot_snap(b8, new.slot_id, [new], [occ_rec, new_rec])
    assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")), ["malformed_object"])


@pytest.mark.parametrize("referenced", [False, True])
def test_artifact_claim_object_never_repairs_the_slot_view(b8, referenced):
    """UNREFERENCED_ARTIFACT_REPAIRS_SLOT_VIEW=0 (and a referenced one is no registry either)."""
    occ, new, occ_rec, new_rec = _world(b8)
    snap = _slot_snap(b8, new.slot_id, [new], [occ_rec, new_rec])
    refs = (occ.claim_id,) if referenced else ()
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED", refs=refs), [occ])
    assert_rejected(b8, snap, result, ["malformed_object"])


@pytest.mark.parametrize("state", ["CANDIDATE", "HELD", "SUPPORTED", "VERIFIED", "CONTESTED", "STALE",
                                   "INVALIDATED", "SUPERSEDED", "REJECTED"])
def test_any_current_record_without_claim_object_makes_t6_not_evaluable(b8, state):
    """UNKNOWN_CURRENT_RECORD_SEMANTICS_IGNORED=0: its valid_time / frame / slot are unknown."""
    occ, new, occ_rec, new_rec = _world(b8, state)
    snap = _slot_snap(b8, new.slot_id, [new], [occ_rec, new_rec])
    assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")), ["malformed_object"])


def test_missing_claim_rejection_is_independent_of_record_order(b8):
    """A3_ORDER_DIVERGENCES=0."""
    occ, new, occ_rec, new_rec = _world(b8)
    prints = set()
    for perm in itertools.permutations([occ_rec, new_rec]):
        snap = _slot_snap(b8, new.slot_id, [new], perm)
        r = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
        prints.add((r.verdict, tuple(reason_values(r)), r.receipt.canonical_json(), r.receipt.receipt_id))
    assert len(prints) == 1
    (fp,) = prints
    assert fp[0] is b8.TransitionVerdict.REJECTED and fp[1] == ("malformed_object",)


# ---------------------------------------------------------------- T9

def test_t9_missing_predecessor_claim_object_never_yields_empty_e(b8):
    """T9_MISSING_CLAIM_FALSE_EMPTY_E=0."""
    pred = make_claim(b8, "pred", start=10, end=20)
    new = make_claim(b8, "new")
    pred_rec, new_rec = make_record(b8, pred, "PROMOTED"), make_record(b8, new, "VERIFIED")
    snap = _slot_snap(b8, new.slot_id, [new], [pred_rec, new_rec])
    req = request(b8, new, new_rec, "PROMOTED", supersedes_claim_id=pred.claim_id,
                  supersedes_record_id=pred_rec.record_id)
    reasons = assert_rejected(b8, snap, evaluate(b8, snap, req, [pred]))
    assert "malformed_object" in reasons
    assert not {"no_eligible_predecessor", "multiple_predecessors_unsupported", "predecessor_mismatch",
                "containment_not_satisfied"} & set(reasons)
    assert reasons == ["malformed_object"]


def test_t9_bystander_record_without_claim_object_is_not_evaluable(b8):
    pred = make_claim(b8, "pred", start=10, end=20)
    new = make_claim(b8, "new")
    ghost = make_claim(b8, "ghost", start=30, end=40)
    recs = [make_record(b8, pred, "PROMOTED"), make_record(b8, new, "VERIFIED"), make_record(b8, ghost, "PROMOTED")]
    snap = _slot_snap(b8, new.slot_id, [pred, new], recs)
    req = request(b8, new, recs[1], "PROMOTED", supersedes_claim_id=pred.claim_id,
                  supersedes_record_id=recs[0].record_id)
    assert_rejected(b8, snap, evaluate(b8, snap, req), ["malformed_object"])


# ---------------------------------------------------------------- historical / non slot-wide controls

def test_historical_records_of_a_registered_claim_create_no_completeness_failure(b8):
    """HISTORICAL_ONLY_RECORD_FALSE_MALFORMED=0: the guard reads current claims after current_records()."""
    occ, new, _, new_rec = _world(b8)
    old = b8.KnowledgeRecord(claim_id=occ.claim_id, claim_version=1, record_version=3,
                             state=b8.ClaimState.PROMOTED, previous_record_id=None)
    cur = b8.KnowledgeRecord(claim_id=occ.claim_id, claim_version=1, record_version=4,
                             state=b8.ClaimState.STALE, previous_record_id=old.record_id)
    snap = _slot_snap(b8, new.slot_id, [occ, new], [old, cur, new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"))
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)


def test_non_slot_wide_t2_without_claim_registry_is_unchanged(b8):
    """NON_SLOT_WIDE_TRANSITION_REGRESSIONS=0 (RED-1 contract: T2 needs no claim object)."""
    snap = candidate_snapshot(b8)
    result = b8.evaluate_transition(snap, hold_request(b8), recorded_at=RECORDED_AT)
    assert result.verdict is b8.TransitionVerdict.APPLIED and result.snapshot.slot_revision == 4


def test_non_slot_wide_t10_with_an_orphan_record_is_unchanged(b8):
    occ, new, occ_rec, _ = _world(b8)
    subject = make_record(b8, new, "PROMOTED")
    snap = _slot_snap(b8, new.slot_id, [new], [occ_rec, subject])
    from tests.b8.red2_support import evidence, ids
    ev = evidence(b8, new, kind="WITHDRAWAL")
    result = evaluate(b8, snap, request(b8, new, subject, "INVALIDATED", refs=ids(ev)), [ev])
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)


# ---------------------------------------------------------------- ambiguous / disagreeing claim objects

def _twin(claim):
    """Same claim_id (identity fields equal), distinct object (non-identity provenance differs)."""
    twin = dataclasses.replace(claim, source_refs=("src:other",))
    assert twin.claim_id == claim.claim_id and twin != claim
    return twin


def test_duplicate_distinct_occupant_claim_objects_fail_closed(b8):
    """AMBIGUOUS_CLAIM_OBJECT_APPLIED=0."""
    occ, new, occ_rec, new_rec = _world(b8)
    for claims in ([occ, _twin(occ), new], [_twin(occ), new, occ]):
        snap = _slot_snap(b8, new.slot_id, claims, [occ_rec, new_rec])
        assert "malformed_object" in assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")))


def test_duplicate_distinct_subject_claim_objects_fail_closed(b8):
    new = make_claim(b8, "newcomer")
    new_rec = make_record(b8, new, "VERIFIED")
    snap = _slot_snap(b8, new.slot_id, [new, _twin(new)], [new_rec])
    assert "malformed_object" in assert_rejected(b8, snap, evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED")))


def test_subject_artifact_disagreeing_with_registry_fails_closed(b8):
    new = make_claim(b8, "newcomer")
    new_rec = make_record(b8, new, "VERIFIED")
    snap = _slot_snap(b8, new.slot_id, [new], [new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"), [_twin(new)])
    assert "malformed_object" in assert_rejected(b8, snap, result)


def test_subject_supplied_only_as_artifact_does_not_complete_t6(b8):
    new = make_claim(b8, "newcomer")
    new_rec = make_record(b8, new, "VERIFIED")
    snap = _slot_snap(b8, new.slot_id, [], [new_rec])
    result = evaluate(b8, snap, request(b8, new, new_rec, "PROMOTED"), [new])
    assert_rejected(b8, snap, result, ["malformed_object"])
