"""
Memory Candidate — a candidate for memory promotion. Never auto-promoted.
Human review required for PROMOTED_MANUAL_ONLY status.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .memory_source_types import MemorySourceType, MemoryCandidateStatus


@dataclass
class MemoryCandidate:
    candidate_id: str
    source_id: str
    source_type: MemorySourceType
    content_hash: str
    content_summary: str
    status: MemoryCandidateStatus
    memory_write_allowed: bool = False
    auto_promotion_allowed: bool = False
    created_at: str = ""
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "content_hash": self.content_hash,
            "content_summary": self.content_summary,
            "status": self.status.value,
            "memory_write_allowed": self.memory_write_allowed,
            "auto_promotion_allowed": self.auto_promotion_allowed,
            "created_at": self.created_at,
            "risk_flags": self.risk_flags,
        }


def build_memory_candidate_v2(
    source_id: str,
    source_type: MemorySourceType,
    content: str,
) -> MemoryCandidate:
    h = hashlib.sha256(content.encode()).hexdigest()
    return MemoryCandidate(
        candidate_id=uuid.uuid4().hex,
        source_id=source_id,
        source_type=source_type,
        content_hash=h,
        content_summary=content[:200],
        status=MemoryCandidateStatus.CANDIDATE_ONLY,
        memory_write_allowed=False,
        auto_promotion_allowed=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
