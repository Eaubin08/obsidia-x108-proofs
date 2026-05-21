"""
Demo connector: Memory feedback capture → candidate → promotion policy flow.
"""
from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy
from periphery.memory.memory_source_registry import list_sources
from periphery.memory.memory_source_types import MemoryCandidateStatus, MemorySourceType


def run_memory_feedback_candidate_flow():
    sources = list_sources()
    for src in sources:
        assert src.write_allowed is False

    candidate = build_memory_candidate_v2(
        source_id="demo_session_01",
        source_type=MemorySourceType.FEEDBACK_CAPTURE,
        content="User confirmed that governance layer responded correctly.",
    )
    assert candidate.memory_write_allowed is False
    assert candidate.status == MemoryCandidateStatus.CANDIDATE_ONLY

    candidate_rejected = build_memory_candidate_v2(
        "demo_session_02", MemorySourceType.BRODY_RUNTIME, "rejected content"
    )
    candidate_rejected.status = MemoryCandidateStatus.REJECTED
    policy_rejected = evaluate_promotion_policy(candidate_rejected)
    assert "REJECTED" in policy_rejected.reason

    candidate_ready = build_memory_candidate_v2(
        "demo_session_03", MemorySourceType.DOCUMENT_INGESTION, "ready content"
    )
    candidate_ready.status = MemoryCandidateStatus.PROMOTION_READY
    policy_ready = evaluate_promotion_policy(candidate_ready)
    assert policy_ready.auto_promotion_blocked is True
    assert policy_ready.requires_human_review is True

    return {
        "sources_readonly": True,
        "candidate": candidate.to_dict(),
        "policy_rejected": policy_rejected.to_dict(),
        "policy_ready": policy_ready.to_dict(),
        "flow": "MEMORY_FEEDBACK_CANDIDATE_FLOW_OK",
    }


if __name__ == "__main__":
    import json
    result = run_memory_feedback_candidate_flow()
    print(json.dumps(result, indent=2))
