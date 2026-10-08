"""Class A2 remediation RED — attestation partition (spec §6, §7, §9.1 complete set, §9.5 SA5).

For a required attestation kind K, the candidates are the correctly bound attestations of kind K:
none → attestation_missing; candidates but none admissible → attestation_inadmissible. A wrongly bound
attestation is never a candidate and separately yields ref_binding_mismatch: the two facts are independent and
neither suppresses the other. Wrong kind != untrusted required kind.

Out of scope (frozen elsewhere, asserted here only as preservation): EvidenceRef rules (§9.5 "a wrongly bound
ref is ref_binding_mismatch only") and the SA5 VerificationRecord partition.
"""
from __future__ import annotations

import itertools

import pytest

from tests.b8.red2_support import (
    assert_rejected, attestation, evaluate, evidence, ids, latest, make_claim, make_record, reason_values, request,
    snapshot, verification,
)

H = "HUMAN_DECLARATION"


def _human(b8, state, cls=H):
    claim = make_claim(b8, "human", cls=cls)
    return claim, snapshot(b8, [(claim, make_record(b8, claim, state))], slot_id=claim.slot_id)


def _go(b8, claim, snap, target, artifacts):
    return evaluate(b8, snap, request(b8, claim, latest(snap, claim), target, refs=ids(*artifacts)), artifacts)


WRONG = [{"claim_version": 2}, {"claim_id": "b8claim_" + "9" * 64}]


# ---------------------------------------------------------------- T5 primary declaration

@pytest.mark.parametrize("cls", [H, "ORGANIZATIONAL_POLICY"])
@pytest.mark.parametrize("kind", ["PRIMARY_DECLARATION", "REVIEW_AUTHORIZATION", "ATTESTATION"])
@pytest.mark.parametrize("binding", WRONG)
def test_t5_only_wrongly_bound_attestation_is_missing_plus_binding(b8, cls, kind, binding):
    """HUMAN_T5_WRONG_BOUND_MISSING_REASON_LOST=0 (auditor witness: other kind, other claim)."""
    claim, snap = _human(b8, "SUPPORTED", cls)
    result = _go(b8, claim, snap, "VERIFIED", [attestation(b8, claim, kind=kind, **binding)])
    assert_rejected(b8, snap, result, ["attestation_missing", "ref_binding_mismatch"])


@pytest.mark.parametrize("decoy_kind", ["PRIMARY_DECLARATION", "REVIEW_AUTHORIZATION"])
def test_t5_valid_primary_with_wrong_decoy_is_binding_only(b8, decoy_kind):
    """VALID_PRIMARY_WITH_WRONG_DECOY_FALSE_MISSING=0."""
    claim, snap = _human(b8, "SUPPORTED")
    arts = [attestation(b8, claim), attestation(b8, claim, kind=decoy_kind, claim_version=2)]
    assert_rejected(b8, snap, _go(b8, claim, snap, "VERIFIED", arts), ["ref_binding_mismatch"])


@pytest.mark.parametrize("kind", ["REVIEW_AUTHORIZATION", "ATTESTATION"])
def test_t5_correctly_bound_wrong_kind_is_missing_not_inadmissible(b8, kind):
    """WRONG_KIND_AS_INADMISSIBLE=0, also when the wrong-kind attestation is untrusted."""
    claim, snap = _human(b8, "SUPPORTED")
    for source in ("idp:obsidia-test-boundary", "display-name:Alice"):
        result = _go(b8, claim, snap, "VERIFIED", [attestation(b8, claim, kind=kind, identity_source=source)])
        assert_rejected(b8, snap, result, ["attestation_missing"])


def test_t5_untrusted_required_kind_is_inadmissible_not_missing(b8):
    """UNTRUSTED_REQUIRED_KIND_AS_MISSING=0, with or without a wrongly bound decoy."""
    claim, snap = _human(b8, "SUPPORTED")
    untrusted = attestation(b8, claim, identity_source="display-name:Alice")
    assert_rejected(b8, snap, _go(b8, claim, snap, "VERIFIED", [untrusted]), ["attestation_inadmissible"])
    decoy = attestation(b8, claim, claim_version=2)
    assert_rejected(b8, snap, _go(b8, claim, snap, "VERIFIED", [untrusted, decoy]),
                    ["attestation_inadmissible", "ref_binding_mismatch"])


# ---------------------------------------------------------------- T6 / T9 review authorization

@pytest.mark.parametrize("kind", ["REVIEW_AUTHORIZATION", "PRIMARY_DECLARATION"])
@pytest.mark.parametrize("binding", WRONG)
def test_t6_only_wrongly_bound_review_is_missing_plus_binding(b8, kind, binding):
    """T6_WRONG_BOUND_REVIEW_MISSING_REASON_LOST=0."""
    claim, snap = _human(b8, "VERIFIED")
    result = _go(b8, claim, snap, "PROMOTED", [attestation(b8, claim, kind=kind, **binding)])
    assert_rejected(b8, snap, result, ["attestation_missing", "ref_binding_mismatch"])


def test_t6_valid_review_with_wrong_decoy_is_binding_only(b8):
    claim, snap = _human(b8, "VERIFIED")
    arts = [attestation(b8, claim, kind="REVIEW_AUTHORIZATION"),
            attestation(b8, claim, kind="REVIEW_AUTHORIZATION", claim_version=2)]
    assert_rejected(b8, snap, _go(b8, claim, snap, "PROMOTED", arts), ["ref_binding_mismatch"])


def test_t6_untrusted_bound_review_is_inadmissible_not_missing(b8):
    claim, snap = _human(b8, "VERIFIED")
    arts = [attestation(b8, claim, kind="REVIEW_AUTHORIZATION", identity_source="display-name:Alice"),
            attestation(b8, claim, kind="REVIEW_AUTHORIZATION", claim_version=2)]
    assert_rejected(b8, snap, _go(b8, claim, snap, "PROMOTED", arts),
                    ["attestation_inadmissible", "ref_binding_mismatch"])


def test_t9_only_wrongly_bound_review_is_missing_plus_binding(b8):
    new = make_claim(b8, "new", cls=H)
    pred = make_claim(b8, "pred", cls=H, start=10, end=20)
    snap = snapshot(b8, [(new, make_record(b8, new, "VERIFIED")), (pred, make_record(b8, pred, "PROMOTED"))],
                    slot_id=new.slot_id)
    att = attestation(b8, new, kind="REVIEW_AUTHORIZATION", claim_version=2)
    req = request(b8, new, latest(snap, new), "PROMOTED", refs=ids(att), supersedes_claim_id=pred.claim_id,
                  supersedes_record_id=latest(snap, pred).record_id)
    result = evaluate(b8, snap, req, [att])
    assert_rejected(b8, snap, result, ["attestation_missing", "ref_binding_mismatch"])
    assert result.bundle is None


# ---------------------------------------------------------------- order determinism

def test_a2_reason_sequence_and_receipt_are_order_independent(b8):
    """A2_REASON_ORDER_DIVERGENCES=0."""
    claim, snap = _human(b8, "SUPPORTED")
    arts = [attestation(b8, claim, kind="REVIEW_AUTHORIZATION", claim_version=2),
            attestation(b8, claim, kind="REVIEW_AUTHORIZATION"),
            attestation(b8, claim, claim_id="b8claim_" + "9" * 64)]
    req = request(b8, claim, latest(snap, claim), "VERIFIED", refs=ids(*arts))  # ref order is Class C, out of scope
    prints = set()
    for perm in itertools.permutations(arts):
        r = evaluate(b8, snap, req, list(perm))
        prints.add((tuple(reason_values(r)), r.receipt.canonical_json(), r.receipt.receipt_id))
    assert len(prints) == 1
    (fp,) = prints
    assert fp[0] == ("attestation_missing", "ref_binding_mismatch")


# ---------------------------------------------------------------- preservation (not changed by A2)

def test_evidence_wrongly_bound_only_stays_binding_only(b8):
    """§9.5 evidence_inadmissible: 'a wrongly bound ref is ref_binding_mismatch only' (frozen, unchanged)."""
    claim = make_claim(b8, "ev")
    for frm, target in (("CANDIDATE", "SUPPORTED"), ("PROMOTED", "INVALIDATED")):
        snap = snapshot(b8, [(claim, make_record(b8, claim, frm))], slot_id=claim.slot_id)
        result = _go(b8, claim, snap, target, [evidence(b8, claim, claim_version=2)])
        assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


@pytest.mark.parametrize("arts,expected", [
    ("wrong_only", ["ref_binding_mismatch"]),
    ("bound_not_satisfied", ["verification_not_satisfied"]),
    ("bound_wrong_family", ["verifier_inadmissible"]),
    ("wrong_plus_bound_not_satisfied", ["ref_binding_mismatch", "verification_not_satisfied"]),
])
def test_sa5_verification_partition_is_preserved(b8, arts, expected):
    """SA5_VERIFICATION_PARTITION_REGRESSIONS=0."""
    claim = make_claim(b8, "sa5")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "SUPPORTED"))], slot_id=claim.slot_id)
    wrong = verification(b8, claim, claim_version=2)
    unsat = verification(b8, claim, verdict="NOT_SATISFIED")
    family = verification(b8, claim, family="FORMAL_PROOF_VERIFIER")
    chosen = {"wrong_only": [wrong], "bound_not_satisfied": [unsat], "bound_wrong_family": [family],
              "wrong_plus_bound_not_satisfied": [wrong, unsat]}[arts]
    assert_rejected(b8, snap, _go(b8, claim, snap, "VERIFIED", chosen), expected)
