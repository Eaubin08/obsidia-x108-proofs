"""RED tranche 2 — evidence (T4), verification (T5 / T12) and human-attestation policy (spec §4, §6, §7, §9.2,
§9.5 SA5 atomic partition: ref_binding_mismatch / verifier_inadmissible / verification_not_satisfied disjoint)."""
from __future__ import annotations

import re

import pytest

from tests.b8.red2_support import (
    OBJECTIVE_FAMILIES, assert_applied, assert_rejected, attestation, evaluate, evidence, ids, latest, make_claim,
    make_record, reason_values, request, snapshot, verification,
)


def _world(b8, state, cls="CODE_BUILD_CLAIM", revision=5):
    claim = make_claim(b8, f"policy-{cls}", cls=cls)
    snap = snapshot(b8, [(claim, make_record(b8, claim, state))], slot_id=claim.slot_id, revision=revision)
    return claim, snap


def _run(b8, state, target, artifacts=(), *, cls="CODE_BUILD_CLAIM", refs=None, trusted=None, **kw):
    claim, snap = _world(b8, state, cls)
    refs = ids(*artifacts) if refs is None else refs
    req = request(b8, claim, latest(snap, claim), target, refs=refs, **kw)
    extra = {} if trusted is None else {"trusted": trusted}
    return claim, snap, evaluate(b8, snap, req, artifacts, **extra)


def test_section6_verifier_table_is_the_one_encoded(spec_text):
    sec = spec_text[spec_text.index("## 6. Claim classes"):spec_text.index("## 7. Human identity")]
    for cls, family in OBJECTIVE_FAMILIES.items():
        assert re.search(rf"^\| {cls} \| {family} \| false \|", sec, re.M), cls
    assert re.search(r"^\| HUMAN_DECLARATION \| HumanAttestation PRIMARY_DECLARATION \| true \|", sec, re.M)
    assert "one attestation never satisfies both" in sec


def test_closed_artifact_vocabularies(b8):
    assert tuple(v.value for v in b8.VerificationVerdict) == ("SATISFIED", "NOT_SATISFIED", "INCONCLUSIVE")
    assert tuple(k.value for k in b8.AttestationKind) == ("ATTESTATION", "REVIEW_AUTHORIZATION", "PRIMARY_DECLARATION")
    assert tuple(m.value for m in b8.StalenessMechanism) == ("NEVER_BY_TIME", "TTL", "SOURCE_VERSION_CHANGE",
                                                             "VALID_UNTIL", "CONDITION_TRIGGER", "DOMAIN_POLICY")


def test_artifact_identities_are_full_sha256_with_spec_prefixes(b8):
    claim = make_claim(b8, "ids")
    for obj, prefix in ((evidence(b8, claim), "b8ev_"), (verification(b8, claim), "b8ver_"),
                        (attestation(b8, claim), "b8att_")):
        assert re.fullmatch(prefix + r"[0-9a-f]{64}", obj.identity)
    assert re.fullmatch(r"b8claim_[0-9a-f]{64}", claim.claim_id)


# ---------------------------------------------------------------- T4 evidence

@pytest.mark.parametrize("frm", ["CANDIDATE", "HELD"])
def test_t4_valid_evidence_supports(b8, frm):
    claim, _ = _world(b8, frm)
    ev = evidence(b8, claim)
    claim, snap, result = _run(b8, frm, "SUPPORTED", [ev])
    assert_applied(b8, snap, result, claim, "SUPPORTED")


@pytest.mark.parametrize("frm", ["CANDIDATE", "HELD"])
def test_t4_without_evidence_is_evidence_inadmissible(b8, frm):
    claim, snap, result = _run(b8, frm, "SUPPORTED", [])
    assert_rejected(b8, snap, result, ["evidence_inadmissible"])


def test_t4_incomplete_provenance_is_evidence_inadmissible(b8):
    claim, _ = _world(b8, "CANDIDATE")
    claim, snap, result = _run(b8, "CANDIDATE", "SUPPORTED", [evidence(b8, claim, provenance=())])
    assert_rejected(b8, snap, result, ["evidence_inadmissible"])


@pytest.mark.parametrize("binding", [{"claim_version": 2}, {"claim_id": "b8claim_" + "9" * 64}])
def test_t4_wrongly_bound_evidence_is_ref_binding_mismatch_only(b8, binding):
    claim, _ = _world(b8, "CANDIDATE")
    claim, snap, result = _run(b8, "CANDIDATE", "SUPPORTED", [evidence(b8, claim, **binding)])
    assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


def test_t4_missing_reason_and_missing_evidence_are_two_facts(b8):
    claim, snap, result = _run(b8, "CANDIDATE", "SUPPORTED", [], reason="")
    assert_rejected(b8, snap, result, ["evidence_inadmissible", "reason_missing"])


def test_t4_confidence_is_never_a_sufficient_precondition(b8):
    claim, _ = _world(b8, "CANDIDATE")
    claim, snap, result = _run(b8, "CANDIDATE", "SUPPORTED", [evidence(b8, claim, provenance=(), confidence=0.999)])
    assert_rejected(b8, snap, result, ["evidence_inadmissible"])


# ---------------------------------------------------------------- T5 objective classes

@pytest.mark.parametrize("cls", sorted(OBJECTIVE_FAMILIES))
def test_t5_admissible_family_satisfied_verifies(b8, cls):
    claim, _ = _world(b8, "SUPPORTED", cls)
    vr = verification(b8, claim, family=OBJECTIVE_FAMILIES[cls])
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [vr], cls=cls)
    assert_applied(b8, snap, result, claim, "VERIFIED")


@pytest.mark.parametrize("cls", sorted(OBJECTIVE_FAMILIES))
def test_t5_wrong_family_is_verifier_inadmissible(b8, cls):
    claim, _ = _world(b8, "SUPPORTED", cls)
    wrong = next(f for c, f in sorted(OBJECTIVE_FAMILIES.items()) if c != cls)
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [verification(b8, claim, family=wrong)], cls=cls)
    assert_rejected(b8, snap, result, ["verifier_inadmissible"])


def test_t5_without_verification_record_is_verification_not_satisfied(b8):
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [])
    assert_rejected(b8, snap, result, ["verification_not_satisfied"])


@pytest.mark.parametrize("verdict", ["NOT_SATISFIED", "INCONCLUSIVE"])
def test_t5_unsatisfied_verdict_is_verification_not_satisfied(b8, verdict):
    claim, _ = _world(b8, "SUPPORTED")
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [verification(b8, claim, verdict=verdict)])
    assert_rejected(b8, snap, result, ["verification_not_satisfied"])


@pytest.mark.parametrize("binding", [{"claim_version": 2}, {"claim_id": "b8claim_" + "9" * 64}])
def test_t5_wrong_binding_is_ref_binding_mismatch_only(b8, binding):
    claim, _ = _world(b8, "SUPPORTED")
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [verification(b8, claim, **binding)])
    assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


def test_t5_a_valid_record_does_not_hide_a_wrongly_bound_ref(b8):
    claim, _ = _world(b8, "SUPPORTED")
    arts = [verification(b8, claim), verification(b8, claim, claim_version=2)]
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", arts)
    assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


def test_t5_unreferenced_artifact_is_not_bound(b8):
    claim, _ = _world(b8, "SUPPORTED")
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [verification(b8, claim)], refs=())
    assert_rejected(b8, snap, result, ["verification_not_satisfied"])


def test_t5_independent_binding_and_family_facts_both_reported(b8):
    claim, _ = _world(b8, "SUPPORTED")
    arts = [verification(b8, claim, claim_version=2), verification(b8, claim, family="FORMAL_PROOF_VERIFIER")]
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", arts)
    assert_rejected(b8, snap, result, ["ref_binding_mismatch", "verifier_inadmissible"])


def test_t5_stale_request_and_missing_verification_accumulate(b8):
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [], revision=4)
    assert_rejected(b8, snap, result, ["stale_request", "verification_not_satisfied"])


@pytest.mark.parametrize("kind", ["PRIMARY_DECLARATION", "REVIEW_AUTHORIZATION"])
def test_t5_human_attestation_never_verifies_an_objective_class(b8, kind):
    """HUMAN_APPROVAL != TRUTH (§6): on objective classes an attestation is an inadmissible verifier."""
    claim, _ = _world(b8, "SUPPORTED")
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [attestation(b8, claim, kind=kind)])
    assert "verifier_inadmissible" in assert_rejected(b8, snap, result)


# ---------------------------------------------------------------- T5 HUMAN_DECLARATION

H = "HUMAN_DECLARATION"


def test_t5_human_valid_primary_declaration_verifies(b8):
    claim, _ = _world(b8, "SUPPORTED", H)
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [attestation(b8, claim)], cls=H)
    assert_applied(b8, snap, result, claim, "VERIFIED")


def test_t5_human_missing_primary_declaration(b8):
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [], cls=H)
    assert_rejected(b8, snap, result, ["attestation_missing"])


def test_t5_human_review_authorization_alone_is_not_a_primary_declaration(b8):
    claim, _ = _world(b8, "SUPPORTED", H)
    att = attestation(b8, claim, kind="REVIEW_AUTHORIZATION")
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [att], cls=H)
    assert_rejected(b8, snap, result, ["attestation_missing"])


@pytest.mark.parametrize("identity", [{"identity_source": "display-name:Alice"}, {"auth_context_ref": ""}])
def test_t5_human_untrusted_identity_is_attestation_inadmissible(b8, identity):
    claim, _ = _world(b8, "SUPPORTED", H)
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [attestation(b8, claim, **identity)], cls=H)
    assert_rejected(b8, snap, result, ["attestation_inadmissible"])


def test_t5_human_attestation_is_inadmissible_until_an_identity_boundary_is_wired(b8):
    """§7: with no trusted identity boundary every attestation is inadmissible; the claim keeps its state."""
    claim, _ = _world(b8, "SUPPORTED", H)
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [attestation(b8, claim)], cls=H, trusted=frozenset())
    assert_rejected(b8, snap, result, ["attestation_inadmissible"])


def test_t5_human_wrongly_bound_declaration_is_ref_binding_mismatch(b8):
    claim, _ = _world(b8, "SUPPORTED", H)
    claim, snap, result = _run(b8, "SUPPORTED", "VERIFIED", [attestation(b8, claim, claim_version=2)], cls=H)
    assert_rejected(b8, snap, result, ["ref_binding_mismatch"])


# ---------------------------------------------------------------- T12 re-verification

def test_t12_fresh_satisfied_record_reverifies_stale_claim(b8):
    claim, _ = _world(b8, "STALE")
    claim, snap, result = _run(b8, "STALE", "VERIFIED", [verification(b8, claim)])
    after = assert_applied(b8, snap, result, claim, "VERIFIED")
    assert after.claim_version == claim.claim_version  # re-verification never changes the claim version


@pytest.mark.parametrize("case,expected", [
    ("none", ["verification_not_satisfied"]),
    ("not_satisfied", ["verification_not_satisfied"]),
    ("other_version", ["ref_binding_mismatch"]),
    ("wrong_family", ["verifier_inadmissible"]),
])
def test_t12_requires_satisfied_record_bound_to_same_claim_version(b8, case, expected):
    claim, _ = _world(b8, "STALE")
    arts = {"none": [], "not_satisfied": [verification(b8, claim, verdict="NOT_SATISFIED")],
            "other_version": [verification(b8, claim, claim_version=2)],
            "wrong_family": [verification(b8, claim, family="SOURCE_PROVENANCE_VERIFIER")]}[case]
    claim, snap, result = _run(b8, "STALE", "VERIFIED", arts)
    assert_rejected(b8, snap, result, expected)


def test_t12_then_promotion_still_requires_t6(b8):
    claim, _ = _world(b8, "STALE")
    claim, snap, result = _run(b8, "STALE", "VERIFIED", [verification(b8, claim)])
    assert latest(result.snapshot, claim).state is b8.ClaimState.VERIFIED  # not PROMOTED
    direct = _run(b8, "STALE", "PROMOTED", [verification(b8, claim)])
    assert reason_values(direct[2]) == ["forbidden_transition"]
