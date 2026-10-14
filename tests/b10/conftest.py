from __future__ import annotations
import pytest
from app.knowledge.b8.core import (
    KnowledgeRecord,
    TransitionReceipt,
    SupersessionTransitionBundle,
)
from app.knowledge.b8.artifacts import KnowledgeClaim
from app.knowledge.b8.contracts import ClaimClass, ClaimState, TransitionVerdict
from app.knowledge.b8.temporal import TemporalFrameRef, ValidTimeInterval
from tests.b10._harness import (
    SLOT_A,
    SLOT_B,
    NOW,
    FRAME_ID,
    B10AuthorizationRef,
    B10DurableCommit,
    SpecFixtureGapRecord,
    SpecFixtureGapPartitionBundle,
)

_FRAME = TemporalFrameRef(FRAME_ID)


@pytest.fixture
def b10_adapter(tmp_path):
    from app.knowledge.b10.persistence import B10PersistenceAdapter
    return B10PersistenceAdapter(str(tmp_path / "b10_test.db"))


@pytest.fixture
def b10_auth_ref():
    return B10AuthorizationRef(
        authorization_id="b10_auth_stub_001",
        commit_ref="commit_ref_stub_001",
    )


@pytest.fixture
def b10_claim_a():
    return KnowledgeClaim(
        lineage_id="b10_test_lineage_a",
        claim_version=1,
        previous_claim_id=None,
        claim_class=ClaimClass.FORMAL_CLAIM,
        slot_id=SLOT_A,
        valid_time=ValidTimeInterval(_FRAME, 0, None),
        content={"b10_test": "claim_a"},
    )


@pytest.fixture
def b10_record_candidate(b10_claim_a):
    return KnowledgeRecord(
        claim_id=b10_claim_a.claim_id,
        claim_version=1,
        record_version=1,
        state=ClaimState.CANDIDATE,
        previous_record_id=None,
        refs=(),
        recorded_at=NOW,
    )


@pytest.fixture
def b10_single_record_commit(b10_claim_a, b10_record_candidate, b10_auth_ref):
    artifact_ids = (b10_record_candidate.record_id, b10_claim_a.claim_id)
    return B10DurableCommit(
        slot_id=SLOT_A,
        slot_revision=1,
        artifact_ids=artifact_ids,
        authorization_ref=b10_auth_ref,
        artifacts=(b10_record_candidate, b10_claim_a),
    )


@pytest.fixture
def b10_supersession_commit(b10_claim_a, b10_auth_ref):
    old_claim = b10_claim_a
    new_claim = KnowledgeClaim(
        lineage_id="b10_test_lineage_superseding",
        claim_version=1,
        previous_claim_id=None,
        claim_class=ClaimClass.FORMAL_CLAIM,
        slot_id=SLOT_A,
        valid_time=ValidTimeInterval(_FRAME, 0, None),
        content={"b10_test": "claim_superseding_a"},
    )
    old_from_rec = KnowledgeRecord(
        claim_id=old_claim.claim_id, claim_version=1, record_version=3,
        state=ClaimState.PROMOTED, previous_record_id=None, refs=(), recorded_at=NOW,
    )
    old_to_rec = KnowledgeRecord(
        claim_id=old_claim.claim_id, claim_version=1, record_version=4,
        state=ClaimState.SUPERSEDED, previous_record_id=old_from_rec.record_id,
        refs=(), recorded_at=NOW, superseded_by=new_claim.claim_id,
    )
    new_from_rec = KnowledgeRecord(
        claim_id=new_claim.claim_id, claim_version=1, record_version=2,
        state=ClaimState.VERIFIED, previous_record_id=None, refs=(), recorded_at=NOW,
    )
    new_to_rec = KnowledgeRecord(
        claim_id=new_claim.claim_id, claim_version=1, record_version=3,
        state=ClaimState.PROMOTED, previous_record_id=new_from_rec.record_id,
        refs=(), recorded_at=NOW, supersedes=old_claim.claim_id,
    )
    old_rcpt = TransitionReceipt(
        request_id="b8treq_stub_old_001",
        verdict=TransitionVerdict.APPLIED,
        claim_id=old_claim.claim_id, claim_version=1,
        from_state=ClaimState.PROMOTED, to_state=ClaimState.SUPERSEDED,
        from_record_version=3, to_record_version=4,
        from_record_id=old_from_rec.record_id, to_record_id=old_to_rec.record_id,
        reasons=(), gate_contract_version="B8_KNOWLEDGE_PROMOTION_SPEC_V1", recorded_at=NOW,
    )
    new_rcpt = TransitionReceipt(
        request_id="b8treq_stub_new_001",
        verdict=TransitionVerdict.APPLIED,
        claim_id=new_claim.claim_id, claim_version=1,
        from_state=ClaimState.VERIFIED, to_state=ClaimState.PROMOTED,
        from_record_version=2, to_record_version=3,
        from_record_id=new_from_rec.record_id, to_record_id=new_to_rec.record_id,
        reasons=(), gate_contract_version="B8_KNOWLEDGE_PROMOTION_SPEC_V1", recorded_at=NOW,
    )
    bundle = SupersessionTransitionBundle(
        request_id="b8treq_stub_t9_001",
        old_claim_id=old_claim.claim_id,
        old_from_record_id=old_from_rec.record_id,
        old_to_record_id=old_to_rec.record_id,
        new_claim_id=new_claim.claim_id,
        new_from_record_id=new_from_rec.record_id,
        new_to_record_id=new_to_rec.record_id,
        old_transition_receipt=old_rcpt,
        new_transition_receipt=new_rcpt,
        supersedes_link=(new_claim.claim_id, old_claim.claim_id),
        superseded_by_link=(old_claim.claim_id, new_claim.claim_id),
        recorded_at=NOW,
        gate_contract_version="B8_KNOWLEDGE_PROMOTION_SPEC_V1",
    )
    artifact_ids = (
        old_to_rec.record_id,
        new_to_rec.record_id,
        old_rcpt.receipt_id,
        new_rcpt.receipt_id,
        bundle.bundle_id,
        old_claim.claim_id,
        new_claim.claim_id,
    )
    return B10DurableCommit(
        slot_id=SLOT_A,
        slot_revision=5,
        artifact_ids=artifact_ids,
        authorization_ref=b10_auth_ref,
        artifacts=(old_to_rec, new_to_rec, old_rcpt, new_rcpt, bundle, old_claim, new_claim),
    )


@pytest.fixture
def gap_bundle_spec_fixture():
    original = SpecFixtureGapRecord(
        gap_id="b8gap_test_original_001",
        slot_id=SLOT_A,
        state="SUPERSEDED",
        gap_version=2,
        reason="PARTIAL_RESOLUTION",
        recorded_at=NOW,
    )
    residual_a = SpecFixtureGapRecord(
        gap_id="b8gap_test_residual_a_001",
        slot_id=SLOT_A,
        state="OPEN",
        gap_version=1,
        reason="GAP_REFRAMED_LEFT",
        recorded_at=NOW,
    )
    residual_b = SpecFixtureGapRecord(
        gap_id="b8gap_test_residual_b_001",
        slot_id=SLOT_A,
        state="OPEN",
        gap_version=1,
        reason="GAP_REFRAMED_RIGHT",
        recorded_at=NOW,
    )
    return SpecFixtureGapPartitionBundle(
        bundle_id="b8gpart_test_001",
        original_gap=original,
        residual_gap_records=(residual_a, residual_b),
    )
