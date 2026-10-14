"""B10 Durable Memory RED contract tests.

Tests express the B10 contract as defined in:
  docs/architecture/B10_DURABLE_MEMORY_SPEC_V1.md  (commit 83620fe8)
  docs/architecture/M40_B10_DURABLE_MEMORY_DOCTRINE_V1.md (commit 5a6a2acd)

RED phase: tests collect and fail because app.knowledge.b10 is not yet implemented.
GREEN phase: same tests pass when runtime is implemented.

Traceability: RED-01 through RED-17 (spec s30).

NF-SPEC-1 NOTE:
  ARTIFACT_LEVEL_IDEMPOTENCE_KEY = canonical artifact_id  (per-artifact dedup)
  COMMIT_LEVEL_IDEMPOTENCE_KEY   = b10_commit_id          (per-commit dedup)
  These are DISTINCT. Both are required. (NF-SPEC-1, nonblocking finding, spec cert.)
"""
from __future__ import annotations
import pytest
from app.knowledge.b8.contracts import BOUNDARY as B8_BOUNDARY
from tests.b10._harness import (
    SLOT_A,
    SLOT_B,
    NOW,
    FRAME_ID,
    get_adapter,
    B10AuthorizationRef,
    B10DurableCommit,
    SpecFixtureGapPartitionBundle,
    _LazyB10Adapter,
)

# ---------------------------------------------------------------------------
# Traceability registry
# ---------------------------------------------------------------------------

_RED_REGISTRY: dict = {}


def _red(red_id: str):
    def decorator(fn):
        _RED_REGISTRY[red_id] = fn.__name__
        return fn
    return decorator


# ---------------------------------------------------------------------------
# RED-01 -- RED-06
# ---------------------------------------------------------------------------


@_red("RED-01")
def test_red_01_single_artifact_durable_persistence(b10_adapter, b10_single_record_commit):
    """RED-01: Authorized B10DurableCommit makes a KnowledgeRecord durable. (Spec s6)"""
    result = b10_adapter.execute_commit(b10_single_record_commit)
    assert result is not None, "execute_commit must return a B10DurableWriteReceipt"
    assert result.verdict == "DURABLE_SUCCESS", (
        f"Expected DURABLE_SUCCESS, got {result.verdict!r}"
    )
    for art_id in b10_single_record_commit.artifact_ids:
        assert b10_adapter.artifact_exists(art_id), (
            f"Artifact {art_id!r} must be retrievable after durable commit"
        )


@_red("RED-02")
def test_red_02_canonical_id_round_trip(
    b10_adapter, b10_single_record_commit, b10_record_candidate
):
    """RED-02: Canonical artifact identity survives encode-persist-recover. (Spec s18)"""
    original_id = b10_record_candidate.record_id
    b10_adapter.execute_commit(b10_single_record_commit)
    recovered = b10_adapter.get_artifact(original_id)
    assert recovered is not None, "Artifact must be recoverable by canonical ID"
    assert recovered.record_id == original_id, (
        f"Recovered ID {recovered.record_id!r} must equal original {original_id!r}"
    )


@_red("RED-03")
def test_red_03_slot_revision_survives_restart(b10_adapter, b10_single_record_commit):
    """RED-03: B10SlotRevisionEntry survives process restart. (Spec s7.1 + B10-I09)"""
    commit = b10_single_record_commit
    b10_adapter.execute_commit(commit)
    b10_adapter.recover_after_restart()
    entry = b10_adapter.get_revision_entry(commit.slot_id, commit.slot_revision)
    assert entry is not None, (
        f"B10SlotRevisionEntry for slot={commit.slot_id!r} "
        f"rev={commit.slot_revision} must survive restart"
    )
    assert entry.slot_revision == commit.slot_revision
    assert set(entry.committed_artifact_ids) == set(commit.artifact_ids), (
        "committed_artifact_ids must exactly match committed artifacts"
    )


@_red("RED-04")
def test_red_04_per_slot_ordered_history(b10_adapter, b10_claim_a, b10_auth_ref):
    """RED-04: Per-slot history ordered by slot_revision ascending. (Spec s19 + B10-I10)"""
    from app.knowledge.b8.core import KnowledgeRecord
    from app.knowledge.b8.contracts import ClaimState

    records = []
    for rev in range(1, 4):
        rec = KnowledgeRecord(
            claim_id=b10_claim_a.claim_id, claim_version=1, record_version=rev,
            state=ClaimState.CANDIDATE,
            previous_record_id=records[-1].record_id if records else None,
            refs=(), recorded_at=NOW,
        )
        records.append(rec)
        commit = B10DurableCommit(
            slot_id=SLOT_A, slot_revision=rev,
            artifact_ids=(rec.record_id, b10_claim_a.claim_id),
            authorization_ref=b10_auth_ref,
            artifacts=(rec, b10_claim_a),
        )
        b10_adapter.execute_commit(commit)

    revisions = [
        b10_adapter.get_revision_entry(SLOT_A, rev).slot_revision
        for rev in range(1, 4)
        if b10_adapter.get_revision_entry(SLOT_A, rev) is not None
    ]
    assert revisions == sorted(revisions), (
        f"Slot revisions must be ascending: {revisions}"
    )
    assert len(revisions) == 3, "All 3 slot revision entries must exist"


@_red("RED-05")
def test_red_05_supersession_bundle_atomicity(b10_adapter, b10_supersession_commit):
    """RED-05: SupersessionTransitionBundle persists atomically. (Spec s11 + B10-I11)"""
    commit = b10_supersession_commit
    result = b10_adapter.execute_commit(commit)
    if result.verdict == "DURABLE_SUCCESS":
        for art_id in commit.artifact_ids:
            assert b10_adapter.artifact_exists(art_id), (
                f"Bundle artifact {art_id!r} missing after DURABLE_SUCCESS -- "
                "partial bundle success is forbidden"
            )
    else:
        for art_id in commit.artifact_ids:
            assert not b10_adapter.artifact_exists(art_id), (
                f"After FAILED bundle, artifact {art_id!r} must not be durably visible"
            )


@_red("RED-06")
def test_red_06_gap_bundle_contract_compatibility(
    b10_adapter, b10_auth_ref, gap_bundle_spec_fixture
):
    """RED-06: GapPartitionBundle treated as indivisible persistence unit. (Spec s11/s24)
    SPEC_FIXTURE_NOT_RUNTIME_PRODUCED: no live B8 runtime producer for gap artifacts.
    """
    assert gap_bundle_spec_fixture.FIXTURE_PROVENANCE == "SPEC_FIXTURE_NOT_RUNTIME_PRODUCED"
    bundle = gap_bundle_spec_fixture
    artifact_ids = bundle.all_constituent_artifact_ids
    commit = B10DurableCommit(
        slot_id=bundle.original_gap.slot_id,
        slot_revision=3,
        artifact_ids=artifact_ids,
        authorization_ref=b10_auth_ref,
        artifacts=tuple([bundle.original_gap] + list(bundle.residual_gap_records)),
    )
    result = b10_adapter.execute_commit(commit)
    if result.verdict == "DURABLE_SUCCESS":
        for art_id in artifact_ids:
            assert b10_adapter.artifact_exists(art_id), (
                f"GapPartitionBundle artifact {art_id!r} missing after DURABLE_SUCCESS"
            )
    else:
        for art_id in artifact_ids:
            assert not b10_adapter.artifact_exists(art_id), (
                f"After FAILED gap bundle, artifact {art_id!r} must not be partially visible"
            )


# ---------------------------------------------------------------------------
# RED-07 -- RED-12
# ---------------------------------------------------------------------------


@_red("RED-07")
def test_red_07_identical_commit_idempotence(b10_adapter, b10_single_record_commit):
    """RED-07: Identical duplicate commit yields NO_OP_DUPLICATE or equivalent. (Spec s14 + B10-I12)

    NF-SPEC-1 preserved:
      ARTIFACT_LEVEL_IDEMPOTENCE_KEY = canonical artifact_id   (per-artifact dedup)
      COMMIT_LEVEL_IDEMPOTENCE_KEY   = b10_commit_id           (per-commit dedup)
    Both mechanisms are distinct and required.
    """
    commit = b10_single_record_commit
    result1 = b10_adapter.execute_commit(commit)
    assert result1.verdict == "DURABLE_SUCCESS"
    count_after_first = len(list(b10_adapter.get_slot_history(commit.slot_id)))

    result2 = b10_adapter.execute_commit(commit)  # same b10_commit_id
    assert result2.verdict in ("DURABLE_SUCCESS", "NO_OP_DUPLICATE"), (
        f"Duplicate commit must yield DURABLE_SUCCESS or NO_OP_DUPLICATE; got {result2.verdict!r}"
    )
    count_after_second = len(list(b10_adapter.get_slot_history(commit.slot_id)))
    assert count_after_second == count_after_first, (
        "Duplicate commit must not create a second semantic history entry"
    )


@_red("RED-08")
def test_red_08_conflicting_payload_fails_closed(
    b10_adapter, b10_claim_a, b10_auth_ref, b10_single_record_commit
):
    """RED-08: Commit with artifact_ids that conflict with artifact content fails closed.
    (Spec s14: integrity_mismatch -- canonical ID is a hash; mismatch = corruption)
    """
    from app.knowledge.b8.core import KnowledgeRecord
    from app.knowledge.b8.contracts import ClaimState

    result1 = b10_adapter.execute_commit(b10_single_record_commit)
    assert result1.verdict == "DURABLE_SUCCESS"

    # Different artifact content but claiming the original artifact IDs (ID/content mismatch)
    different_rec = KnowledgeRecord(
        claim_id=b10_claim_a.claim_id, claim_version=1,
        record_version=99,  # different version -> different canonical hash
        state=ClaimState.CANDIDATE, previous_record_id=None, refs=(), recorded_at=NOW,
    )
    conflicting_commit = B10DurableCommit(
        slot_id=SLOT_A,
        slot_revision=2,
        artifact_ids=b10_single_record_commit.artifact_ids,  # claim original IDs
        authorization_ref=b10_auth_ref,
        artifacts=(different_rec, b10_claim_a),  # but content hashes to different IDs
    )
    result2 = b10_adapter.execute_commit(conflicting_commit)
    assert result2.verdict == "FAILED", (
        f"ID/content mismatch must FAIL CLOSED; got {result2.verdict!r}"
    )


@_red("RED-09")
def test_red_09_unauthorized_commit_cannot_execute(b10_adapter, b10_single_record_commit):
    """RED-09: Commit without valid KX108/Binder authorization must not execute.
    (Spec s10: WRITE_AUTHORIZATION_BOUNDARY=BINDER_KX108)
    """
    unauthorized_commit = B10DurableCommit(
        slot_id=SLOT_A,
        slot_revision=99,
        artifact_ids=b10_single_record_commit.artifact_ids,
        authorization_ref=B10AuthorizationRef(
            authorization_id="INVALID_AUTH",
            commit_ref="INVALID_REF",
            granted_by="UNAUTHORIZED_SOURCE",
        ),
        artifacts=b10_single_record_commit.artifacts,
    )
    result = b10_adapter.execute_commit(unauthorized_commit)
    assert result.verdict == "FAILED", (
        f"Unauthorized commit must FAIL; got {result.verdict!r}"
    )
    for art_id in unauthorized_commit.artifact_ids:
        assert not b10_adapter.artifact_exists(art_id), (
            f"Unauthorized commit must not durably write artifact {art_id!r}"
        )


@_red("RED-10")
def test_red_10_partial_bundle_cannot_succeed(
    b10_adapter, b10_auth_ref, b10_supersession_commit
):
    """RED-10: Partial bundle must not report DURABLE_SUCCESS. (Spec s11 + B10-I11)
    PARTIAL_DURABLE_VISIBILITY_OF_BUNDLE=FORBIDDEN.
    """
    from app.knowledge.b8.core import SupersessionTransitionBundle as B8Bundle

    full_commit = b10_supersession_commit
    bundle_artifact = next(
        (a for a in full_commit.artifacts if isinstance(a, B8Bundle)), None
    )
    assert bundle_artifact is not None, "Fixture must contain a SupersessionTransitionBundle"

    # Commit the bundle artifact alone, without its constituent records/receipts
    partial_commit = B10DurableCommit(
        slot_id=full_commit.slot_id,
        slot_revision=full_commit.slot_revision + 100,
        artifact_ids=(bundle_artifact.bundle_id,),
        authorization_ref=b10_auth_ref,
        artifacts=(bundle_artifact,),
    )
    result = b10_adapter.execute_commit(partial_commit)
    assert result.verdict == "FAILED", (
        f"Bundle commit missing constituent artifacts must FAIL; got {result.verdict!r}"
    )


@_red("RED-11")
def test_red_11_backend_unavailable_does_not_fabricate(b10_adapter, b10_single_record_commit):
    """RED-11: Backend unavailable returns normalized failure, not fabricated success.
    (Spec s15 + B10-I13: failure cannot fabricate success receipt)
    """
    b10_adapter.simulate_backend_unavailable(True)
    try:
        result = b10_adapter.execute_commit(b10_single_record_commit)
        assert result.verdict == "FAILED", (
            f"Backend unavailable must return FAILED; got {result.verdict!r}"
        )
        for art_id in b10_single_record_commit.artifact_ids:
            assert not b10_adapter.artifact_exists(art_id), (
                f"Backend unavailable must not create durable artifact {art_id!r}"
            )
    finally:
        b10_adapter.simulate_backend_unavailable(False)


@_red("RED-12")
def test_red_12_receipt_fields_and_type_distinctness(b10_adapter, b10_single_record_commit):
    """RED-12: Successful receipt has correct fields and is distinct from B8 TransitionReceipt.
    (Spec s12: B10DurableWriteReceipt minimum field set)
    """
    from app.knowledge.b8.core import TransitionReceipt as B8Receipt

    commit = b10_single_record_commit
    result = b10_adapter.execute_commit(commit)
    assert result.verdict == "DURABLE_SUCCESS"

    assert result.b10_commit_id == commit.b10_commit_id
    assert set(result.artifact_ids) == set(commit.artifact_ids)
    assert result.slot_id == commit.slot_id
    assert result.slot_revision_after == commit.slot_revision
    assert result.authorization_ref == commit.authorization_ref
    assert not isinstance(result, B8Receipt), (
        "B10DurableWriteReceipt must be a distinct type from B8 TransitionReceipt"
    )


# ---------------------------------------------------------------------------
# RED-13 -- RED-17 + traceability meta-test
# ---------------------------------------------------------------------------


@_red("RED-13")
def test_red_13_no_global_revision(b10_adapter, b10_claim_a, b10_auth_ref):
    """RED-13: No global revision semantics exposed by adapter. (Spec s19 + B10-I10)
    Revision 4 of slot A and revision 4 of slot B do NOT share a global position.
    """
    from app.knowledge.b8.core import KnowledgeRecord
    from app.knowledge.b8.contracts import ClaimState
    from app.knowledge.b8.artifacts import KnowledgeClaim
    from app.knowledge.b8.temporal import TemporalFrameRef, ValidTimeInterval

    frame = TemporalFrameRef(FRAME_ID)
    claim_b = KnowledgeClaim(
        lineage_id="b10_test_lineage_slot_b_red13",
        claim_version=1,
        previous_claim_id=None,
        claim_class=b10_claim_a.claim_class,
        slot_id=SLOT_B,
        valid_time=ValidTimeInterval(frame, 0, None),
        content={"b10_test": "claim_slot_b_red13"},
    )
    TARGET_REV = 4
    rec_a = KnowledgeRecord(
        claim_id=b10_claim_a.claim_id, claim_version=1, record_version=1,
        state=ClaimState.CANDIDATE, previous_record_id=None, refs=(), recorded_at=NOW,
    )
    rec_b = KnowledgeRecord(
        claim_id=claim_b.claim_id, claim_version=1, record_version=1,
        state=ClaimState.CANDIDATE, previous_record_id=None, refs=(), recorded_at=NOW,
    )
    b10_adapter.execute_commit(B10DurableCommit(
        slot_id=SLOT_A, slot_revision=TARGET_REV,
        artifact_ids=(rec_a.record_id, b10_claim_a.claim_id),
        authorization_ref=b10_auth_ref, artifacts=(rec_a, b10_claim_a),
    ))
    b10_adapter.execute_commit(B10DurableCommit(
        slot_id=SLOT_B, slot_revision=TARGET_REV,
        artifact_ids=(rec_b.record_id, claim_b.claim_id),
        authorization_ref=b10_auth_ref, artifacts=(rec_b, claim_b),
    ))
    entry_a = b10_adapter.get_revision_entry(SLOT_A, TARGET_REV)
    entry_b = b10_adapter.get_revision_entry(SLOT_B, TARGET_REV)
    assert entry_a is not None and entry_b is not None
    assert entry_a.slot_id != entry_b.slot_id
    assert entry_a.slot_revision == entry_b.slot_revision == TARGET_REV
    assert not hasattr(b10_adapter, "global_revision"), (
        "B10PersistenceAdapter must not expose global_revision"
    )
    assert not hasattr(b10_adapter, "get_global_revision"), (
        "B10PersistenceAdapter must not expose get_global_revision()"
    )


@_red("RED-14")
def test_red_14_native_memory_remains_unselected(b10_adapter):
    """RED-14: B10 V1 must not select Native Memory as canonical write backend.
    (Spec s25 + doctrine s9: NATIVE_MEMORY_IS_CANONICAL_B10_BACKEND=NO)
    """
    assert not hasattr(b10_adapter, "native_memory_write"), (
        "B10PersistenceAdapter must not expose native_memory_write"
    )
    if hasattr(b10_adapter, "backend_id"):
        assert b10_adapter.backend_id != "native_memory", (
            "backend_id must not be native_memory"
        )


@_red("RED-15")
def test_red_15_graphiti_neo4j_remain_inactive(b10_adapter):
    """RED-15: B10 must not activate Graphiti or Neo4j. (Spec s25)
    GRAPHITI_RUNTIME_CALLS=0, NEO4J_RUNTIME_CALLS=0.
    """
    import sys
    module_name = type(b10_adapter).__module__
    assert "graphiti" not in module_name, (
        f"B10PersistenceAdapter module must not reference graphiti; got {module_name!r}"
    )
    assert "neo4j" not in module_name, (
        f"B10PersistenceAdapter module must not reference neo4j; got {module_name!r}"
    )
    assert not hasattr(b10_adapter, "graphiti_client"), (
        "B10PersistenceAdapter must not expose graphiti_client"
    )
    assert not hasattr(b10_adapter, "neo4j_driver"), (
        "B10PersistenceAdapter must not expose neo4j_driver"
    )


@_red("RED-16")
def test_red_16_memory_write_lock():
    """RED-16: memory_write stays False; execution denied without explicit unlock.
    (Spec s21 + B10-I06: MEMORY_WRITE=FALSE)
    Step 1 (always): B8 BOUNDARY invariant.
    Step 2 (RED until runtime): adapter-level enforcement.
    """
    # Step 1: always-true invariant (runs even during RED phase)
    assert B8_BOUNDARY["memory_write"] is False, (
        "B8 BOUNDARY memory_write must remain False (B10-I06)"
    )
    # Step 2: adapter-level enforcement (AssertionError from test body = FAILED, M33 pattern)
    adapter = _LazyB10Adapter()
    adapter.assert_memory_write_false()  # raises AssertionError if runtime absent


@_red("RED-17")
def test_red_17_m39_sufficient_recovery_facts(b10_adapter, b10_claim_a, b10_auth_ref):
    """RED-17: B10 exposes storage facts sufficient for future M39.
    (Spec s7.2 + B10-I17: B10 supplies facts, M39 owns interpretation)
    B10 must NOT expose get_knowledge_state_as_of_revision() -- that belongs to M39.
    """
    from app.knowledge.b8.core import KnowledgeRecord
    from app.knowledge.b8.contracts import ClaimState

    records = []
    for rev in range(1, 4):
        rec = KnowledgeRecord(
            claim_id=b10_claim_a.claim_id, claim_version=1, record_version=rev,
            state=ClaimState.CANDIDATE,
            previous_record_id=records[-1].record_id if records else None,
            refs=(), recorded_at=NOW,
        )
        records.append(rec)
        b10_adapter.execute_commit(B10DurableCommit(
            slot_id=SLOT_A, slot_revision=rev,
            artifact_ids=(rec.record_id, b10_claim_a.claim_id),
            authorization_ref=b10_auth_ref,
            artifacts=(rec, b10_claim_a),
        ))

    TARGET_R = 2
    history = list(b10_adapter.get_slot_history(SLOT_A))
    assert len(history) >= len(records), "get_slot_history must return complete history"

    entry = b10_adapter.get_revision_entry(SLOT_A, TARGET_R)
    assert entry is not None, f"B10SlotRevisionEntry for rev={TARGET_R} must exist"
    assert entry.slot_revision == TARGET_R

    artifacts_through_r = list(b10_adapter.get_artifacts_at_or_before(SLOT_A, TARGET_R))
    assert len(artifacts_through_r) > 0, (
        f"get_artifacts_at_or_before(slot={SLOT_A!r}, R={TARGET_R}) must return artifacts"
    )
    assert not hasattr(b10_adapter, "get_knowledge_state_as_of_revision"), (
        "B10PersistenceAdapter must NOT expose get_knowledge_state_as_of_revision() -- "
        "that semantic interpretation belongs to M39"
    )


# ---------------------------------------------------------------------------
# Traceability meta-test
# ---------------------------------------------------------------------------


def test_red_traceability_complete():
    """Meta-test: verify exactly RED-01 through RED-17 are registered. No gaps, no extras."""
    expected = {f"RED-{i:02d}" for i in range(1, 18)}
    actual = set(_RED_REGISTRY.keys())
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"Missing RED requirements: {sorted(missing)}"
    assert not extra, f"Unexpected extra RED IDs: {sorted(extra)}"
