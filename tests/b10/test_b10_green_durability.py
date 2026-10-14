from __future__ import annotations
import pytest
from tests.b10._harness import (
    SLOT_A,
    NOW,
    FRAME_ID,
    B10AuthorizationRef,
    B10DurableCommit,
)
from app.knowledge.b8.artifacts import KnowledgeClaim
from app.knowledge.b8.contracts import ClaimClass, ClaimState
from app.knowledge.b8.temporal import TemporalFrameRef, ValidTimeInterval
from app.knowledge.b8.core import KnowledgeRecord
from app.knowledge.b10.persistence import B10PersistenceAdapter

_FRAME = TemporalFrameRef(FRAME_ID)

DURABLE_REOPEN_PROOF = "YES"
SEPARATE_PROCESS_RESTART_PROOF = "NO"
OS_CRASH_RECOVERY_PROOF = "NO"


def _make_commit(auth_ref, slot_id=SLOT_A, slot_revision=1):
    claim = KnowledgeClaim(
        lineage_id="b10_durability_lineage",
        claim_version=1,
        previous_claim_id=None,
        claim_class=ClaimClass.FORMAL_CLAIM,
        slot_id=slot_id,
        valid_time=ValidTimeInterval(_FRAME, 0, None),
        content={"durability_test": "green"},
    )
    record = KnowledgeRecord(
        claim_id=claim.claim_id,
        claim_version=1,
        record_version=1,
        state=ClaimState.CANDIDATE,
        previous_record_id=None,
        refs=(),
        recorded_at=NOW,
    )
    artifact_ids = (record.record_id, claim.claim_id)
    return B10DurableCommit(
        slot_id=slot_id,
        slot_revision=slot_revision,
        artifact_ids=artifact_ids,
        authorization_ref=auth_ref,
        artifacts=(record, claim),
    )


def test_durability_genuine_reopen(tmp_path):
    db_path = str(tmp_path / "b10_durability.db")
    auth_ref = B10AuthorizationRef(
        authorization_id="b10_auth_durability_001",
        commit_ref="durability_commit_ref_001",
    )
    commit = _make_commit(auth_ref)

    adapter_a = B10PersistenceAdapter(db_path)
    receipt_a = adapter_a.execute_commit(commit)
    assert receipt_a.verdict == "DURABLE_SUCCESS", (
        f"adapter_a write failed: {receipt_a.failure_reason}"
    )
    written_commit_id = receipt_a.b10_commit_id
    written_artifact_ids = set(receipt_a.artifact_ids)
    del adapter_a

    adapter_b = B10PersistenceAdapter(db_path)
    for art_id in written_artifact_ids:
        assert adapter_b.artifact_exists(art_id), (
            f"artifact {art_id!r} not found after reopen"
        )

    entry = adapter_b.get_revision_entry(SLOT_A, 1)
    assert entry is not None, "slot revision entry absent after reopen"
    assert entry.b10_commit_id == written_commit_id
    assert set(entry.committed_artifact_ids) == written_artifact_ids

    history = list(adapter_b.get_slot_history(SLOT_A))
    assert len(history) == 1
    assert history[0].slot_revision == 1
