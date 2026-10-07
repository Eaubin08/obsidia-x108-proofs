"""F20 Cross-Modal Coherence V0.

Conservative compatibility layer across heterogeneous modality observations.
Reuses F6 modality observations and F15 compatibility statuses.

Cross-modal agreement never creates truth, identity, causality or authority.
Generated content cannot establish physical coherence.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.multimodal.bridge_v0 import ModalityObservationV0
from periphery.physical_evidence.contracts_v0 import CompatibilityStatusV0


@dataclass(frozen=True)
class CrossModalPairAssessmentV0:
    left_observation_ref: str
    right_observation_ref: str
    temporal: CompatibilityStatusV0
    spatial: CompatibilityStatusV0
    metric: CompatibilityStatusV0
    causal: CompatibilityStatusV0
    independence: CompatibilityStatusV0
    reasons: tuple[str, ...] = ()

    @property
    def incompatible(self) -> bool:
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
class CrossModalCoherenceReportV0:
    report_id: str
    modality_refs: tuple[str, ...]
    pair_assessments: tuple[CrossModalPairAssessmentV0, ...]
    uncertainty: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    generated_present: bool = False
    physical_coherence_proven: bool = False
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not self.report_id or len(self.modality_refs) < 2:
            raise ValueError("cross-modal report requires identity and at least two modality refs")
        if self.physical_coherence_proven:
            raise ValueError("F20 cannot self-promote physical coherence")
        if not self.readonly or not self.advisory_only:
            raise ValueError("cross-modal report must remain readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("cross-modal report cannot decide or act")


def assess_cross_modal_pair_v0(
    left: ModalityObservationV0,
    right: ModalityObservationV0,
) -> CrossModalPairAssessmentV0:
    if left.observation_id == right.observation_id:
        raise ValueError("cross-modal pair requires distinct observations")

    reasons: list[str] = []

    # Generated channels cannot establish physical cross-modal coherence.
    if left.generated or right.generated:
        reasons.append("GENERATED_MODALITY_NOT_PHYSICAL_TRUTH")

    temporal = (
        CompatibilityStatusV0.COMPATIBLE
        if left.observed_at == right.observed_at
        else CompatibilityStatusV0.UNKNOWN
    )
    if temporal == CompatibilityStatusV0.UNKNOWN:
        reasons.append("TEMPORAL_ALIGNMENT_NOT_PROVEN")

    if left.frame_ref is None or right.frame_ref is None:
        spatial = CompatibilityStatusV0.UNKNOWN
        reasons.append("SPATIAL_FRAME_UNKNOWN")
    elif left.frame_ref == right.frame_ref:
        spatial = CompatibilityStatusV0.COMPATIBLE
    else:
        spatial = CompatibilityStatusV0.UNKNOWN
        reasons.append("FRAME_TRANSFORM_NOT_PROVEN")

    # Metric compatibility is only asserted when both observations explicitly
    # expose the same unit. Heterogeneous modalities otherwise remain UNKNOWN.
    left_unit = left.state.get("unit")
    right_unit = right.state.get("unit")
    if left_unit is None or right_unit is None:
        metric = CompatibilityStatusV0.UNKNOWN
        reasons.append("METRIC_COMPATIBILITY_NOT_PROVEN")
    elif left_unit == right_unit:
        metric = CompatibilityStatusV0.COMPATIBLE
    else:
        metric = CompatibilityStatusV0.UNKNOWN
        reasons.append("METRIC_TRANSFORM_NOT_PROVEN")

    # F20 never derives causality from agreement.
    causal = CompatibilityStatusV0.UNKNOWN
    reasons.append("CAUSAL_COMPATIBILITY_NOT_PROVEN")

    independence = (
        CompatibilityStatusV0.COMPATIBLE
        if left.source_ref != right.source_ref
        else CompatibilityStatusV0.UNKNOWN
    )
    if independence == CompatibilityStatusV0.UNKNOWN:
        reasons.append("SOURCE_INDEPENDENCE_NOT_PROVEN")

    return CrossModalPairAssessmentV0(
        left_observation_ref=left.observation_id,
        right_observation_ref=right.observation_id,
        temporal=temporal,
        spatial=spatial,
        metric=metric,
        causal=causal,
        independence=independence,
        reasons=tuple(dict.fromkeys(reasons)),
    )


def build_cross_modal_coherence_report_v0(
    *,
    report_id: str,
    observations: tuple[ModalityObservationV0, ...],
) -> CrossModalCoherenceReportV0:
    if len(observations) < 2:
        raise ValueError("cross-modal coherence requires at least two observations")

    pairs: list[CrossModalPairAssessmentV0] = []
    for i, left in enumerate(observations):
        for right in observations[i + 1 :]:
            pairs.append(assess_cross_modal_pair_v0(left, right))

    uncertainty = tuple(
        dict.fromkeys(
            reason
            for pair in pairs
            for reason in pair.reasons
            if reason.endswith("_NOT_PROVEN") or reason.endswith("_UNKNOWN")
        )
    )
    contradictions = tuple(
        dict.fromkeys(
            contradiction
            for observation in observations
            for contradiction in observation.contradictions
        )
    )
    evidence_refs = tuple(
        dict.fromkeys(
            ref
            for observation in observations
            for ref in observation.evidence_refs
        )
    )
    provenance_refs = tuple(dict.fromkeys(observation.source_ref for observation in observations))

    return CrossModalCoherenceReportV0(
        report_id=report_id,
        modality_refs=tuple(observation.observation_id for observation in observations),
        pair_assessments=tuple(pairs),
        uncertainty=uncertainty,
        contradictions=contradictions,
        evidence_refs=evidence_refs,
        provenance_refs=provenance_refs,
        generated_present=any(observation.generated for observation in observations),
    )
