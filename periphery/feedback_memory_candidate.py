from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class FeedbackMemoryCandidate:
    action_id: str
    source_ticket_id: str
    memory_write_allowed: bool
    memory_policy: str
    candidate_payload: dict[str, Any]

def build_feedback_memory_candidate(action: Any, ticket: Any, feedback: dict[str, Any], memory_status: str = "STABLE") -> FeedbackMemoryCandidate:
    if memory_status != "STABLE":
        policy = "FROZEN_IF_UNSTABLE"
        allowed = False
    else:
        policy = "CANDIDATE_ONLY_READONLY_REVIEW_REQUIRED"
        allowed = False

    return FeedbackMemoryCandidate(
        action_id=action.action_id,
        source_ticket_id=getattr(ticket, "ticket_id", "UNKNOWN"),
        memory_write_allowed=allowed,
        memory_policy=policy,
        candidate_payload={"feedback": feedback, "action_id": action.action_id},
    )
