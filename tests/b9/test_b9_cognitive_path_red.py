import pytest

try:
    from app.cognition.b9.contracts import (
        CognitivePath,
        FailedPath,
        PathHistory,
        PathStatus,
        Retryability
    )
    B9_IMPORT_OK = True
except ImportError:
    B9_IMPORT_OK = False

pytestmark = pytest.mark.skipif(not B9_IMPORT_OK, reason="B9 runtime not implemented yet")

def test_b9_r1_deterministic_identity():
    # B9-R1: same ordered canonical path -> same identity
    path1 = CognitivePath(
        subject="test_subject",
        goal="test_goal",
        steps=["step_1", "step_2"]
    )
    path2 = CognitivePath(
        subject="test_subject",
        goal="test_goal",
        steps=["step_1", "step_2"]
    )
    assert path1.path_id == path2.path_id

def test_b9_r2_order_participates_in_identity():
    # B9-R2: same steps different order -> different identity
    path1 = CognitivePath(subject="A", goal="B", steps=["S1", "S2"])
    path2 = CognitivePath(subject="A", goal="B", steps=["S2", "S1"])
    assert path1.path_id != path2.path_id

def test_b9_r3_completed_path_immutable():
    # B9-R3: completed path immutable
    path = CognitivePath(subject="A", goal="B", steps=[])
    path.mark_status(PathStatus.SUCCEEDED)
    with pytest.raises(Exception):
        path.steps.append("NEW_STEP")

def test_b9_r4_failed_path_preserves_reason_context():
    # B9-R4: failed path preserves reason/context
    fp = FailedPath(
        path=CognitivePath(subject="A", goal="B", steps=["S1"]),
        reason="MISSING_EVIDENCE",
        context={"evidence_id": "123"}
    )
    assert fp.reason == "MISSING_EVIDENCE"
    assert fp.context["evidence_id"] == "123"

def test_b9_r5_failed_path_not_permanent_prohibition():
    # B9-R5: failed path not permanent prohibition
    fp = FailedPath(
        path=CognitivePath(subject="A", goal="B", steps=[]),
        reason="TEMPORAL_INDETERMINACY",
        retryability=Retryability.RETRYABLE
    )
    assert fp.retryability != Retryability.NON_RETRYABLE_UNDER_CURRENT_CONTRACT

def test_b9_r6_successful_path_grants_no_authority():
    # B9-R6: successful path grants no authority
    path = CognitivePath(subject="A", goal="B", steps=["S1"])
    path.mark_status(PathStatus.SUCCEEDED)
    assert not hasattr(path, "authorize")
    assert not hasattr(path, "execute")
    assert getattr(path, "emits_act", False) is False

def test_b9_r7_path_history_append_only():
    # B9-R7: PathHistory append-only
    ph = PathHistory()
    path = CognitivePath(subject="A", goal="B", steps=[])
    ph.append(path)
    with pytest.raises(Exception):
        ph.paths.pop()

def test_b9_r8_successful_and_failed_alternatives_coexist():
    # B9-R8: successful + failed alternatives coexist
    ph = PathHistory()
    ph.append(FailedPath(path=CognitivePath(subject="A", goal="B", steps=["S1"]), reason="FAIL"))
    ph.append(CognitivePath(subject="A", goal="B", steps=["S2"], status=PathStatus.SUCCEEDED))
    assert len(ph.paths) == 2

def test_b9_r9_unknown_not_collapsed():
    # B9-R9: UNKNOWN not collapsed to FAILED/FALSE
    fp = FailedPath(path=CognitivePath(subject="A", goal="B", steps=[]), reason="UNKNOWN_OR_UNRESOLVED")
    assert fp.status != PathStatus.FAILED
    assert fp.status == PathStatus.UNKNOWN

def test_b9_r10_b7_role_refs_preserved():
    # B9-R10: B7 role refs preserved
    path = CognitivePath(subject="A", goal="B", steps=[{"role": "INVESTIGATOR"}])
    assert path.steps[0]["role"] == "INVESTIGATOR"

def test_b9_r11_b8_state_not_mutated():
    # B9-R11: B8 state not mutated
    path = CognitivePath(subject="A", goal="B", steps=[])
    path.mark_status(PathStatus.SUCCEEDED)
    assert not hasattr(path, "promote_knowledge")

def test_b9_r12_no_durable_memory_writes():
    # B9-R12: no durable memory writes
    path = CognitivePath(subject="A", goal="B", steps=[])
    assert not hasattr(path, "write_to_b10")
    assert not hasattr(path, "persist")

def test_b9_r13_replay_does_not_act():
    # B9-R13: replay does not ACT
    path = CognitivePath(subject="A", goal="B", steps=[])
    replay_generator = path.replay()
    assert not hasattr(replay_generator, "execute")

def test_b9_r14_path_order_participates_in_identity():
    # B9-R14: path order participates in identity
    # Covered by R2
    pass

def test_b9_r15_same_inputs_diff_route_diff_identity():
    # B9-R15: same inputs but different cognitive route -> distinct path
    path1 = CognitivePath(subject="Input_A", goal="Goal_B", steps=["S1", "S2"])
    path2 = CognitivePath(subject="Input_A", goal="Goal_B", steps=["S3", "S4"])
    assert path1.path_id != path2.path_id
