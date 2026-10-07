"""RED tranche 2 — T6 VERIFIED → PROMOTED: free slot on CURRENT promoted state, open contradiction, human review
(spec §6, §7, §8, §9.1, §9.2 T6, §9.4, §9.5, §10)."""
from __future__ import annotations

import pytest

from tests.b8.red2_support import (
    FRAME_B, assert_applied, assert_rejected, attestation, evaluate, evidence, ids, latest, make_claim, make_record,
    request, snapshot,
)


def _t6(b8, others=(), *, cls="CODE_BUILD_CLAIM", start=0, end=100, revision=5):
    """Candidate VERIFIED on [start, end) in FRAME_A; `others` = (lineage, state, start, end, frame) on the slot."""
    cand = make_claim(b8, "candidate", cls=cls, start=start, end=end)
    entries = [(cand, make_record(b8, cand, "VERIFIED"))]
    for lineage, state, s, e, fid in others:
        other = make_claim(b8, lineage, cls=cls, start=s, end=e, fid=fid)
        entries.append((other, make_record(b8, other, state, contested_by=(cand.claim_id,) if state == "CONTESTED" else ())))
    return cand, snapshot(b8, entries, slot_id=cand.slot_id, revision=revision)


def _promote(b8, cand, snap, artifacts=(), **kw):
    return evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED", refs=ids(*artifacts), **kw), artifacts)


def test_t6_free_slot_promotes_once(b8):
    cand, snap = _t6(b8)
    result = _promote(b8, cand, snap)
    assert_applied(b8, snap, result, cand, "PROMOTED")
    assert result.snapshot.slot_revision == snap.slot_revision + 1


@pytest.mark.parametrize("s,e", [(9, 20), (0, 100), (50, 60), (-10, 1), (None, None)])
def test_t6_same_frame_overlapping_current_promoted_occupies_the_slot(b8, s, e):
    cand, snap = _t6(b8, [("occupant", "PROMOTED", s, e, "frame:lab-a")])
    assert_rejected(b8, snap, _promote(b8, cand, snap), ["slot_occupied"])


@pytest.mark.parametrize("s,e", [(100, 200), (-50, 0), (None, 0), (100, None)])
def test_t6_boundary_touching_or_disjoint_promoted_coexists(b8, s, e):
    cand, snap = _t6(b8, [("neighbour", "PROMOTED", s, e, "frame:lab-a")])
    assert_applied(b8, snap, _promote(b8, cand, snap), cand, "PROMOTED")


@pytest.mark.parametrize("state", ["SUPERSEDED", "INVALIDATED", "STALE"])
def test_t6_historical_promoted_whose_latest_state_is_not_promoted_does_not_occupy(b8, state):
    cand, snap = _t6(b8, [("former", state, 0, 100, "frame:lab-a")])
    assert_applied(b8, snap, _promote(b8, cand, snap), cand, "PROMOTED")


def test_t6_cross_frame_occupant_is_indeterminate_never_slot_occupied(b8):
    cand, snap = _t6(b8, [("occupant", "PROMOTED", 0, 100, FRAME_B)])
    assert_rejected(b8, snap, _promote(b8, cand, snap), ["temporal_relation_indeterminate"])


def test_t6_multi_cause_stale_and_indeterminate(b8):
    """§9.1 example: stale expected_slot_revision + PROMOTED occupant in another frame."""
    cand, snap = _t6(b8, [("occupant", "PROMOTED", 0, 100, FRAME_B)])
    result = _promote(b8, cand, snap, revision=4)
    assert_rejected(b8, snap, result, ["stale_request", "temporal_relation_indeterminate"])


def test_t6_multi_cause_stale_and_occupied(b8):
    cand, snap = _t6(b8, [("occupant", "PROMOTED", 0, 100, "frame:lab-a")])
    assert_rejected(b8, snap, _promote(b8, cand, snap, revision=6), ["slot_occupied", "stale_request"])


def test_t6_occupied_slot_requires_t9_not_a_second_promotion(b8):
    cand, snap = _t6(b8, [("occupant", "PROMOTED", 0, 100, "frame:lab-a")])
    result = _promote(b8, cand, snap)
    promoted = [r for r in result.snapshot.records if r.state is b8.ClaimState.PROMOTED]
    assert len(promoted) == 1 and result.bundle is None


# ---------------------------------------------------------------- open contradiction

def test_t6_open_contradiction_on_slot_time_rejects(b8):
    cand, snap = _t6(b8, [("contradictor", "CONTESTED", 20, 30, "frame:lab-a")])
    assert_rejected(b8, snap, _promote(b8, cand, snap), ["open_contradiction"])


def test_t6_contradiction_outside_valid_time_does_not_block(b8):
    cand, snap = _t6(b8, [("contradictor", "CONTESTED", 100, 200, "frame:lab-a")])
    assert_applied(b8, snap, _promote(b8, cand, snap), cand, "PROMOTED")


def test_t6_cross_frame_contradiction_is_indeterminate(b8):
    cand, snap = _t6(b8, [("contradictor", "CONTESTED", 0, 100, FRAME_B)])
    assert_rejected(b8, snap, _promote(b8, cand, snap), ["temporal_relation_indeterminate"])


@pytest.mark.parametrize("support", ["confidence", "majority"])
def test_t6_no_winner_by_confidence_or_majority(b8, support):
    cand, snap = _t6(b8, [("contradictor", "CONTESTED", 20, 30, "frame:lab-a")])
    arts = ([evidence(b8, cand, confidence=0.999)] if support == "confidence"
            else [evidence(b8, cand, source_ref=f"src:{i}") for i in range(5)])
    assert_rejected(b8, snap, _promote(b8, cand, snap, arts), ["open_contradiction"])


# ---------------------------------------------------------------- human review (requires_human_review=True)

H = "HUMAN_DECLARATION"


def test_t6_review_class_without_authorization_is_attestation_missing(b8):
    cand, snap = _t6(b8, cls=H)
    assert_rejected(b8, snap, _promote(b8, cand, snap), ["attestation_missing"])


def test_t6_review_class_untrusted_authorization_is_attestation_inadmissible(b8):
    cand, snap = _t6(b8, cls=H)
    att = attestation(b8, cand, kind="REVIEW_AUTHORIZATION", identity_source="display-name:Alice")
    assert_rejected(b8, snap, _promote(b8, cand, snap, [att]), ["attestation_inadmissible"])


def test_t6_primary_declaration_does_not_satisfy_review_authorization(b8):
    cand, snap = _t6(b8, cls=H)
    assert_rejected(b8, snap, _promote(b8, cand, snap, [attestation(b8, cand)]), ["attestation_missing"])


def test_t6_valid_review_authorization_promotes(b8):
    cand, snap = _t6(b8, cls=H)
    att = attestation(b8, cand, kind="REVIEW_AUTHORIZATION")
    assert_applied(b8, snap, _promote(b8, cand, snap, [att]), cand, "PROMOTED")


def test_t6_review_authorization_satisfies_only_its_own_precondition(b8):
    cand, snap = _t6(b8, [("occupant", "PROMOTED", 0, 100, "frame:lab-a")], cls=H)
    att = attestation(b8, cand, kind="REVIEW_AUTHORIZATION")
    assert_rejected(b8, snap, _promote(b8, cand, snap, [att]), ["slot_occupied"])


def test_t6_human_authorization_never_substitutes_for_verification(b8):
    claim = make_claim(b8, "unverified")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "SUPPORTED"))], slot_id=claim.slot_id)
    att = attestation(b8, claim, kind="REVIEW_AUTHORIZATION")
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), "PROMOTED", refs=ids(att)), [att])
    assert_rejected(b8, snap, result, ["forbidden_transition"])
