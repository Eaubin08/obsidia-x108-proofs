from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from ..constants import AGENT_IDS, DECISION_AUTHORITY
from ..models import AgentSignal, Boundary

AGENT_ROLE = {
    "id": AGENT_IDS[5],
    "name": "Readonly aggregator",
    "purpose": "Aggregate Agent 1..5 signals into one context-only packet candidate.",
    "authority": "none; explicitly refuses authority escalation",
    "output": "normalized signal bundle, warning set, authority refusal block",
}


def aggregate_readonly(signals: List[AgentSignal]) -> AgentSignal:
    """Agent 6 — readonly aggregator.

    Aggregation is not arbitration. It preserves contradictions instead of
    resolving them into a verdict.
    """
    payload_signals = [asdict(s) for s in signals]
    warnings = sorted({w for s in signals for w in s.warnings})
    statuses = {s.agent_id: s.status for s in signals}
    status = "READONLY_AGGREGATION_READY_WITH_WARNINGS" if warnings else "READONLY_AGGREGATION_READY"

    payload: Dict[str, Any] = {
        "agent_count": len(signals),
        "expected_agent_count_before_aggregator": 5,
        "signals": payload_signals,
        "statuses": statuses,
        "warnings": warnings,
        "confidence_floor": min([s.confidence for s in signals], default=0.0),
        "authority_refusal": {
            "decision_authority": DECISION_AUTHORITY,
            "workflow_authority": False,
            "agent_authority": False,
            "skill_authority": False,
            "aggregator_authority": False,
            "can_override_x108": False,
        },
        "aggregation_scope": "context_only_no_execution",
        "role_manifest": AGENT_ROLE,
    }

    return AgentSignal(
        agent_id=AGENT_IDS[5],
        signal_family="context_packet",
        status=status,
        summary=f"Aggregated {len(signals)} readonly agent signals.",
        payload=payload,
        confidence=payload["confidence_floor"],
        warnings=warnings,
        trace=["agent_01", "agent_02", "agent_03", "agent_04", "agent_05", "readonly_aggregation"],
        role="READONLY_AGGREGATOR",
        boundary=Boundary().as_dict(),
    )
