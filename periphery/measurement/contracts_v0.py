"""F13 Measurement / Evidence Contract V0.

Generic situated-measurement contracts between world dynamics and specialized
physical/vision/signal adapters. Representation only; no truth promotion,
sensor fusion, domain law, decision or execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.world_dynamics.contracts_v0 import SpatialFrameRefV0, TimeEnvelopeV0


@dataclass(frozen=True)
class InstrumentRefV0:
    instrument_ref: str
    instrument_kind: str
    configuration_ref: str | None = None
    calibration_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.instrument_ref or not self.instrument_kind:
            raise ValueError("instrument identity and kind are required")


@dataclass(frozen=True)
class MeasurementContextV0:
    phenomenon_ref: str
    signal_kind: str
    unit: str | None
    precision: float | None
    time: TimeEnvelopeV0
    instrument: InstrumentRefV0
    spatial_frame: SpatialFrameRefV0 | None = None
    environment_ref: str | None = None
    measurement_limits: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.phenomenon_ref or not self.signal_kind:
            raise ValueError("phenomenon_ref and signal_kind are required")
        if self.precision is not None and self.precision < 0:
            raise ValueError("precision cannot be negative")
        if self.instrument.calibration_ref is None and "CALIBRATION_UNKNOWN" not in self.uncertainty:
            raise ValueError("CALIBRATION_UNKNOWN: missing calibration must remain explicit as uncertainty")


@dataclass(frozen=True)
class SituatedMeasurementV0:
    measurement_id: str
    value: object
    context: MeasurementContextV0
    source_refs: tuple[str, ...]
    source_hashes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    physical_authenticity_proven: bool = False
    readonly: bool = True
    representation_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.measurement_id:
            raise ValueError("measurement_id is required")
        if not self.source_refs:
            raise ValueError("situated measurement requires at least one source_ref")
        if self.physical_authenticity_proven and not self.evidence_refs:
            raise ValueError("physical authenticity requires explicit evidence refs")
        if not self.readonly or not self.representation_only:
            raise ValueError("measurement contract is readonly representation only")
        if self.decision_authority != "KX108_ONLY":
            raise ValueError("decision authority must remain KX108_ONLY")
        if self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("measurement contract cannot decide or act")
