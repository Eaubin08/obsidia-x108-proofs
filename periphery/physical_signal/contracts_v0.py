"""F14 Physical Signal Periphery V0.

Generic physical-signal envelopes built on F13 situated measurements.
This layer aggregates evidence channels and contradictions into candidate world
state reports. It never promotes measurements to truth and never decides/acts.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.measurement.contracts_v0 import SituatedMeasurementV0
from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0


@dataclass(frozen=True)
class PhysicalSignalEventV0:
    event_id: str
    measurement: SituatedMeasurementV0
    signal_family: str
    quality_flags: tuple[str, ...] = ()
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.event_id or not self.signal_family:
            raise ValueError("physical signal event requires identity and signal family")
        if not self.readonly:
            raise ValueError("physical signal event must remain readonly")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("physical signal event cannot hold decision/action authority")


@dataclass(frozen=True)
class SignalContradictionV0:
    contradiction_id: str
    event_refs: tuple[str, ...]
    contradiction_kind: str
    detail: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.contradiction_id or not self.contradiction_kind or not self.detail:
            raise ValueError("signal contradiction requires identity, kind and detail")
        if len(self.event_refs) < 2:
            raise ValueError("signal contradiction requires at least two event refs")


@dataclass(frozen=True)
class PhysicalRiskHintV0:
    risk_code: str
    source_event_refs: tuple[str, ...]
    detail: str
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.risk_code or not self.detail:
            raise ValueError("physical risk hint requires code and detail")
        if not self.advisory_only:
            raise ValueError("physical risk hint must remain advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("physical risk hint cannot decide or act")


@dataclass(frozen=True)
class PhysicalSignalReportV0:
    report_id: str
    event_refs: tuple[str, ...]
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[SignalContradictionV0, ...] = ()
    risk_hints: tuple[PhysicalRiskHintV0, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    physical_authenticity_proven: bool = False
    readonly: bool = True

    def __post_init__(self) -> None:
        if not self.report_id or not self.event_refs:
            raise ValueError("physical signal report requires identity and event refs")
        if self.physical_authenticity_proven and not self.evidence_refs:
            raise ValueError("physical authenticity requires explicit evidence refs")
        if not self.readonly:
            raise ValueError("physical signal report must remain readonly")


@dataclass(frozen=True)
class WorldStateCandidateV0:
    candidate_id: str
    world_state: WorldStateV0
    physical_report_ref: str
    confidence: float | None = None
    physical_authenticity_proven: bool = False
    readonly: bool = True
    representation_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.physical_report_ref:
            raise ValueError("world state candidate requires identity and report ref")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.physical_authenticity_proven and not self.world_state.observations:
            raise ValueError("physical authenticity cannot exist without observations")
        if not self.readonly or not self.representation_only:
            raise ValueError("world state candidate must remain readonly representation")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("world state candidate cannot decide or act")


def physical_event_to_world_observation(event: PhysicalSignalEventV0) -> WorldObservationV0:
    m = event.measurement
    ctx = m.context
    uncertainty = tuple(dict.fromkeys((*ctx.uncertainty, *ctx.measurement_limits)))
    state = {
        "value": m.value,
        "signal_kind": ctx.signal_kind,
        "signal_family": event.signal_family,
        "unit": ctx.unit,
        "precision": ctx.precision,
        "instrument_ref": ctx.instrument.instrument_ref,
        "instrument_kind": ctx.instrument.instrument_kind,
        "configuration_ref": ctx.instrument.configuration_ref,
        "calibration_ref": ctx.instrument.calibration_ref,
        "environment_ref": ctx.environment_ref,
        "quality_flags": list(event.quality_flags),
    }
    space = {}
    if ctx.spatial_frame is not None:
        space = {
            "frame_ref": ctx.spatial_frame.frame_ref,
            "parent_frame_ref": ctx.spatial_frame.parent_frame_ref,
            "transform_refs": list(ctx.spatial_frame.transform_refs),
        }
    return WorldObservationV0(
        observation_id=event.event_id,
        observed_at=ctx.time.observed_at,
        source_refs=m.source_refs,
        source_hashes=m.source_hashes,
        entity_ref=ctx.phenomenon_ref,
        state=state,
        space=space,
        uncertainty=uncertainty,
        contradictions=ctx.contradictions,
        evidence_refs=m.evidence_refs,
        causal_status="UNKNOWN",
    )


def build_world_state_candidate_v0(
    *,
    candidate_id: str,
    report: PhysicalSignalReportV0,
    events: tuple[PhysicalSignalEventV0, ...],
    valid_at: str,
    confidence: float | None = None,
) -> WorldStateCandidateV0:
    if not events:
        raise ValueError("world state candidate requires physical signal events")
    event_ids = {event.event_id for event in events}
    missing = [ref for ref in report.event_refs if ref not in event_ids]
    if missing:
        raise ValueError(f"report references unknown physical events: {missing}")

    observations = tuple(physical_event_to_world_observation(event) for event in events)
    contradictions = tuple(dict.fromkeys((
        *report.uncertainty,
        *(c.contradiction_kind for c in report.contradictions),
    )))
    risk_flags = tuple(dict.fromkeys(h.risk_code for h in report.risk_hints))
    provenance = tuple(dict.fromkeys((
        *report.provenance_refs,
        *(ref for obs in observations for ref in obs.source_refs),
    )))

    world = WorldStateV0(
        world_state_id=f"physical-world:{candidate_id}",
        valid_at=valid_at,
        observations=observations,
        candidate_reality=True,
        unknowns=report.uncertainty,
        contradictions=tuple(c.contradiction_kind for c in report.contradictions),
        risk_flags=risk_flags,
        provenance_refs=provenance,
    )
    return WorldStateCandidateV0(
        candidate_id=candidate_id,
        world_state=world,
        physical_report_ref=report.report_id,
        confidence=confidence,
        physical_authenticity_proven=report.physical_authenticity_proven,
    )
