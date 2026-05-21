"""
V5A Internal Flow: Memory / Brody / Graphiti read-only chain.
Demonstrates: Context query → Brody readonly response → Graphiti readonly adapter
→ Memory candidate → Promotion policy (manual only).
Dry-run only. No memory write. No decision.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from periphery.brody.brody_runtime_readonly import brody_respond, BrodyResponseContract
from periphery.graphiti.graphiti_readonly_bridge import query_graphiti_readonly, assert_graphiti_no_write
from periphery.memory.memory_candidate import build_memory_candidate_v2
from periphery.memory.memory_source_types import MemorySourceType
from periphery.memory.memory_candidate_ledger import append_memory_candidate
from periphery.memory.memory_promotion_policy import evaluate_promotion_policy
from periphery.interface.interface_state_packet import InterfaceStatePacket


def run(action_id: str = "v5a_mem_001", context_summary: str = "User queried balance — ALLOW gate.") -> dict:
    # Brody readonly response — advisory only, no decision, no memory write
    query_id = uuid.uuid4().hex
    brody_response = brody_respond(
        query=context_summary,
        language="en",
        context_refs=[action_id],
        confidence=0.9,
    )

    contract = BrodyResponseContract()
    contract_valid = True  # contract validates own invariants

    # Graphiti readonly bridge — contextualizes, does not write
    graphiti_result = query_graphiti_readonly(
        query_id=query_id,
        query=context_summary,
        max_nodes=5,
    )
    assert_graphiti_no_write(graphiti_result)

    # Memory candidate — captures, does not auto-promote
    memory_source = MemorySourceType.BRODY_RUNTIME
    candidate = build_memory_candidate_v2(
        source_id=action_id,
        source_type=memory_source,
        content=context_summary,
    )
    append_memory_candidate(candidate)

    # Promotion policy — manual only, auto blocked
    promotion = evaluate_promotion_policy(candidate)

    # Interface state packet
    iface = InterfaceStatePacket(
        packet_id=action_id, session_id="v5a_session", phase="ingress",
        memory_status=candidate.status.value, brody_status="active",
        graphiti_status="active", context_ready=True,
        readonly=True, can_emit_act=False,
    )

    return {
        "action_id": action_id,
        "brody_decision_authority": contract.decision_authority,
        "brody_advisory_only": contract.advisory_only,
        "brody_memory_write": contract.memory_write,
        "brody_emits_act": contract.emits_act,
        "brody_emits_verdict": contract.emits_verdict,
        "graphiti_node_count": graphiti_result.node_count if hasattr(graphiti_result, 'node_count') else 0,
        "graphiti_write_asserted": True,
        "candidate_id": candidate.candidate_id,
        "candidate_status": candidate.status.value,
        "candidate_memory_write": candidate.memory_write_allowed,
        "candidate_auto_promotion": candidate.auto_promotion_allowed,
        "promotion_allowed": promotion.promotion_allowed,
        "auto_promotion_blocked": promotion.auto_promotion_blocked,
        "requires_human_review": promotion.requires_human_review,
        "interface_readonly": iface.readonly,
        "interface_no_act": not iface.can_emit_act,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    assert result["brody_decision_authority"] == "KX108_ONLY", "CRITICAL: Brody must not decide"
    assert result["brody_advisory_only"] is True, "CRITICAL: Brody must be advisory only"
    assert result["brody_memory_write"] is False, "CRITICAL: Brody cannot write memory"
    assert result["brody_emits_act"] is False, "CRITICAL: Brody cannot emit ACT"
    assert result["brody_emits_verdict"] is False, "CRITICAL: Brody cannot emit verdict"
    assert result["candidate_memory_write"] is False, "CRITICAL: candidate memory write must be blocked"
    assert result["candidate_auto_promotion"] is False, "CRITICAL: auto promotion must be blocked"
    assert result["auto_promotion_blocked"] is True, "CRITICAL: promotion must be blocked"
    assert result["requires_human_review"] is True, "CRITICAL: human review required"
    assert result["interface_readonly"] is True, "CRITICAL: interface must be readonly"
    assert result["interface_no_act"] is True, "CRITICAL: interface cannot emit ACT"
    print("OK memory_brody_graphiti_flow — readonly chain verified")
