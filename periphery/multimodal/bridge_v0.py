"""F6 multimodal situated-observation bridge.

Modalities remain evidence channels with their own clocks, provenance and
uncertainty. Fusion never creates truth, identity, causality or authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0


@dataclass(frozen=True)
class ModalityObservationV0:
    observation_id: str
    modality: str
    observed_at: str
    source_ref: str
    source_hash: str
    state: dict[str, object]
    evidence_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    latency_ms: float | None = None
    frame_ref: str | None = None
    generated: bool = False
    causal_status: str = "UNKNOWN"

    def __post_init__(self) -> None:
        if not all((self.observation_id, self.modality, self.observed_at, self.source_ref, self.source_hash)):
            raise ValueError("multimodal observation requires identity, modality, time and provenance")
        if self.generated and self.causal_status == "CAUSAL_PROVEN":
            raise ValueError("generated content cannot establish physical causality")


def modality_to_world_observation(item: ModalityObservationV0) -> WorldObservationV0:
    uncertainty = item.uncertainty
    if item.latency_ms is None:
        uncertainty = tuple(dict.fromkeys((*uncertainty, "LATENCY_UNKNOWN")))
    if item.frame_ref is None:
        uncertainty = tuple(dict.fromkeys((*uncertainty, "FRAME_UNKNOWN")))
    return WorldObservationV0(
        observation_id=item.observation_id,
        observed_at=item.observed_at,
        source_refs=(item.source_ref,),
        source_hashes=(item.source_hash,),
        entity_ref=f"multimodal:{item.modality}",
        state={**item.state, "modality": item.modality, "generated": item.generated, "latency_ms": item.latency_ms, "frame_ref": item.frame_ref},
        uncertainty=uncertainty,
        contradictions=item.contradictions,
        evidence_refs=item.evidence_refs,
        causal_status=item.causal_status,
    )


def fuse_modalities_v0(*items: ModalityObservationV0, world_state_id: str, valid_at: str) -> WorldStateV0:
    if not items:
        raise ValueError("at least one modality observation is required")
    observations = tuple(modality_to_world_observation(item) for item in items)
    unknowns = tuple(dict.fromkeys(x for obs in observations for x in obs.uncertainty))
    contradictions = tuple(dict.fromkeys(x for obs in observations for x in obs.contradictions))
    provenance = tuple(dict.fromkeys(item.source_ref for item in items))
    risk_flags = ("GENERATED_OUTPUT_NOT_TRUTH",) if any(item.generated for item in items) else ()
    return WorldStateV0(
        world_state_id=world_state_id,
        valid_at=valid_at,
        observations=observations,
        candidate_reality=True,
        unknowns=unknowns,
        contradictions=contradictions,
        risk_flags=risk_flags,
        provenance_refs=provenance,
    )
