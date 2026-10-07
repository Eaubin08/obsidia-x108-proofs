"""RED tranche 2 — T7 CONTESTED, T8 resolution, T10 INVALIDATED, T11 STALE (spec §6, §8, §9.2, §9.5)."""
from __future__ import annotations

import pytest

from tests.b8.red2_support import (
    FRAME_A, FRAME_B, assert_applied, assert_rejected, evaluate, evidence, ids, latest, make_claim, make_record,
    reason_values, request, snapshot, verification,
)


def _world(b8, state, *, cls="CODE_BUILD_CLAIM", others=(), contested_by_others=False):
    claim = make_claim(b8, "subject", cls=cls)
    other_claims = [make_claim(b8, lin, cls=cls, start=s, end=e, fid=fid) for lin, _, s, e, fid in others]
    contested_by = tuple(o.claim_id for o in other_claims) if contested_by_others else ()
    entries = [(claim, make_record(b8, claim, state, contested_by=contested_by))]
    entries += [(o, make_record(b8, o, st)) for o, (_, st, _, _, _) in zip(other_claims, others)]
    return claim, other_claims, snapshot(b8, entries, slot_id=claim.slot_id)


def _go(b8, claim, snap, target, artifacts=(), extra_refs=(), **kw):
    req = request(b8, claim, latest(snap, claim), target, refs=tuple(extra_refs) + ids(*artifacts), **kw)
    return evaluate(b8, snap, req, artifacts)


# ---------------------------------------------------------------- T7

@pytest.mark.parametrize("frm", ["SUPPORTED", "VERIFIED", "PROMOTED"])
def test_t7_admissible_contradicting_evidence_contests(b8, frm):
    claim, _, snap = _world(b8, frm)
    after = assert_applied(b8, snap, _go(b8, claim, snap, "CONTESTED", [evidence(b8, claim, kind="COUNTER_TEST")]),
                           claim, "CONTESTED")
    assert after.claim_version == claim.claim_version


@pytest.mark.parametrize("frm", ["SUPPORTED", "VERIFIED", "PROMOTED"])
def test_t7_without_contradiction_refs_is_contradiction_inadmissible(b8, frm):
    claim, _, snap = _world(b8, frm)
    assert_rejected(b8, snap, _go(b8, claim, snap, "CONTESTED"), ["contradiction_inadmissible"])


def test_t7_evidence_without_provenance_is_contradiction_inadmissible(b8):
    claim, _, snap = _world(b8, "PROMOTED")
    result = _go(b8, claim, snap, "CONTESTED", [evidence(b8, claim, provenance=())])
    assert_rejected(b8, snap, result, ["contradiction_inadmissible"])


def test_t7_same_frame_overlapping_contradicting_claim_contests_with_refs(b8):
    claim, (rival,), snap = _world(b8, "PROMOTED", others=[("rival", "SUPPORTED", 20, 30, FRAME_A)])
    after = assert_applied(b8, snap, _go(b8, claim, snap, "CONTESTED", extra_refs=(rival.claim_id,)),
                           claim, "CONTESTED")
    assert rival.claim_id in after.contested_by


def test_t7_cross_frame_claim_reference_never_infers_a_temporal_contradiction(b8):
    claim, (rival,), snap = _world(b8, "PROMOTED", others=[("rival", "SUPPORTED", 0, 100, FRAME_B)])
    result = _go(b8, claim, snap, "CONTESTED", extra_refs=(rival.claim_id,))
    assert_rejected(b8, snap, result, ["temporal_relation_indeterminate"])


def test_t7_same_frame_disjoint_claim_is_not_a_contradiction(b8):
    claim, (rival,), snap = _world(b8, "PROMOTED", others=[("rival", "SUPPORTED", 100, 200, FRAME_A)])
    result = _go(b8, claim, snap, "CONTESTED", extra_refs=(rival.claim_id,))
    assert_rejected(b8, snap, result, ["contradiction_inadmissible"])


# ---------------------------------------------------------------- T8

@pytest.mark.parametrize("side_state", ["INVALIDATED", "REJECTED"])
def test_t8_resolved_when_contradicting_side_is_withdrawn(b8, side_state):
    claim, (side,), snap = _world(b8, "CONTESTED", others=[("side", side_state, 20, 30, FRAME_A)],
                                  contested_by_others=True)
    assert_applied(b8, snap, _go(b8, claim, snap, "SUPPORTED", extra_refs=(side.claim_id,)), claim, "SUPPORTED")


def test_t8_resolved_by_new_verification_refs(b8):
    claim, _, snap = _world(b8, "CONTESTED", others=[("side", "SUPPORTED", 20, 30, FRAME_A)], contested_by_others=True)
    assert_applied(b8, snap, _go(b8, claim, snap, "SUPPORTED", [verification(b8, claim)]), claim, "SUPPORTED")


@pytest.mark.parametrize("case", ["no_refs", "side_still_current", "confidence", "majority"])
def test_t8_unresolved_contradiction(b8, case):
    claim, (side,), snap = _world(b8, "CONTESTED", others=[("side", "PROMOTED", 20, 30, FRAME_A)],
                                  contested_by_others=True)
    arts, refs = [], ()
    if case == "side_still_current":
        refs = (side.claim_id,)
    elif case == "confidence":
        arts = [evidence(b8, claim, confidence=0.999)]
    elif case == "majority":
        arts = [evidence(b8, claim, source_ref=f"src:{i}") for i in range(5)]
    assert_rejected(b8, snap, _go(b8, claim, snap, "SUPPORTED", arts, extra_refs=refs), ["contradiction_unresolved"])


def test_t8_then_t5_and_t6_are_required_again(b8):
    claim, (side,), snap = _world(b8, "CONTESTED", others=[("side", "INVALIDATED", 20, 30, FRAME_A)],
                                  contested_by_others=True)
    result = _go(b8, claim, snap, "SUPPORTED", extra_refs=(side.claim_id,))
    assert latest(result.snapshot, claim).state is b8.ClaimState.SUPPORTED
    direct = _go(b8, claim, result.snapshot, "PROMOTED", revision=result.snapshot.slot_revision)
    assert reason_values(direct) == ["forbidden_transition"]


# ---------------------------------------------------------------- T10

T10_SOURCES = ("CANDIDATE", "HELD", "SUPPORTED", "VERIFIED", "PROMOTED", "CONTESTED", "STALE")


@pytest.mark.parametrize("frm", T10_SOURCES)
def test_t10_reason_and_evidence_invalidate(b8, frm):
    claim, _, snap = _world(b8, frm)
    assert_applied(b8, snap, _go(b8, claim, snap, "INVALIDATED", [evidence(b8, claim, kind="WITHDRAWAL")]),
                   claim, "INVALIDATED")


@pytest.mark.parametrize("frm", T10_SOURCES)
def test_t10_without_evidence_is_evidence_inadmissible(b8, frm):
    claim, _, snap = _world(b8, frm)
    assert_rejected(b8, snap, _go(b8, claim, snap, "INVALIDATED"), ["evidence_inadmissible"])


def test_t10_without_reason_and_evidence_reports_both(b8):
    claim, _, snap = _world(b8, "PROMOTED")
    assert_rejected(b8, snap, _go(b8, claim, snap, "INVALIDATED", reason=""),
                    ["evidence_inadmissible", "reason_missing"])


def test_t10_without_reason_only(b8):
    claim, _, snap = _world(b8, "PROMOTED")
    result = _go(b8, claim, snap, "INVALIDATED", [evidence(b8, claim, kind="WITHDRAWAL")], reason="")
    assert_rejected(b8, snap, result, ["reason_missing"])


# ---------------------------------------------------------------- T11

T11_CASES = [
    ("CODE_BUILD_CLAIM", "SOURCE_VERSION_CHANGE", True),
    ("CODE_BUILD_CLAIM", "TTL", False),                      # no generic TTL
    ("CODE_BUILD_CLAIM", "VALID_UNTIL", False),
    ("FORMAL_CLAIM", "SOURCE_VERSION_CHANGE", True),         # change of assumptions
    ("FORMAL_CLAIM", "TTL", False),                          # NEVER_BY_TIME
    ("FORMAL_CLAIM", "VALID_UNTIL", False),
    ("DOCUMENTARY_CLAIM", "VALID_UNTIL", True),
    ("DOCUMENTARY_CLAIM", "TTL", False),
    ("PHYSICAL_CLAIM", "DOMAIN_POLICY", True),
    ("PHYSICAL_CLAIM", "TTL", False),
    ("HUMAN_DECLARATION", "CONDITION_TRIGGER", True),
    ("HUMAN_DECLARATION", "TTL", False),
]


@pytest.mark.parametrize("cls,mechanism,admissible", T11_CASES)
def test_t11_requires_trigger_evidence_of_the_class_mechanism(b8, cls, mechanism, admissible):
    claim, _, snap = _world(b8, "PROMOTED", cls=cls)
    result = _go(b8, claim, snap, "STALE", [evidence(b8, claim, kind=mechanism)])
    if admissible:
        assert_applied(b8, snap, result, claim, "STALE")
    else:
        assert_rejected(b8, snap, result, ["staleness_trigger_inadmissible"])


def test_t11_without_trigger_evidence(b8):
    claim, _, snap = _world(b8, "PROMOTED")
    assert_rejected(b8, snap, _go(b8, claim, snap, "STALE"), ["staleness_trigger_inadmissible"])
