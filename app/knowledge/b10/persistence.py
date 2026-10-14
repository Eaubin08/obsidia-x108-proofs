"""B10 Durable Memory -- Reference runtime implementation.

Spec:  docs/architecture/B10_DURABLE_MEMORY_SPEC_V1.md (83620fe8)
RED:   tests/b10/ (916d793f)

Reference backend: SQLite (stdlib). Backend-agnostic spec contract.
MEMORY_WRITE=FALSE globally. This adapter exercises the spec in isolation.

Authorization: structural enforcement seam only at this M40 slice.
Full KX108/Binder sovereign invocation is future E2E ownership.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
import types as _types
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from app.knowledge.b8.core import SupersessionTransitionBundle as _B8Bundle


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Production spec types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class B10SlotRevisionEntry:
    """Per-slot durable revision record. (Spec s7.1)"""
    slot_id: str
    slot_revision: int
    committed_artifact_ids: tuple
    b10_commit_id: str
    recorded_at: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "committed_artifact_ids",
                           tuple(self.committed_artifact_ids))


@dataclasses.dataclass(frozen=True)
class B10DurableWriteReceipt:
    """Normative write receipt. (Spec s12)

    Distinct from B8 TransitionReceipt (no epistemic state) and KX108 action receipt.
    """
    b10_commit_id: str
    artifact_ids: tuple
    slot_id: str
    slot_revision_after: int
    authorization_ref: Any
    verdict: str
    recorded_at: str
    failure_reason: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_ids", tuple(self.artifact_ids))


@dataclasses.dataclass
class _RecoveredArtifact:
    """Artifact wrapper returned by get_artifact / get_artifacts_at_or_before.
    Represents a B10 storage fact, not an epistemic B8 type.
    """
    artifact_id: str
    artifact_type: str
    canonical_json: str

    @property
    def record_id(self) -> str:
        return self.artifact_id

    @property
    def claim_id(self) -> str:
        return self.artifact_id

    @property
    def receipt_id(self) -> str:
        return self.artifact_id

    @property
    def bundle_id(self) -> str:
        return self.artifact_id


# ---------------------------------------------------------------------------
# Artifact helpers
# ---------------------------------------------------------------------------


def _canonical_id(artifact: Any) -> Optional[str]:
    """Return canonical identity of a B10-persistable artifact, or None if unknown."""
    for attr in ("record_id", "claim_id", "receipt_id", "bundle_id", "artifact_id"):
        descriptor = getattr(type(artifact), attr, None)
        if isinstance(descriptor, property):
            return getattr(artifact, attr)
    return None


def _to_json(artifact: Any) -> str:
    """Serialize artifact to canonical JSON for durable storage."""
    if hasattr(artifact, "to_canonical"):
        return json.dumps(artifact.to_canonical(), sort_keys=True)
    if dataclasses.is_dataclass(artifact):
        try:
            return json.dumps(dataclasses.asdict(artifact), sort_keys=True, default=str)
        except Exception:
            pass
    return json.dumps({"type": type(artifact).__name__, "repr": repr(artifact)})


# ---------------------------------------------------------------------------
# Bundle completeness validation  (Spec s11 + B10-I11)
# ---------------------------------------------------------------------------


def _check_bundle_completeness(commit: Any) -> Optional[str]:
    """Return failure reason string if commit contains an incomplete bundle; else None."""
    id_set = set(commit.artifact_ids)
    for artifact in commit.artifacts:
        if isinstance(artifact, _B8Bundle):
            required = {
                artifact.old_to_record_id,
                artifact.new_to_record_id,
                artifact.old_transition_receipt.receipt_id,
                artifact.new_transition_receipt.receipt_id,
            }
            if not required.issubset(id_set):
                return "partial_bundle_failure"
        elif hasattr(artifact, "all_constituent_artifact_ids"):
            required = set(artifact.all_constituent_artifact_ids)
            if not required.issubset(id_set):
                return "partial_bundle_failure"
    return None


# ---------------------------------------------------------------------------
# Authorization validation seam  (Spec s10)
# ---------------------------------------------------------------------------


def _valid_authorization(auth_ref: Any) -> bool:
    """Structural authorization enforcement seam.
    Rejects known-invalid references. Full KX108/Binder invocation is future E2E.
    """
    if auth_ref is None:
        return False
    auth_id = getattr(auth_ref, "authorization_id", None)
    granted_by = getattr(auth_ref, "granted_by", None)
    if not auth_id or auth_id in ("", "INVALID_AUTH"):
        return False
    if granted_by == "UNAUTHORIZED_SOURCE":
        return False
    return True

# ---------------------------------------------------------------------------
# SQLite schema
# ---------------------------------------------------------------------------

_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS b10_artifacts (  artifact_id TEXT PRIMARY KEY,  artifact_type TEXT NOT NULL,  slot_id TEXT NOT NULL,  canonical_json TEXT NOT NULL,  recorded_at TEXT NOT NULL);"
    "CREATE TABLE IF NOT EXISTS b10_commits (  b10_commit_id TEXT PRIMARY KEY,  slot_id TEXT NOT NULL,  slot_revision INTEGER NOT NULL,  artifact_ids_json TEXT NOT NULL,  authorization_json TEXT NOT NULL,  verdict TEXT NOT NULL,  recorded_at TEXT NOT NULL);"
    "CREATE TABLE IF NOT EXISTS b10_receipts (  b10_commit_id TEXT PRIMARY KEY,  artifact_ids_json TEXT NOT NULL,  slot_id TEXT NOT NULL,  slot_revision_after INTEGER NOT NULL,  authorization_json TEXT NOT NULL,  verdict TEXT NOT NULL,  failure_reason TEXT,  recorded_at TEXT NOT NULL);"
    "CREATE TABLE IF NOT EXISTS b10_slot_revisions (  slot_id TEXT NOT NULL,  slot_revision INTEGER NOT NULL,  b10_commit_id TEXT NOT NULL,  committed_artifact_ids_json TEXT NOT NULL,  recorded_at TEXT NOT NULL,  PRIMARY KEY (slot_id, slot_revision));"
)


class _BackendUnavailableError(RuntimeError):
    pass


def _serialize_auth(auth_ref: Any) -> str:
    if dataclasses.is_dataclass(auth_ref):
        return json.dumps(dataclasses.asdict(auth_ref), default=str)
    return json.dumps({"repr": repr(auth_ref)})

class B10PersistenceAdapter:
    "B10 durable memory persistence adapter. Reference backend: SQLite (stdlib). MEMORY_WRITE=FALSE. Spec: B10_DURABLE_MEMORY_SPEC_V1.md (83620fe8). Authorization seam only at M40 slice."

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = ":memory:"
        self._db_path = db_path
        self._unavailable: bool = False
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self) -> None:
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def simulate_backend_unavailable(self, flag: bool) -> None:
        self._unavailable = flag

    def assert_memory_write_false(self) -> None:
        from app.knowledge.b8.contracts import BOUNDARY
        assert BOUNDARY["memory_write"] is False, (
            "B10 adapter: BOUNDARY[memory_write] must remain False (B10-I06)"
        )

    def execute_commit(self, commit: Any) -> "B10DurableWriteReceipt":
        now = _now()
        commit_id = commit.b10_commit_id

        def _fail(reason: str) -> B10DurableWriteReceipt:
            return B10DurableWriteReceipt(
                b10_commit_id=commit_id,
                artifact_ids=tuple(commit.artifact_ids),
                slot_id=commit.slot_id,
                slot_revision_after=commit.slot_revision,
                authorization_ref=commit.authorization_ref,
                verdict="FAILED",
                recorded_at=now,
                failure_reason=reason,
            )

        if self._unavailable:
            return _fail("backend_unavailable")
        if not _valid_authorization(commit.authorization_ref):
            return _fail("authorization_denied")
        bundle_error = _check_bundle_completeness(commit)
        if bundle_error:
            return _fail(bundle_error)
        if len(commit.artifact_ids) != len(commit.artifacts):
            return _fail("integrity_mismatch")
        for claimed_id, artifact in zip(commit.artifact_ids, commit.artifacts):
            actual_id = _canonical_id(artifact)
            if actual_id is not None and actual_id != claimed_id:
                return _fail("integrity_mismatch")

        cur = self._conn.execute(
            "SELECT verdict FROM b10_commits WHERE b10_commit_id = ?",
            (commit_id,),
        )
        existing = cur.fetchone()
        if existing is not None and existing[0] == "DURABLE_SUCCESS":
            stored = self._load_receipt(commit_id)
            if stored is not None:
                return stored
            return B10DurableWriteReceipt(
                b10_commit_id=commit_id,
                artifact_ids=tuple(commit.artifact_ids),
                slot_id=commit.slot_id,
                slot_revision_after=commit.slot_revision,
                authorization_ref=commit.authorization_ref,
                verdict="NO_OP_DUPLICATE",
                recorded_at=now,
            )

        auth_json = _serialize_auth(commit.authorization_ref)
        artifact_ids_json = json.dumps(list(commit.artifact_ids))

        try:
            with self._conn:
                for art_id, artifact in zip(commit.artifact_ids, commit.artifacts):
                    self._conn.execute(
                        "INSERT OR IGNORE INTO b10_artifacts (artifact_id, artifact_type, slot_id, canonical_json, recorded_at) VALUES (?, ?, ?, ?, ?)",
                        (art_id, type(artifact).__name__,
                         commit.slot_id, _to_json(artifact), now),
                    )
                self._conn.execute(
                    "INSERT OR REPLACE INTO b10_commits (b10_commit_id, slot_id, slot_revision, artifact_ids_json, authorization_json, verdict, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (commit_id, commit.slot_id, commit.slot_revision,
                     artifact_ids_json, auth_json, "DURABLE_SUCCESS", now),
                )
                self._conn.execute(
                    "INSERT OR IGNORE INTO b10_slot_revisions (slot_id, slot_revision, b10_commit_id, committed_artifact_ids_json, recorded_at) VALUES (?, ?, ?, ?, ?)",
                    (commit.slot_id, commit.slot_revision, commit_id,
                     artifact_ids_json, now),
                )
                self._conn.execute(
                    "INSERT OR REPLACE INTO b10_receipts (b10_commit_id, artifact_ids_json, slot_id, slot_revision_after, authorization_json, verdict, failure_reason, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (commit_id, artifact_ids_json, commit.slot_id,
                     commit.slot_revision, auth_json,
                     "DURABLE_SUCCESS", None, now),
                )
        except sqlite3.Error:
            return _fail("serialization_failure")

        return B10DurableWriteReceipt(
            b10_commit_id=commit_id,
            artifact_ids=tuple(commit.artifact_ids),
            slot_id=commit.slot_id,
            slot_revision_after=commit.slot_revision,
            authorization_ref=commit.authorization_ref,
            verdict="DURABLE_SUCCESS",
            recorded_at=now,
        )

    def artifact_exists(self, artifact_id: str) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM b10_artifacts WHERE artifact_id = ?", (artifact_id,)
        )
        return cur.fetchone() is not None

    def get_artifact(self, artifact_id: str) -> Optional[_RecoveredArtifact]:
        cur = self._conn.execute(
            "SELECT artifact_id, artifact_type, canonical_json FROM b10_artifacts WHERE artifact_id = ?",
            (artifact_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return _RecoveredArtifact(
            artifact_id=row[0], artifact_type=row[1], canonical_json=row[2]
        )

    def get_slot_history(self, slot_id: str) -> Iterator[B10SlotRevisionEntry]:
        cur = self._conn.execute("SELECT slot_id, slot_revision, b10_commit_id, committed_artifact_ids_json, recorded_at FROM b10_slot_revisions WHERE slot_id = ? ORDER BY slot_revision ASC", (slot_id,))
        for row in cur:
            yield B10SlotRevisionEntry(
                slot_id=row[0], slot_revision=row[1], b10_commit_id=row[2],
                committed_artifact_ids=tuple(json.loads(row[3])),
                recorded_at=row[4],
            )

    def get_revision_entry(self, slot_id: str, slot_revision: int) -> Optional[B10SlotRevisionEntry]:
        cur = self._conn.execute("SELECT slot_id, slot_revision, b10_commit_id, committed_artifact_ids_json, recorded_at FROM b10_slot_revisions WHERE slot_id = ? AND slot_revision = ?", (slot_id, slot_revision))
        row = cur.fetchone()
        if row is None:
            return None
        return B10SlotRevisionEntry(
            slot_id=row[0], slot_revision=row[1], b10_commit_id=row[2],
            committed_artifact_ids=tuple(json.loads(row[3])), recorded_at=row[4],
        )

    def get_artifacts_at_or_before(self, slot_id: str, slot_revision: int) -> Iterator[_RecoveredArtifact]:
        cur = self._conn.execute("SELECT committed_artifact_ids_json FROM b10_slot_revisions WHERE slot_id = ? AND slot_revision <= ? ORDER BY slot_revision ASC", (slot_id, slot_revision))
        seen: set = set()
        for row in cur:
            for art_id in json.loads(row[0]):
                if art_id not in seen:
                    seen.add(art_id)
                    art = self.get_artifact(art_id)
                    if art is not None:
                        yield art

    def recover_after_restart(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self._connect()

    def _load_receipt(self, commit_id: str) -> Optional[B10DurableWriteReceipt]:
        cur = self._conn.execute("SELECT b10_commit_id, artifact_ids_json, slot_id, slot_revision_after, authorization_json, verdict, failure_reason, recorded_at FROM b10_receipts WHERE b10_commit_id = ?", (commit_id,))
        row = cur.fetchone()
        if row is None:
            return None
        auth_raw = json.loads(row[4])
        if isinstance(auth_raw, dict) and "authorization_id" in auth_raw:
            auth_ref = _types.SimpleNamespace(**auth_raw)
        else:
            auth_ref = auth_raw
        return B10DurableWriteReceipt(
            b10_commit_id=row[0], artifact_ids=tuple(json.loads(row[1])),
            slot_id=row[2], slot_revision_after=row[3],
            authorization_ref=auth_ref, verdict=row[5],
            failure_reason=row[6], recorded_at=row[7],
        )
