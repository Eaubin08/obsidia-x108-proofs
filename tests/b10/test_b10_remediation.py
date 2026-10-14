"""B10 remediation targeted tests.
Targets: revision_mismatch, corrupted_read, serialization_failure.
"""
from __future__ import annotations
import sqlite3
import pytest
from tests.b10._harness import SLOT_A, SLOT_B, NOW, FRAME_ID, B10AuthorizationRef, B10DurableCommit
from app.knowledge.b8.core import KnowledgeRecord
from app.knowledge.b8.artifacts import KnowledgeClaim
from app.knowledge.b8.contracts import ClaimClass, ClaimState
from app.knowledge.b8.temporal import TemporalFrameRef, ValidTimeInterval
from app.knowledge.b10.persistence import B10PersistenceAdapter, _CorruptedReadError

_FRAME = TemporalFrameRef(FRAME_ID)

def _auth():
    return B10AuthorizationRef(authorization_id="remed_auth_001", commit_ref="remed_ref_001")

def _claim(lineage_id, slot_id=SLOT_A):
    return KnowledgeClaim(lineage_id=lineage_id, claim_version=1, previous_claim_id=None,
        claim_class=ClaimClass.FORMAL_CLAIM, slot_id=slot_id,
        valid_time=ValidTimeInterval(_FRAME, 0, None), content={"k": lineage_id})

def _rec(claim, rv=1):
    return KnowledgeRecord(claim_id=claim.claim_id, claim_version=1, record_version=rv,
        state=ClaimState.CANDIDATE, previous_record_id=None, refs=(), recorded_at=NOW)

def _commit(claim, record, rev, slot=SLOT_A):
    return B10DurableCommit(slot_id=slot, slot_revision=rev,
        artifact_ids=(record.record_id, claim.claim_id),
        authorization_ref=_auth(), artifacts=(record, claim))


def test_revision_mismatch_fails_closed(tmp_path):
    adapter = B10PersistenceAdapter(str(tmp_path / "rev.db"))
    c1 = _claim("remed_rev_a"); r1 = _rec(c1)
    receipt1 = adapter.execute_commit(_commit(c1, r1, 7))
    assert receipt1.verdict == "DURABLE_SUCCESS"

    c2 = _claim("remed_rev_b"); r2 = _rec(c2)
    receipt2 = adapter.execute_commit(_commit(c2, r2, 7))
    assert receipt2.verdict == "FAILED"
    assert receipt2.failure_reason == "revision_mismatch"

    entry = adapter.get_revision_entry(SLOT_A, 7)
    assert entry is not None
    commit1_id = _commit(c1, r1, 7).b10_commit_id
    assert entry.b10_commit_id == commit1_id
    assert adapter.artifact_exists(r1.record_id)
    assert not adapter.artifact_exists(r2.record_id)

def test_corrupted_read_detected(tmp_path):
    db_path = str(tmp_path / "corrupt.db")
    adapter = B10PersistenceAdapter(db_path)
    c = _claim("remed_corrupt"); r = _rec(c)
    receipt = adapter.execute_commit(_commit(c, r, 1))
    assert receipt.verdict == "DURABLE_SUCCESS"

    art_id = r.record_id
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE b10_artifacts SET payload_hash = ? WHERE artifact_id = ?",
        ("deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef", art_id))
    conn.commit(); conn.close()

    adapter2 = B10PersistenceAdapter(db_path)
    with pytest.raises(_CorruptedReadError):
        adapter2.get_artifact(art_id)

class _UnsupportedArtifact:
    def __init__(self, uid):
        self._uid = uid
    @property
    def record_id(self): return self._uid


def test_unsupported_serialization_fails_closed(tmp_path):
    adapter = B10PersistenceAdapter(str(tmp_path / "serial.db"))
    bad = _UnsupportedArtifact("bad_remed_001")
    commit = B10DurableCommit(slot_id=SLOT_A, slot_revision=1,
        artifact_ids=(bad.record_id,), authorization_ref=_auth(),
        artifacts=(bad,))
    receipt = adapter.execute_commit(commit)
    assert receipt.verdict == "FAILED"
    assert receipt.failure_reason == "serialization_failure"
    assert not adapter.artifact_exists(bad.record_id)
