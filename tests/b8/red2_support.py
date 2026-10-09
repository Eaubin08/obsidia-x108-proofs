"""B8 RED tranche 2 — shared builders (test-only; spec §3, §4, §5.1, §6, §7, §9).

Tranche-2 API surface required by these tests (canonical spec names, §4 / §5.1 / §9.3):

- ``KnowledgeClaim(lineage_id, claim_version, previous_claim_id, claim_class, slot_id, valid_time, content,
  source_refs=(), origin_refs=())`` with derived ``claim_id`` (``b8claim_``);
- ``TemporalFrameRef(frame_id)``; ``ValidTimeInterval(temporal_frame_ref, start, end)`` — V1 half-open
  ``[start, end)``, ``None`` = unbounded (−∞ start / +∞ end); ``TEMPORALLY_INDETERMINATE`` sentinel;
  ``temporally_comparable`` / ``overlaps`` / ``contains``;
- ``EvidenceRef``, ``VerificationRecord`` (``VerificationVerdict``), ``HumanAttestation`` (``AttestationKind``),
  each with a derived full identity ``identity`` (``b8ev_`` / ``b8ver_`` / ``b8att_``); ``StalenessMechanism``;
- ``KnowledgeRecord`` gains ``supersedes`` / ``superseded_by`` / ``contested_by``; ``TransitionRequest`` gains
  ``supersedes_claim_id`` / ``supersedes_record_id`` (T9 only); ``SlotSnapshot`` gains ``claims``;
- ``evaluate_transition(snapshot, request, *, recorded_at, artifacts=(), trusted_identity_sources=frozenset())``
  stays the single gate; T9 returns ``TransitionResult.bundle`` (``SupersessionTransitionBundle``).

Representation choices (no doctrine added): request ``refs`` carry identities only; the referenced objects are
handed to the pure gate as ``artifacts`` and re-hashed (§9.1). The trusted identity boundary of §7 is injected
as ``trusted_identity_sources``; by default it is empty, so every attestation is inadmissible (§7). A claim whose
latest state is CONTESTED on the slot is the open contradiction of §8 / §9.2 T6. Staleness trigger evidence is
an EvidenceRef whose ``kind`` names the class mechanism (§6 closed set).
"""
from __future__ import annotations

from tests.b8.conftest import RECORDED_AT

FRAME_A = "frame:lab-a"
FRAME_B = "frame:lab-b"
TRUSTED_SOURCE = "idp:obsidia-test-boundary"
TRUSTED = frozenset({TRUSTED_SOURCE})
REVISION = 5
WRONG_RECORD_ID = "b8rec_" + "f" * 64
PREVIOUS_RECORD_ID = "b8rec_" + "0" * 64

# §6 table: admissible (objective) verifier family per class
OBJECTIVE_FAMILIES = {
    "FORMAL_CLAIM": "FORMAL_PROOF_VERIFIER",
    "CODE_BUILD_CLAIM": "TEST_BUILD_PROOF_VERIFIER",
    "PHYSICAL_CLAIM": "PROVENANCE_PLUS_REALITY_VERIFIER",
    "DOCUMENTARY_CLAIM": "SOURCE_PROVENANCE_VERIFIER",
}


def frame(b8, fid=FRAME_A):
    return b8.TemporalFrameRef(frame_id=fid)


def interval(b8, start, end, fid=FRAME_A):
    return b8.ValidTimeInterval(temporal_frame_ref=frame(b8, fid), start=start, end=end)


def slot_for(b8, cls, domain="domain:x"):
    return b8.knowledge_slot_id(cls, domain, ["subj:a"], [], "pred:p")


def make_claim(b8, lineage, *, cls="CODE_BUILD_CLAIM", start=0, end=100, fid=FRAME_A, domain="domain:x"):
    return b8.KnowledgeClaim(lineage_id=lineage, claim_version=1, previous_claim_id=None,
                             claim_class=b8.ClaimClass(cls), slot_id=slot_for(b8, cls, domain),
                             valid_time=interval(b8, start, end, fid), content={"lineage": lineage})


def make_record(b8, claim, state, *, rv=3, contested_by=(), refs=(), previous_record_id=None):
    prev = previous_record_id if previous_record_id is not None else (PREVIOUS_RECORD_ID if rv > 1 else None)
    return b8.KnowledgeRecord(claim_id=claim.claim_id, claim_version=claim.claim_version, record_version=rv,
                              state=b8.ClaimState(state), previous_record_id=prev,
                              contested_by=tuple(contested_by), refs=tuple(refs))


def snapshot(b8, entries, *, slot_id, revision=REVISION):
    """entries: (claim, record) pairs; a foreign-slot claim may be present as a referenced object."""
    return b8.SlotSnapshot(slot_id=slot_id, slot_revision=revision, records=tuple(r for _, r in entries),
                           applied_requests={}, claims=tuple(c for c, _ in entries))


def request(b8, claim, record, target, *, revision=REVISION, reason="explicit reason", refs=(), **overrides):
    fields = dict(claim_id=claim.claim_id, expected_claim_version=claim.claim_version,
                  expected_state=record.state, expected_record_version=record.record_version,
                  slot_id=claim.slot_id, expected_slot_revision=revision, target_state=b8.ClaimState(target),
                  refs=tuple(refs), requester_ref="requester:test", reason=reason)
    fields.update(overrides)
    return b8.TransitionRequest(**fields)


def evaluate(b8, snap, req, artifacts=(), *, trusted=TRUSTED, recorded_at=RECORDED_AT):
    if req.slot_id != snap.slot_id:
        from dataclasses import replace
        req = replace(req, slot_id=snap.slot_id)
    return b8.evaluate_transition(snap, req, recorded_at=recorded_at, artifacts=tuple(artifacts),
                                  trusted_identity_sources=trusted)


def evidence(b8, claim, *, kind="TEST_LOG", provenance=("prov:ci-run-1",), claim_id=None, claim_version=None,
             confidence=None, source_ref="src:ci"):
    return b8.EvidenceRef(kind=kind, source_ref=source_ref, content_digest="sha256:" + "e" * 64,
                          captured_at="2026-10-07T00:00:00Z", provenance_refs=tuple(provenance),
                          claim_id=claim_id or claim.claim_id,
                          claim_version=claim.claim_version if claim_version is None else claim_version,
                          confidence=confidence)


def verification(b8, claim, *, family="TEST_BUILD_PROOF_VERIFIER", verdict="SATISFIED", claim_id=None,
                 claim_version=None, basis_record_id=None):
    return b8.VerificationRecord(verifier_family=family, claim_id=claim_id or claim.claim_id,
                                 claim_version=claim.claim_version if claim_version is None else claim_version,
                                 verdict=b8.VerificationVerdict(verdict), evidence_refs=(),
                                 method_ref="method:pytest", produced_at="2026-10-07T00:00:00Z", basis_record_id=basis_record_id)


def attestation(b8, claim, *, kind="PRIMARY_DECLARATION", identity_source=TRUSTED_SOURCE,
                auth_context_ref="auth:session-1", claim_id=None, claim_version=None):
    return b8.HumanAttestation(attestation_id="att:1", actor_id="actor:human-1", identity_source=identity_source,
                               auth_context_ref=auth_context_ref, issued_at="2026-10-07T00:00:00Z",
                               claim_id=claim_id or claim.claim_id,
                               claim_version=claim.claim_version if claim_version is None else claim_version,
                               attestation_kind=b8.AttestationKind(kind), scope="claim")


def ids(*artifacts):
    return tuple(a.identity for a in artifacts)


def latest(snap, claim):
    """Current record = the unique record with maximal record_version (history is append-only)."""
    recs = [r for r in snap.records if r.claim_id == claim.claim_id]
    top = max(r.record_version for r in recs)
    (rec,) = {r for r in recs if r.record_version == top}   # ambiguous maximum fails here, no tie-break
    return rec


def reason_values(result):
    return [r.value for r in result.receipt.reasons]


def assert_rejected(b8, snap, result, expected=None):
    assert result.verdict is b8.TransitionVerdict.REJECTED
    assert result.receipt.verdict is b8.TransitionVerdict.REJECTED
    assert result.snapshot == snap and result.snapshot.slot_revision == snap.slot_revision
    got = reason_values(result)
    assert got, "REJECTED with an empty reason set"
    assert got == sorted(set(got)), "reasons must be unique and in code point order"
    if expected is not None:
        assert got == sorted(expected)
    return got


def assert_applied(b8, snap, result, claim, target):
    assert result.verdict is b8.TransitionVerdict.APPLIED, reason_values(result)
    assert result.receipt.verdict is b8.TransitionVerdict.APPLIED and tuple(result.receipt.reasons) == ()
    before, after = latest(snap, claim), latest(result.snapshot, claim)
    assert after.state is b8.ClaimState(target)
    assert after.record_version == before.record_version + 1 and after.claim_version == before.claim_version
    assert after.previous_record_id == before.record_id
    assert result.snapshot.slot_revision == snap.slot_revision + 1
    assert latest(snap, claim) == before  # input snapshot untouched
    return after
