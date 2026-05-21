"""
Demo connector: Brody + Memory readonly flow.
Shows Brody responding with read-only contract, memory candidate captured (no write).
"""
from periphery.brody.brody_runtime_readonly import brody_respond
from periphery.brody.brody_response_contract import BRODY_CONTRACT
from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy
from periphery.memory.memory_source_types import MemoryCandidateStatus, MemorySourceType


def run_brody_memory_readonly_flow():
    BRODY_CONTRACT.validate()

    response = brody_respond("What is the governance context for this session?", "en")
    assert response.readonly is True
    assert response.emits_act is False
    assert response.memory_write is False

    candidate = build_memory_candidate_v2(
        source_id="brody_demo_session",
        source_type=MemorySourceType.BRODY_RUNTIME,
        content=response.response_text,
    )
    assert candidate.memory_write_allowed is False
    assert candidate.auto_promotion_allowed is False

    policy = evaluate_promotion_policy(candidate)
    assert policy.auto_promotion_blocked is True
    assert policy.requires_human_review is True

    return {
        "brody_response": response.to_dict(),
        "memory_candidate": candidate.to_dict(),
        "promotion_policy": policy.to_dict(),
        "flow": "BRODY_MEMORY_READONLY_FLOW_OK",
    }


if __name__ == "__main__":
    import json
    result = run_brody_memory_readonly_flow()
    print(json.dumps(result, indent=2))
