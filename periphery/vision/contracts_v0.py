"""F16 Vision / Real Image V0.

Situated real-image observation contracts. This layer preserves capture context,
visual primitives, physical-signal references, candidate interpretations and an
integrity report. It does not turn perception into truth and does not authorize
decision or action.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.mmonde.contracts_v0 import WorldObservationV0
from periphery.multimodal.bridge_v0 import ModalityObservationV0


@dataclass(frozen=True)
class ImageAssetRefV0:
    asset_ref: str
    asset_hash: str
    media_type: str = "image"

    def __post_init__(self) -> None:
        if not self.asset_ref or not self.asset_hash:
            raise ValueError("image asset requires immutable ref and hash")


@dataclass(frozen=True)
class CaptureContextV0:
    device_ref: str | None = None
    optics_ref: str | None = None
    author_ref: str | None = None
    application_ref: str | None = None
    consent_ref: str | None = None
    capture_parameters: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class VisualPrimitiveV0:
    primitive_id: str
    primitive_kind: str
    label: str | None = None
    confidence: float | None = None
    geometry_ref: str | None = None
    mask_ref: str | None = None
    depth_ref: str | None = None
    motion_ref: str | None = None
    text_value: str | None = None
    feature_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.primitive_id or not self.primitive_kind:
            raise ValueError("visual primitive requires identity and kind")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("visual primitive confidence must be between 0 and 1")


@dataclass(frozen=True)
class CandidateInterpretationV0:
    interpretation_id: str
    claim: str
    supporting_primitive_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    confidence: float | None = None
    observed_fact: bool = False
    generated_hypothesis: bool = False

    def __post_init__(self) -> None:
        if not self.interpretation_id or not self.claim:
            raise ValueError("candidate interpretation requires identity and claim")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("candidate interpretation confidence must be between 0 and 1")
        if self.observed_fact and self.generated_hypothesis:
            raise ValueError("generated hypothesis cannot simultaneously be asserted as observed fact")


@dataclass(frozen=True)
class ImageIntegrityReportV0:
    quality_flags: tuple[str, ...] = ()
    calibration_refs: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    freshness_flags: tuple[str, ...] = ()
    synchronized_signal_refs: tuple[str, ...] = ()
    physical_compatibility_refs: tuple[str, ...] = ()
    integrity_proven: bool = False

    def __post_init__(self) -> None:
        if self.integrity_proven and not self.physical_compatibility_refs:
            raise ValueError("integrity_proven requires physical compatibility evidence refs")


@dataclass(frozen=True)
class RealImageObservationV0:
    observation_id: str
    observed_at: str
    asset: ImageAssetRefV0
    source_ref: str
    capture_context: CaptureContextV0
    frame_ref: str | None = None
    latency_ms: float | None = None
    primitives: tuple[VisualPrimitiveV0, ...] = ()
    physical_signal_refs: tuple[str, ...] = ()
    prior_state_refs: tuple[str, ...] = ()
    context_graph_refs: tuple[str, ...] = ()
    candidate_interpretations: tuple[CandidateInterpretationV0, ...] = ()
    integrity: ImageIntegrityReportV0 = ImageIntegrityReportV0()
    evidence_refs: tuple[str, ...] = ()
    generated: bool = False
    readonly: bool = True
    representation_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.observation_id or not self.observed_at or not self.source_ref:
            raise ValueError("real image observation requires identity, time and provenance")
        if self.generated:
            raise ValueError("RealImageObservationV0 cannot represent generated imagery")
        if not self.readonly or not self.representation_only:
            raise ValueError("real image observation must remain readonly representation")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("real image observation cannot decide or act")


def real_image_to_modality_observation_v0(item: RealImageObservationV0) -> ModalityObservationV0:
    uncertainty = tuple(dict.fromkeys((
        *item.integrity.uncertainty,
        *(("FRAME_UNKNOWN",) if item.frame_ref is None else ()),
        *(("LATENCY_UNKNOWN",) if item.latency_ms is None else ()),
    )))
    contradictions = tuple(dict.fromkeys(item.integrity.contradictions))
    state = {
        "asset_ref": item.asset.asset_ref,
        "asset_hash": item.asset.asset_hash,
        "media_type": item.asset.media_type,
        "device_ref": item.capture_context.device_ref,
        "optics_ref": item.capture_context.optics_ref,
        "author_ref": item.capture_context.author_ref,
        "application_ref": item.capture_context.application_ref,
        "consent_ref": item.capture_context.consent_ref,
        "capture_parameters": dict(item.capture_context.capture_parameters),
        "primitives": [
            {
                "primitive_id": p.primitive_id,
                "primitive_kind": p.primitive_kind,
                "label": p.label,
                "confidence": p.confidence,
                "geometry_ref": p.geometry_ref,
                "mask_ref": p.mask_ref,
                "depth_ref": p.depth_ref,
                "motion_ref": p.motion_ref,
                "text_value": p.text_value,
                "feature_refs": list(p.feature_refs),
                "evidence_refs": list(p.evidence_refs),
            }
            for p in item.primitives
        ],
        "primitive_refs": [p.primitive_id for p in item.primitives],
        "physical_signal_refs": list(item.physical_signal_refs),
        "prior_state_refs": list(item.prior_state_refs),
        "context_graph_refs": list(item.context_graph_refs),
        "candidate_interpretation_refs": [c.interpretation_id for c in item.candidate_interpretations],
        "integrity_proven": item.integrity.integrity_proven,
    }
    return ModalityObservationV0(
        observation_id=item.observation_id,
        modality="image",
        observed_at=item.observed_at,
        source_ref=item.source_ref,
        source_hash=item.asset.asset_hash,
        state=state,
        evidence_refs=item.evidence_refs,
        uncertainty=uncertainty,
        contradictions=contradictions,
        latency_ms=item.latency_ms,
        frame_ref=item.frame_ref,
        generated=False,
        causal_status="UNKNOWN",
    )


def real_image_to_world_observation_v0(item: RealImageObservationV0) -> WorldObservationV0:
    from periphery.multimodal.bridge_v0 import modality_to_world_observation

    return modality_to_world_observation(real_image_to_modality_observation_v0(item))
