"""B10 durable memory test-side harness (test code only).

Constants, stub types, and contract loader.
NOT production code -- these types are for test input construction only.
"""
from __future__ import annotations
import hashlib
import importlib
import json
from dataclasses import dataclass
from typing import Optional

SLOT_A = "b10_test_slot_a"
SLOT_B = "b10_test_slot_b"
NOW = "2026-10-14T00:00:00Z"
FRAME_ID = "test_frame_b10"

RUNTIME_MODULE = "app.knowledge.b10.persistence"
ADAPTER_CLASS = "B10PersistenceAdapter"
ABSENT_MSG = (
    "B10_RUNTIME_NOT_IMPLEMENTED: "
    "app.knowledge.b10.persistence.B10PersistenceAdapter is absent "
    "(certified RED -- spec 83620fe8)"
)


def get_adapter():
    """Return production B10PersistenceAdapter or raise AssertionError (certified RED)."""
    try:
        mod = importlib.import_module(RUNTIME_MODULE)
        return getattr(mod, ADAPTER_CLASS)()
    except (ImportError, AttributeError):
        raise AssertionError(ABSENT_MSG)


# ---------------------------------------------------------------------------
# Test-side contract types (NOT production types)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class B10AuthorizationRef:
    """Authorization proof from KX108/Binder. (Spec s8.3)"""
    authorization_id: str
    commit_ref: str
    granted_by: str = "KX108_BINDER_STUB"


@dataclass(frozen=True)
class B10SlotRevisionEntry:
    """Per-slot durable revision record. (Spec s7.1)"""
    slot_id: str
    slot_revision: int
    committed_artifact_ids: tuple
    b10_commit_id: str
    recorded_at: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "committed_artifact_ids", tuple(self.committed_artifact_ids))


@dataclass(frozen=True)
class B10DurableCommit:
    """Backend-neutral persistence unit. (Spec s8.2)

    b10_commit_id is distinct from any single artifact_id. (NF-SPEC-1 preserved:
    ARTIFACT_LEVEL_IDEMPOTENCE_KEY=canonical artifact_id,
    COMMIT_LEVEL_IDEMPOTENCE_KEY=b10_commit_id -- distinct concepts.)
    """
    slot_id: str
    slot_revision: int
    artifact_ids: tuple
    authorization_ref: B10AuthorizationRef
    artifacts: tuple

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_ids", tuple(self.artifact_ids))
        object.__setattr__(self, "artifacts", tuple(self.artifacts))

    @property
    def b10_commit_id(self) -> str:
        """Deterministic from (slot_id, slot_revision, sorted artifact_ids).
        Distinct from individual artifact_ids per NF-SPEC-1.
        """
        body = json.dumps(
            {"slot_id": self.slot_id, "slot_revision": self.slot_revision,
             "artifact_ids": sorted(self.artifact_ids)},
            sort_keys=True,
        )
        return "b10commit_" + hashlib.sha256(body.encode()).hexdigest()[:24]


# ---------------------------------------------------------------------------
# Gap spec fixtures (SPEC_FIXTURE_NOT_RUNTIME_PRODUCED)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpecFixtureGapRecord:
    """Normative fixture derived from B8 KNOWLEDGE_PROMOTION_SPEC_V1 s8.1.
    CURRENT_B8_RUNTIME_PRODUCER=ABSENT (spec s24).
    """
    gap_id: str
    slot_id: str
    state: str
    gap_version: int
    reason: str
    recorded_at: Optional[str] = None
    FIXTURE_PROVENANCE: str = "SPEC_FIXTURE_NOT_RUNTIME_PRODUCED"

    @property
    def artifact_id(self) -> str:
        body = json.dumps(
            {"gap_id": self.gap_id, "gap_version": self.gap_version,
             "slot_id": self.slot_id, "state": self.state},
            sort_keys=True,
        )
        return "b8gap_" + hashlib.sha256(body.encode()).hexdigest()[:24]


@dataclass(frozen=True)
class SpecFixtureGapPartitionBundle:
    """Normative fixture for GapPartitionBundle (B8 spec s8.1 G4).
    CURRENT_B8_RUNTIME_PRODUCER=ABSENT (spec s24).
    Must be treated as an indivisible logical persistence unit by B10 (spec s11 / B10-I11).
    """
    bundle_id: str
    original_gap: SpecFixtureGapRecord
    residual_gap_records: tuple
    FIXTURE_PROVENANCE: str = "SPEC_FIXTURE_NOT_RUNTIME_PRODUCED"

    def __post_init__(self) -> None:
        object.__setattr__(self, "residual_gap_records", tuple(self.residual_gap_records))

    @property
    def all_constituent_artifact_ids(self) -> tuple:
        ids = [self.original_gap.artifact_id]
        ids.extend(g.artifact_id for g in self.residual_gap_records)
        return tuple(ids)


# ---------------------------------------------------------------------------
# Lazy adapter wrapper -- M33 pattern
# ---------------------------------------------------------------------------


class _LazyB10Adapter:
    """Defers production adapter import to test body.
    
    Pattern mirrors tests/m33/conftest.py: fixture setup always succeeds,
    first attribute access in test body calls get_adapter(), which raises
    AssertionError if runtime absent. AssertionError from test body = FAILED.
    """
    def __getattr__(self, name: str):
        return getattr(get_adapter(), name)
