"""F7 governed-world adapter into the sovereign GuardX108 boundary.

World/domain payloads contribute evidence, unknowns, contradictions and risks.
They never provide a final gate, ticket, permission, or execution authority.
"""
from __future__ import annotations

from sigma.contracts import Domain, DomainAggregate
from sigma.guard import GuardX108

from periphery.udip.contracts_v0 import GovernancePayloadV0


_DOMAIN_MAP = {domain.value: domain for domain in Domain}


def governance_payload_to_aggregate(
    payload: GovernancePayloadV0,
    *,
    confidence: float,
) -> DomainAggregate:
    domain = _DOMAIN_MAP.get(payload.domain_id)
    if domain is None:
        raise ValueError(f"unsupported KX108 domain: {payload.domain_id}")
    if payload.decision is not None or payload.binder_permission or payload.allowed_to_act:
        raise ValueError("world/domain payload cannot arrive with decision or action authority")

    provenance_evidence = tuple(f"provenance:{ref}" for ref in payload.provenance_refs)
    return DomainAggregate(
        domain=domain,
        market_verdict="HOLD",
        confidence=confidence,
        contradictions=list(payload.contradictions),
        unknowns=list(payload.unknowns),
        risk_flags=list(payload.risk_flags),
        evidence_refs=list(dict.fromkeys((*payload.evidence_refs, *provenance_evidence))),
        agent_votes=[],
        extra_metrics={
            "world_state_ref": payload.world_state_ref,
            "domain_state_ref": payload.domain_state_ref,
            "proposed_action_ref": payload.proposed_action_ref,
            "input_decision_authority": payload.decision_authority,
            "world_payload_can_decide": False,
            "world_payload_can_act": False,
        },
    )


def decide_governed_world_v0(
    payload: GovernancePayloadV0,
    *,
    confidence: float,
):
    """Only GuardX108 creates the canonical gate/envelope."""
    aggregate = governance_payload_to_aggregate(payload, confidence=confidence)
    return GuardX108().decide(aggregate)
