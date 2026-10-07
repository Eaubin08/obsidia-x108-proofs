"""RED tranche 2 — complete claim state graph T1–T12 and its fail-closed complement (spec §9.2, §9.4, §9.5)."""
from __future__ import annotations

import itertools
import re

import pytest

from tests.b8.red2_support import (
    assert_applied, assert_rejected, evaluate, evidence, ids, latest, make_claim, make_record,
    request, snapshot, verification,
)

STATES = ("CANDIDATE", "HELD", "REJECTED", "SUPPORTED", "VERIFIED", "PROMOTED", "CONTESTED", "SUPERSEDED",
          "INVALIDATED", "STALE")

# §9.2, derived row by row (T1 ∅ → CANDIDATE is the only pair without a source state)
LEGAL_RULES = {
    "T1": [(None, "CANDIDATE")],
    "T2": [("CANDIDATE", "HELD")],
    "T3": [("CANDIDATE", "REJECTED"), ("HELD", "REJECTED")],
    "T4": [("CANDIDATE", "SUPPORTED"), ("HELD", "SUPPORTED")],
    "T5": [("SUPPORTED", "VERIFIED")],
    "T6": [("VERIFIED", "PROMOTED")],
    "T7": [("SUPPORTED", "CONTESTED"), ("VERIFIED", "CONTESTED"), ("PROMOTED", "CONTESTED")],
    "T8": [("CONTESTED", "SUPPORTED")],
    "T9": [("VERIFIED", "PROMOTED"), ("PROMOTED", "SUPERSEDED")],
    "T10": [(s, "INVALIDATED") for s in ("CANDIDATE", "HELD", "SUPPORTED", "VERIFIED", "PROMOTED", "CONTESTED",
                                         "STALE")],
    "T11": [("PROMOTED", "STALE")],
    "T12": [("STALE", "VERIFIED")],
}
LEGAL_PAIRS = sorted({p for pairs in LEGAL_RULES.values() for p in pairs}, key=str)
STATE_PAIRS = [p for p in LEGAL_PAIRS if p[0] is not None]
COMPLEMENT = [(f, t) for f, t in itertools.product(STATES, STATES) if (f, t) not in STATE_PAIRS]
HOSTILE = [("CANDIDATE", "VERIFIED"), ("CANDIDATE", "PROMOTED"), ("HELD", "VERIFIED"), ("HELD", "PROMOTED"),
           ("SUPPORTED", "PROMOTED"), ("STALE", "PROMOTED"), ("CONTESTED", "VERIFIED"), ("CONTESTED", "PROMOTED")]
HOSTILE += [(terminal, t) for terminal in ("REJECTED", "INVALIDATED", "SUPERSEDED") for t in STATES]


def test_legal_graph_matches_the_closed_spec_rows(spec_text):
    sec = spec_text[spec_text.index("### 9.2 Rules"):spec_text.index("### 9.3")]
    rows = dict(re.findall(r"^\| (T\d+) \| ([^|]+) \|", sec, re.M))
    assert sorted(rows, key=lambda k: int(k[1:])) == list(LEGAL_RULES)
    for rule, cell in rows.items():
        if rule in ("T1", "T9"):
            continue
        src, dst = cell.split("→")
        dst = dst.split("(")[0].strip()
        expected = sorted((s.strip(), dst) for s in src.split("/"))
        assert sorted(LEGAL_RULES[rule]) == expected, rule
    assert "Claim (from, to) pairs: 22" in spec_text
    assert len(LEGAL_PAIRS) == 22 and len(STATE_PAIRS) == 21 and len(COMPLEMENT) == 79


def test_hostile_pairs_are_all_in_the_complement():
    assert set(HOSTILE) <= set(COMPLEMENT)


@pytest.mark.parametrize("pair", COMPLEMENT, ids=lambda p: f"{p[0]}->{p[1]}")
def test_every_unlisted_pair_fails_closed_with_forbidden_transition(b8, pair):
    frm, to = pair
    claim = make_claim(b8, "graph")
    snap = snapshot(b8, [(claim, make_record(b8, claim, frm))], slot_id=claim.slot_id)
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), to))
    assert_rejected(b8, snap, result, ["forbidden_transition"])  # ILLEGAL_STATE_TRANSITIONS_APPLIED=0


def test_half_t9_promoted_to_superseded_outside_a_bundle_is_forbidden(b8):
    claim = make_claim(b8, "half-t9")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "PROMOTED"))], slot_id=claim.slot_id)
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), "SUPERSEDED"))
    assert_rejected(b8, snap, result, ["forbidden_transition"])


def _legal_witness(b8, frm, to):
    """A snapshot + request + artifacts meeting every §9.2 precondition of the (frm → to) rule."""
    claim = make_claim(b8, "witness")
    entries, artifacts, refs = [], [], ()
    record = make_record(b8, claim, frm)
    if to in ("SUPPORTED",) and frm in ("CANDIDATE", "HELD"):                     # T4
        artifacts = [evidence(b8, claim)]
    elif (frm, to) in (("SUPPORTED", "VERIFIED"), ("STALE", "VERIFIED")):          # T5 / T12
        artifacts = [verification(b8, claim)]
    elif to == "CONTESTED":                                                         # T7
        artifacts = [evidence(b8, claim, kind="CONTRADICTING_TEST_LOG")]
    elif (frm, to) == ("CONTESTED", "SUPPORTED"):                                   # T8
        other = make_claim(b8, "contradicting-side")
        record = make_record(b8, claim, frm, contested_by=(other.claim_id,))
        entries.append((other, make_record(b8, other, "INVALIDATED")))
        refs = (other.claim_id,)
    elif to == "INVALIDATED":                                                       # T10
        artifacts = [evidence(b8, claim, kind="WITHDRAWAL_NOTICE")]
    elif to == "STALE":                                                             # T11 (CODE_BUILD mechanism)
        artifacts = [evidence(b8, claim, kind="SOURCE_VERSION_CHANGE")]
    snap = snapshot(b8, [(claim, record), *entries], slot_id=claim.slot_id)
    return claim, snap, request(b8, claim, record, to, refs=refs + ids(*artifacts)), artifacts


@pytest.mark.parametrize("pair", [p for p in STATE_PAIRS if p != ("PROMOTED", "SUPERSEDED")],
                         ids=lambda p: f"{p[0]}->{p[1]}")
def test_every_legal_single_claim_pair_applies_when_its_preconditions_hold(b8, pair):
    claim, snap, req, artifacts = _legal_witness(b8, *pair)
    result = evaluate(b8, snap, req, artifacts)
    assert_applied(b8, snap, result, claim, pair[1])
    assert result.receipt.from_state is b8.ClaimState(pair[0]) and result.receipt.to_state is b8.ClaimState(pair[1])


def test_t1_creates_candidate_record_version_one_and_is_idempotent(b8):
    claim = make_claim(b8, "t1")
    snap = b8.SlotSnapshot(slot_id=claim.slot_id, slot_revision=0, records=(), applied_requests={}, claims=())
    req = b8.TransitionRequest(claim_id=claim.claim_id, expected_claim_version=1, expected_state=None,
                               expected_record_version=0, slot_id=claim.slot_id, expected_slot_revision=0,
                               target_state=b8.ClaimState.CANDIDATE, refs=(), requester_ref="requester:test",
                               reason="capture")
    result = evaluate(b8, snap, req, [claim])
    assert result.verdict is b8.TransitionVerdict.APPLIED
    rec = latest(result.snapshot, claim)
    assert rec.state is b8.ClaimState.CANDIDATE and rec.record_version == 1 and rec.previous_record_id is None
    assert result.snapshot.slot_revision == 1 and claim in result.snapshot.claims
    assert snap.records == () and snap.slot_revision == 0
    again = evaluate(b8, result.snapshot, req, [claim])
    assert again.verdict is b8.TransitionVerdict.NO_OP_DUPLICATE and again.receipt == result.receipt
    assert again.snapshot == result.snapshot


def test_t1_requires_a_reason_and_only_targets_candidate(b8):
    claim = make_claim(b8, "t1-bad")
    snap = b8.SlotSnapshot(slot_id=claim.slot_id, slot_revision=0, records=(), applied_requests={}, claims=())
    base = dict(claim_id=claim.claim_id, expected_claim_version=1, expected_state=None, expected_record_version=0,
                slot_id=claim.slot_id, expected_slot_revision=0, refs=(), requester_ref="requester:test")
    no_reason = b8.TransitionRequest(target_state=b8.ClaimState.CANDIDATE, reason="", **base)
    assert_rejected(b8, snap, evaluate(b8, snap, no_reason, [claim]), ["reason_missing"])
    for target in ("HELD", "SUPPORTED", "VERIFIED", "PROMOTED"):
        bad = b8.TransitionRequest(target_state=b8.ClaimState(target), reason="capture", **base)
        assert_rejected(b8, snap, evaluate(b8, snap, bad, [claim]), ["forbidden_transition"])


def test_t3_requires_explicit_reasons(b8):
    for frm in ("CANDIDATE", "HELD"):
        claim = make_claim(b8, "t3")
        snap = snapshot(b8, [(claim, make_record(b8, claim, frm))], slot_id=claim.slot_id)
        result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), "REJECTED", reason="   "))
        assert_rejected(b8, snap, result, ["reason_missing"])


def test_rejected_state_is_not_a_rejected_verdict(b8):
    claim = make_claim(b8, "t3-ok")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "CANDIDATE"))], slot_id=claim.slot_id)
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), "REJECTED"))
    assert result.verdict is b8.TransitionVerdict.APPLIED
    assert latest(result.snapshot, claim).state is b8.ClaimState.REJECTED
