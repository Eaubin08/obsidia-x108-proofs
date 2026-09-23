"""
Demo: Feedback memory candidate — always read-only, memory_write_allowed=False.
No memory is written. Bridge returns candidate packet only.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate


def run_feedback_memory_candidate(action_id: str, context_summary: str) -> dict:
    candidate = build_memory_candidate(
        action_id=action_id,
        context_summary=context_summary,
        source_agent="demo_agent",
        gate="ALLOW",
    )

    assert candidate.memory_write_allowed is False, "CRITICAL: memory_write_allowed must be False"

    return {
        "action_id": candidate.action_id,
        "memory_write_allowed": candidate.memory_write_allowed,
        "candidate_id": candidate.candidate_id,
        "source_agent": candidate.source_agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = run_feedback_memory_candidate("demo_mem_001", "User requested balance check — ALLOW gate.")
    print(json.dumps(result, indent=2))
    assert result["memory_write_allowed"] is False
    print("✓ Feedback memory candidate demo complete — memory_write_allowed=False always")
