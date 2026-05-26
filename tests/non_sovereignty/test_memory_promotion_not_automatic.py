import pytest
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy
from periphery.memory.memory_candidate import build_memory_candidate_v2, MemoryCandidate
from periphery.memory.memory_source_types import MemoryCandidateStatus, MemorySourceType


def _make_candidate(status: MemoryCandidateStatus, auto: bool = False) -> MemoryCandidate:
    c = build_memory_candidate_v2("src1", MemorySourceType.BRODY_RUNTIME, "test content")
    c.status = status
    c.auto_promotion_allowed = auto
    return c


def test_auto_promotion_blocked():
    c = _make_candidate(MemoryCandidateStatus.PROMOTION_READY, auto=False)
    r = evaluate_promotion_policy(c)
    assert r.auto_promotion_blocked is True


def test_auto_promotion_allowed_invariant_violated():
    c = _make_candidate(MemoryCandidateStatus.PROMOTION_READY, auto=True)
    r = evaluate_promotion_policy(c)
    assert "INVARIANT" in r.reason or r.promotion_allowed is False


def test_candidate_memory_write_false():
    c = build_memory_candidate_v2("src2", MemorySourceType.FEEDBACK_CAPTURE, "test content")
    assert c.memory_write_allowed is False


def test_candidate_auto_promotion_false():
    c = build_memory_candidate_v2("src3", MemorySourceType.BRODY_RUNTIME, "test content")
    assert c.auto_promotion_allowed is False


def test_promoted_manual_only_needs_human():
    c = _make_candidate(MemoryCandidateStatus.PROMOTION_READY)
    r = evaluate_promotion_policy(c)
    assert r.requires_human_review is True
