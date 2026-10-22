"""Fixtures for the isolated Oxygen pilot bench (RED V0.2). Temporary storage only.

Without Docker or without the private exam file, tests are SKIPPED with an explicit HOLD
reason (never reported as passing)."""
from __future__ import annotations

import pytest

from app.knowledge.b8.artifacts import KnowledgeClaim
from app.knowledge.b8.contracts import ClaimClass, ClaimState
from app.knowledge.b8.core import KnowledgeRecord
from app.knowledge.b8.temporal import TemporalFrameRef, ValidTimeInterval
from tests.b10._harness import B10AuthorizationRef, B10DurableCommit
from tests.education_pilot import _bench as B

PILOT_SLOT = "pilot_force_sense_F4"
PILOT_NOW = "2026-10-17T00:00:00Z"


@pytest.fixture(scope="session")
def exams():
    if not B.exams_path().is_file():
        pytest.skip("HOLD_PRIVATE_EXAMS_MISSING: set OXYGEN_PILOT_EXAMS to the private exam file")
    return B.load_private_exams()


@pytest.fixture(scope="session")
def sandbox_ready():
    if not B.docker_ready():
        pytest.skip("HOLD_SECURITY_BOUNDARY: Docker isolation unavailable")
    B.kill_leftover_containers()
    yield True
    B.kill_leftover_containers()


@pytest.fixture
def new_student(sandbox_ready, tmp_path):
    """Factory: new_student(name, spec=None, extra=None, load=False) -> SandboxStudent."""
    created = []

    def make(name="student", spec=None, extra=None, load=False):
        s = B.SandboxStudent(tmp_path / f"state_{name}", spec=spec, extra=extra, load=load)
        created.append(s)
        return s

    yield make
    for s in created:
        s.close()


@pytest.fixture
def bench_b10(tmp_path):
    from app.knowledge.b10.persistence import B10PersistenceAdapter
    return B10PersistenceAdapter(str(tmp_path / "pilot_b10.db"))


@pytest.fixture
def bench_authorization():
    return B10AuthorizationRef(authorization_id="pilot_bench_auth_001", commit_ref="pilot_commit_001",
                               granted_by=B.BENCH_AUTHORIZATION_LABEL)


@pytest.fixture
def pilot_claim_and_record():
    claim = KnowledgeClaim(
        lineage_id="pilot_force_F4", claim_version=1, previous_claim_id=None,
        claim_class=ClaimClass.FORMAL_CLAIM, slot_id=PILOT_SLOT,
        valid_time=ValidTimeInterval(TemporalFrameRef("pilot_frame"), 0, None),
        content={"word": "force", "sense": "F4", "status": "CANDIDATE_LESSON"},
    )
    record = KnowledgeRecord(claim_id=claim.claim_id, claim_version=1, record_version=1,
                             state=ClaimState.CANDIDATE, previous_record_id=None, refs=(), recorded_at=PILOT_NOW)
    return claim, record


def make_commit(claim, record, authorization):
    return B10DurableCommit(slot_id=PILOT_SLOT, slot_revision=1, artifact_ids=(record.record_id, claim.claim_id),
                            authorization_ref=authorization, artifacts=(record, claim))
