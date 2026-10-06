"""UDIP V0 — minimal bridge from situated world state to domain governance.

The bridge conserves references and uncertainty. It never creates a decision,
permission, execution capability, or domain-specific meaning.
DOMAIN != AUTHORITY. DOMAIN SIGNAL != DECISION. SOURCE != TRUST.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.mmonde.contracts_v0 import WorldStateV0


@dataclass(frozen=True)
class DomainStateRefV0:
    domain_id: str
    world_state_ref: str
    valid_at: str
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.domain_id or not self.world_state_ref or not self.valid_at:
            raise ValueError("domain_id, world_state_ref and valid_at are required")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("DomainStateRefV0 cannot decide or act")


@dataclass(frozen=True)
class GovernancePayloadV0:
    domain_id: str
    domain_state_ref: str
    world_state_ref: str
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    proposed_action_ref: str | None = None
    decision: str | None = None
    binder_permission: bool = False
    allowed_to_act: bool = False
    decision_authority: str = "KX108_ONLY"

    def __post_init__(self) -> None:
        if not self.domain_id or not self.domain_state_ref or not self.world_state_ref:
            raise ValueError("domain and state references are required")
        if self.decision is not None:
            raise ValueError("GovernancePayloadV0 transports proposals; it cannot contain a decision")
        if self.binder_permission or self.allowed_to_act:
            raise ValueError("GovernancePayloadV0 cannot grant permission or action")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")


def world_state_to_domain_state(world: WorldStateV0, *, domain_id: str) -> DomainStateRefV0:
    """Conservative MMonde -> Domain boundary; no domain semantics are invented."""
    evidence = tuple(dict.fromkeys(ref for obs in world.observations for ref in obs.evidence_refs))
    provenance = tuple(dict.fromkeys((*world.provenance_refs, *(ref for obs in world.observations for ref in obs.source_refs))))
    obs_unknowns = tuple(item for obs in world.observations for item in obs.uncertainty)
    obs_contradictions = tuple(item for obs in world.observations for item in obs.contradictions)
    return DomainStateRefV0(
        domain_id=domain_id,
        world_state_ref=world.world_state_id,
        valid_at=world.valid_at,
        unknowns=tuple(dict.fromkeys((*world.unknowns, *obs_unknowns))),
        contradictions=tuple(dict.fromkeys((*world.contradictions, *obs_contradictions))),
        risk_flags=world.risk_flags,
        evidence_refs=evidence,
        provenance_refs=provenance,
    )


def domain_state_to_governance_payload(
    state: DomainStateRefV0, *, proposed_action_ref: str | None = None
) -> GovernancePayloadV0:
    """Conservative Domain -> KX108 transport; proposal never becomes authority."""
    return GovernancePayloadV0(
        domain_id=state.domain_id,
        domain_state_ref=f"{state.domain_id}:{state.world_state_ref}:{state.valid_at}",
        world_state_ref=state.world_state_ref,
        unknowns=state.unknowns,
        contradictions=state.contradictions,
        risk_flags=state.risk_flags,
        evidence_refs=state.evidence_refs,
        provenance_refs=state.provenance_refs,
        proposed_action_ref=proposed_action_ref,
    )
