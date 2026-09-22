from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy
from periphery.memory.memory_source_types import MemorySourceType


def test_memory_cannot_decide_or_write():
    candidate = build_memory_candidate_v2(
        source_id="nsov_memory",
        source_type=MemorySourceType.BRODY_RUNTIME,
        content="readonly candidate",
    )

    decision = evaluate_promotion_policy(candidate)

    assert candidate.memory_write_allowed is False
    assert candidate.auto_promotion_allowed is False
    assert decision.auto_promotion_blocked is True
    assert decision.requires_human_review is True
