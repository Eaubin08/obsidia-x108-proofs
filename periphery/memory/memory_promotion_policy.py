"""
Memory Promotion Policy — defines rules for memory promotion.
Auto-promotion is NEVER allowed. PROMOTED_MANUAL_ONLY requires human review.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .memory_source_types import MemoryCandidateStatus
from .memory_candidate import MemoryCandidate


@dataclass
class PromotionDecision:
    candidate_id: str
    current_status: str
    promotion_allowed: bool
    reason: str
    requires_human_review: bool = True
    auto_promotion_blocked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "current_status": self.current_status,
            "promotion_allowed": self.promotion_allowed,
            "reason": self.reason,
            "requires_human_review": self.requires_human_review,
            "auto_promotion_blocked": self.auto_promotion_blocked,
        }


def evaluate_promotion_policy(candidate: MemoryCandidate) -> PromotionDecision:
    if candidate.auto_promotion_allowed:
        return PromotionDecision(
            candidate_id=candidate.candidate_id,
            current_status=candidate.status.value,
            promotion_allowed=False,
            reason="AUTO_PROMOTION_INVARIANT_VIOLATED",
            requires_human_review=True,
            auto_promotion_blocked=True,
        )

    if candidate.status == MemoryCandidateStatus.REJECTED:
        return PromotionDecision(
            candidate_id=candidate.candidate_id,
            current_status=candidate.status.value,
            promotion_allowed=False,
            reason="CANDIDATE_REJECTED",
            requires_human_review=True,
        )

    if candidate.status == MemoryCandidateStatus.PROMOTION_READY:
        return PromotionDecision(
            candidate_id=candidate.candidate_id,
            current_status=candidate.status.value,
            promotion_allowed=True,
            reason="HUMAN_REVIEW_REQUIRED_BEFORE_PROMOTION",
            requires_human_review=True,
            auto_promotion_blocked=True,
        )

    return PromotionDecision(
        candidate_id=candidate.candidate_id,
        current_status=candidate.status.value,
        promotion_allowed=False,
        reason=f"STATUS_NOT_READY_FOR_PROMOTION:{candidate.status.value}",
        requires_human_review=True,
    )
