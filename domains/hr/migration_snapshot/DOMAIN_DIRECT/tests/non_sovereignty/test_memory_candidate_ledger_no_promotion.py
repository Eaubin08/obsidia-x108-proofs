"""
V5A Non-Sovereignty Test: Memory candidate ledger never auto-promotes.
Memory candidates are capture-only. Promotion requires human review.
"""
import pytest
from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_source_types import MemorySourceType
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy


def test_memory_candidate_write_blocked():
    """Every memory candidate must have memory_write_allowed=False."""
    candidate = build_memory_candidate_v2(
        source_id="test_source",
        source_type=MemorySourceType.BRODY_RUNTIME,
        content="Test memory content",
    )
    assert candidate.memory_write_allowed is False


def test_memory_candidate_auto_promotion_blocked():
    """Every memory candidate must have auto_promotion_allowed=False."""
    candidate = build_memory_candidate_v2(
        source_id="test_source",
        source_type=MemorySourceType.CONTEXT_PACKET,
        content="Test",
    )
    assert candidate.auto_promotion_allowed is False


def test_promotion_policy_blocks_auto():
    """Promotion policy must return auto_promotion_blocked=True for all candidates."""
    candidate = build_memory_candidate_v2(
        source_id="test_promo",
        source_type=MemorySourceType.FEEDBACK_CAPTURE,
        content="Candidate for promotion test",
    )
    decision = evaluate_promotion_policy(candidate)
    assert decision.auto_promotion_blocked is True
    assert decision.promotion_allowed is False
    assert decision.requires_human_review is True


def test_all_source_types_block_auto_promotion():
    """Every source type must result in auto_promotion_blocked=True."""
    for source_type in MemorySourceType:
        if source_type == MemorySourceType.UNKNOWN:
            continue
        candidate = build_memory_candidate_v2(
            source_id=f"test_{source_type.value}",
            source_type=source_type,
            content=f"Content from {source_type.value}",
        )
        assert candidate.auto_promotion_allowed is False, f"Source {source_type.value}: auto_promotion must be blocked"


def test_promotion_decision_never_allows():
    """PromotionDecision must never show promotion_allowed=True without human review."""
    candidate = build_memory_candidate_v2(
        source_id="test_never",
        source_type=MemorySourceType.HUMAN_REVIEW,
        content="Even human review source needs review",
    )
    decision = evaluate_promotion_policy(candidate)
    assert decision.promotion_allowed is False
