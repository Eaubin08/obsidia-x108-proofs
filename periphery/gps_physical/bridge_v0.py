"""F5 GPS physical-world bridge into MMonde/UDIP.

Recorded evidence is represented conservatively. Provenance is not promoted to
physical authenticity, and receiver/configuration blockers remain explicit.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0
from periphery.udip.contracts_v0 import DomainStateRefV0, world_state_to_domain_state


@dataclass(frozen=True)
class RecordedGpsEvidenceV0:
    evidence_id: str
    observed_at: str
    source_ref: str
    source_hash: str
    proof_level: str
    state: dict[str, object]
    evidence_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    physical_authenticity_proven: bool = False
    receiver_status: str = "UNKNOWN"

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.observed_at or not self.source_ref or not self.source_hash:
            raise ValueError("recorded GPS evidence requires identity, time, source and source hash")
        if self.physical_authenticity_proven and self.proof_level.startswith("RECORDED_"):
            raise ValueError("recorded provenance alone cannot prove physical authenticity")


def recorded_gps_to_world(evidence: RecordedGpsEvidenceV0) -> WorldStateV0:
    risk_flags: tuple[str, ...] = ()
    unknowns = evidence.uncertainty
    if evidence.receiver_status == "BLOCKED_RECEIVER_CONFIGURATION":
        unknowns = tuple(dict.fromkeys((*unknowns, "RECEIVER_CONFIGURATION_BLOCKED")))
        risk_flags = ("LIVE_OR_ATTACK_CLAIM_NOT_CLOSED",)

    obs = WorldObservationV0(
        observation_id=evidence.evidence_id,
        observed_at=evidence.observed_at,
        source_refs=(evidence.source_ref,),
        source_hashes=(evidence.source_hash,),
        entity_ref="gps_physical_observation",
        state=dict(evidence.state),
        uncertainty=unknowns,
        contradictions=evidence.contradictions,
        evidence_refs=evidence.evidence_refs,
        causal_status="UNKNOWN",
    )
    return WorldStateV0(
        world_state_id=f"gps-world:{evidence.evidence_id}",
        valid_at=evidence.observed_at,
        observations=(obs,),
        candidate_reality=True,
        unknowns=unknowns,
        contradictions=evidence.contradictions,
        risk_flags=risk_flags,
        provenance_refs=(evidence.source_ref,),
    )


def recorded_gps_to_domain(evidence: RecordedGpsEvidenceV0) -> DomainStateRefV0:
    return world_state_to_domain_state(recorded_gps_to_world(evidence), domain_id="gps_defense_aviation")
