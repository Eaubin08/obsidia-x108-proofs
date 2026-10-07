"""F15 Physical Evidence Plane V0.

Generic compatibility assessment for physical evidence candidates.
This layer does NOT decide truth, does NOT replace domain-specific gates,
and does NOT authorize execution. It only evaluates whether evidence channels
are mutually compatible enough to remain admissible as a physical candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from periphery.physical_signal.contracts_v0 import (
    PhysicalSignalEventV0,
    PhysicalSignalReportV0,
    WorldStateCandidateV0,
)


class CompatibilityStatusV0(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceCompatibilityV0:
    temporal: CompatibilityStatusV0
    spatial: CompatibilityStatusV0
    metric: CompatibilityStatusV0
    causal: CompatibilityStatusV0
    independence: CompatibilityStatusV0
    reasons: tuple[str, ...] = ()

    @property
    def fail_closed(self) -> bool:
        return any(
            status == CompatibilityStatusV0.INCOMPATIBLE
            for status in (
                self.temporal,
                self.spatial,
                self.metric,
                self.causal,
                self.independence,
            )
        )


@dataclass(frozen=True)
class ReplayablePhysicalEvidenceCandidateV0:
    evidence_id: str
    report_ref: str
    world_candidate_ref: str
    event_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    compatibility: EvidenceCompatibilityV0
    replay_refs: tuple[str, ...] = ()
    source_hash_refs: tuple[str, ...] = ()
    physical_authenticity_proven: bool = False
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.report_ref or not self.world_candidate_ref:
            raise ValueError("physical evidence candidate requires identity and bindings")
        if not self.event_refs:
            raise ValueError("physical evidence candidate requires event refs")
        if not self.replay_refs:
            raise ValueError("replayable physical evidence candidate requires replay_refs")
        if self.physical_authenticity_proven:
            raise ValueError("F15 evidence candidate cannot promote itself to physical truth")
        if not self.readonly or not self.advisory_only:
            raise ValueError("physical evidence candidate must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("physical evidence candidate cannot decide or act")


def assess_physical_compatibility_v0(
    events: tuple[PhysicalSignalEventV0, ...],
) -> EvidenceCompatibilityV0:
    if not events:
        raise ValueError("at least one physical event is required")

    reasons: list[str] = []

    # Temporal compatibility:
    observed = [event.measurement.context.time.observed_at for event in events]
    temporal = CompatibilityStatusV0.COMPATIBLE if len(set(observed)) == 1 else CompatibilityStatusV0.UNKNOWN
    if temporal == CompatibilityStatusV0.UNKNOWN:
        reasons.append("TEMPORAL_ALIGNMENT_NOT_PROVEN")

    # Spatial compatibility:
    frames = []
    for event in events:
        frame = event.measurement.context.spatial_frame
        frames.append(frame.frame_ref if frame is not None else None)
    known_frames = [f for f in frames if f is not None]
    if not known_frames:
        spatial = CompatibilityStatusV0.UNKNOWN
        reasons.append("SPATIAL_FRAME_UNKNOWN")
    elif len(set(known_frames)) == 1 and len(known_frames) == len(events):
        spatial = CompatibilityStatusV0.COMPATIBLE
    else:
        spatial = CompatibilityStatusV0.UNKNOWN
        reasons.append("FRAME_TRANSFORM_NOT_PROVEN")

    # Metric compatibility:
    units = [event.measurement.context.unit for event in events]
    known_units = [u for u in units if u is not None]
    if not known_units:
        metric = CompatibilityStatusV0.UNKNOWN
        reasons.append("METRIC_UNIT_UNKNOWN")
    elif len(set(known_units)) == 1 and len(known_units) == len(events):
        metric = CompatibilityStatusV0.COMPATIBLE
    else:
        metric = CompatibilityStatusV0.UNKNOWN
        reasons.append("METRIC_COMPATIBILITY_NOT_PROVEN")

    # Causal compatibility:
    # F15 never infers causality from co-occurrence.
    causal = CompatibilityStatusV0.UNKNOWN
    reasons.append("CAUSAL_COMPATIBILITY_NOT_PROVEN")

    # Independence:
    sources = [tuple(event.measurement.source_refs) for event in events]
    flattened = [ref for group in sources for ref in group]
    independence = (
        CompatibilityStatusV0.COMPATIBLE
        if len(events) >= 2 and len(flattened) == len(set(flattened)) and len(flattened) >= 2
        else CompatibilityStatusV0.UNKNOWN
    )
    if independence == CompatibilityStatusV0.UNKNOWN:
        reasons.append("SOURCE_INDEPENDENCE_NOT_PROVEN")

    return EvidenceCompatibilityV0(
        temporal=temporal,
        spatial=spatial,
        metric=metric,
        causal=causal,
        independence=independence,
        reasons=tuple(dict.fromkeys(reasons)),
    )


def build_replayable_physical_evidence_candidate_v0(
    *,
    evidence_id: str,
    report: PhysicalSignalReportV0,
    world_candidate: WorldStateCandidateV0,
    events: tuple[PhysicalSignalEventV0, ...],
    replay_refs: tuple[str, ...] = (),
) -> ReplayablePhysicalEvidenceCandidateV0:
    event_ids = tuple(event.event_id for event in events)
    missing = [ref for ref in report.event_refs if ref not in event_ids]
    if missing:
        raise ValueError(f"report references missing events: {missing}")
    if world_candidate.physical_report_ref != report.report_id:
        raise ValueError("world candidate/report binding mismatch")

    compatibility = assess_physical_compatibility_v0(events)

    evidence_refs = tuple(dict.fromkeys((
        *report.evidence_refs,
        *(ref for event in events for ref in event.measurement.evidence_refs),
    )))
    provenance_refs = tuple(dict.fromkeys((
        *report.provenance_refs,
        *(ref for event in events for ref in event.measurement.source_refs),
    )))
    source_hash_refs = tuple(dict.fromkeys(
        ref for event in events for ref in event.measurement.source_hashes
    ))

    return ReplayablePhysicalEvidenceCandidateV0(
        evidence_id=evidence_id,
        report_ref=report.report_id,
        world_candidate_ref=world_candidate.candidate_id,
        event_refs=event_ids,
        evidence_refs=evidence_refs,
        provenance_refs=provenance_refs,
        compatibility=compatibility,
        replay_refs=replay_refs,
        source_hash_refs=source_hash_refs,
    )
