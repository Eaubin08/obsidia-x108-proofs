"""A2-Evidence remediation RED — mixed evidence facts (spec §9.1 complete set, §9.5 evidence_inadmissible /
ref_binding_mismatch, SA5 "N independent facts yield the code of each").

Frozen partition (E1–E6): a wrongly bound EvidenceRef alone is ref_binding_mismatch only (§9.5 "a wrongly bound
ref is ref_binding_mismatch only"); that clause covers the wrongly bound ref itself, never a different correctly
bound but inadmissible EvidenceRef, which keeps its own evidence_inadmissible. Any correctly bound admissible
EvidenceRef satisfies the prerequisite (EXISTS_ADMISSIBLE_EVIDENCE = EVIDENCE_PREREQUISITE_SATISFIED).
"""
from __future__ import annotations

import itertools

import pytest

from tests.b8.red2_support import (
    assert_applied, assert_rejected, evaluate, evidence, ids, latest, make_claim, make_record, request, snapshot,
)

TRANSITIONS = [("CANDIDATE", "SUPPORTED"), ("HELD", "SUPPORTED"), ("PROMOTED", "INVALIDATED"),
               ("STALE", "INVALIDATED")]
WRONG_BINDINGS = {"claim_version": {"claim_version": 2}, "claim_id": {"claim_id": "b8claim_" + "9" * 64}}

# (valid, weak, wrong) counts — the matrix of the ticket plus E1..E6
COMBINATIONS = [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 0), (0, 2, 0), (0, 1, 1), (0, 1, 2), (0, 2, 1),
                (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]


def _expected(valid, weak, wrong):
    reasons = set()
    if not valid and (weak or not wrong):    # E1, E3, E4 — never for wrongly-bound-only (E2)
        reasons.add("evidence_inadmissible")
    if wrong:
        reasons.add("ref_binding_mismatch")
    return sorted(reasons)


def _artifacts(b8, claim, valid, weak, wrong, binding="claim_version"):
    arts = [evidence(b8, claim, source_ref=f"src:valid-{i}") for i in range(valid)]
    arts += [evidence(b8, claim, provenance=(), source_ref=f"src:weak-{i}") for i in range(weak)]
    arts += [evidence(b8, claim, source_ref=f"src:wrong-{i}", **WRONG_BINDINGS[binding]) for i in range(wrong)]
    return arts


def _world(b8, frm):
    claim = make_claim(b8, "evidence-subject")
    return claim, snapshot(b8, [(claim, make_record(b8, claim, frm))], slot_id=claim.slot_id)


@pytest.mark.parametrize("binding", sorted(WRONG_BINDINGS))
@pytest.mark.parametrize("counts", COMBINATIONS, ids=lambda c: "valid{}-weak{}-wrong{}".format(*c))
@pytest.mark.parametrize("pair", TRANSITIONS, ids=lambda p: f"{p[0]}->{p[1]}")
def test_evidence_partition_matrix(b8, pair, counts, binding):
    frm, target = pair
    claim, snap = _world(b8, frm)
    arts = _artifacts(b8, claim, *counts, binding=binding)
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), target, refs=ids(*arts)), arts)
    expected = _expected(*counts)
    if expected:
        assert_rejected(b8, snap, result, expected)
    else:
        assert_applied(b8, snap, result, claim, target)


@pytest.mark.parametrize("pair", TRANSITIONS, ids=lambda p: f"{p[0]}->{p[1]}")
def test_mixed_wrong_and_bound_inadmissible_primary_witness(b8, pair):
    """T4_ / T10_MIXED_EVIDENCE_REASON_LOSS: two independent facts, two codes."""
    claim, snap = _world(b8, pair[0])
    arts = [evidence(b8, claim, claim_version=2), evidence(b8, claim, provenance=(), source_ref="src:weak")]
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), pair[1], refs=ids(*arts)), arts)
    assert_rejected(b8, snap, result, ["evidence_inadmissible", "ref_binding_mismatch"])


@pytest.mark.parametrize("pair", TRANSITIONS, ids=lambda p: f"{p[0]}->{p[1]}")
def test_wrong_bound_only_stays_binding_only(b8, pair):
    """Hard regression guard: WRONG_BOUND_ONLY_EXTRA_EVIDENCE_REASON=0."""
    claim, snap = _world(b8, pair[0])
    arts = [evidence(b8, claim, claim_version=2)]
    result = evaluate(b8, snap, request(b8, claim, latest(snap, claim), pair[1], refs=ids(*arts)), arts)
    assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


@pytest.mark.parametrize("counts", [c for c in COMBINATIONS if sum(c) > 1], ids=lambda c: "v{}-w{}-x{}".format(*c))
def test_mixed_evidence_outcome_is_artifact_order_independent(b8, counts):
    """A2_EVIDENCE_ARTIFACT_ORDER_DIVERGENCES=0 (request refs fixed; ref order is Class C)."""
    claim, snap = _world(b8, "CANDIDATE")
    arts = _artifacts(b8, claim, *counts)
    req = request(b8, claim, latest(snap, claim), "SUPPORTED", refs=ids(*arts))
    prints = set()
    for perm in itertools.permutations(arts):
        r = evaluate(b8, snap, req, list(perm))
        prints.add((r.verdict, tuple(x.value for x in r.receipt.reasons), r.receipt.canonical_json(),
                    r.receipt.receipt_id))
    assert len(prints) == 1
