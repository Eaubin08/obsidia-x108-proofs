"""P3 GPS multi-source physical corroboration readiness.

Specialized layer on top of F13/F15/F20.

F20 may say that distinct source refs are compatible with independence, but P3
requires stronger evidence before removing the GPS blocker
MULTI_SOURCE_CORROBORATION_NOT_PROVEN.

This module never decides truth, causality, or action.
"""
from __future__ import annotations

from dataclasses import dataclass

from periphery.cross_modal.contracts_v0 import CrossModalCoherenceReportV0
from periphery.multimodal.bridge_v0 import ModalityObservationV0
from periphery.physical_evidence.contracts_v0 import CompatibilityStatusV0


@dataclass(frozen=True)
class PhysicalSourceChainEvidenceV0:
    source_ref: str
    modality: str
    instrument_ref: str
    hardware_chain_ref: str
    configuration_ref: str
    identity_evidence_refs: tuple[str, ...]
    source_hash_refs: tuple[str, ...]
    calibration_ref: str | None = None
    calibration_not_applicable_ref: str | None = None
    time_alignment_evidence_refs: tuple[str, ...] = ()
    frame_alignment_evidence_refs: tuple[str, ...] = ()
    readonly: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not all((
            self.source_ref,
            self.modality,
            self.instrument_ref,
            self.hardware_chain_ref,
            self.configuration_ref,
        )):
            raise ValueError("physical source chain requires source, modality, instrument, hardware chain and config")
        if not self.identity_evidence_refs:
            raise ValueError("physical source chain requires identity evidence refs")
        if not self.source_hash_refs:
            raise ValueError("physical source chain requires source hash refs")
        if not self.readonly:
            raise ValueError("physical source chain evidence must remain readonly")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("physical source chain evidence cannot decide or act")


@dataclass(frozen=True)
class GpsMultiSourceCorroborationV0:
    report_id: str
    primary_gnss_ref: str
    secondary_observation_ref: str
    cross_modal_report_ref: str
    primary_source_chain_ref: str
    secondary_source_chain_ref: str
    p2_live_gnss_verified: bool
    source_independence_proven: bool
    calibration_binding_proven: bool
    temporal_alignment_proven: bool
    spatial_alignment_proven: bool
    multi_source_corroboration_proven: bool
    blockers: tuple[str, ...]
    causal_attribution_proven: bool = False
    physical_truth_proven: bool = False
    readonly: bool = True
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False

    def __post_init__(self) -> None:
        if not all((
            self.report_id,
            self.primary_gnss_ref,
            self.secondary_observation_ref,
            self.cross_modal_report_ref,
        )):
            raise ValueError("P3 corroboration report requires identity and bindings")
        if self.causal_attribution_proven:
            raise ValueError("P3 corroboration cannot prove causal spoofing attribution")
        if self.physical_truth_proven:
            raise ValueError("P3 corroboration cannot self-promote physical truth")
        if self.multi_source_corroboration_proven and self.blockers:
            raise ValueError("proven P3 corroboration cannot retain blockers")
        if not self.readonly or not self.advisory_only:
            raise ValueError("P3 corroboration remains readonly/advisory")
        if self.decision_authority != "KX108_ONLY" or self.allowed_to_decide or self.allowed_to_act:
            raise ValueError("P3 corroboration cannot decide or act")


def _pair_for(
    report: CrossModalCoherenceReportV0,
    left_ref: str,
    right_ref: str,
):
    wanted = {left_ref, right_ref}
    for pair in report.pair_assessments:
        if {pair.left_observation_ref, pair.right_observation_ref} == wanted:
            return pair
    return None


def build_gps_multisource_corroboration_v0(
    *,
    report_id: str,
    primary_gnss: ModalityObservationV0,
    secondary: ModalityObservationV0,
    primary_chain: PhysicalSourceChainEvidenceV0,
    secondary_chain: PhysicalSourceChainEvidenceV0,
    cross_modal_report: CrossModalCoherenceReportV0,
) -> GpsMultiSourceCorroborationV0:
    blockers: list[str] = []

    if primary_gnss.modality.lower() != "gnss":
        blockers.append("PRIMARY_SOURCE_NOT_GNSS")

    p2_live_gnss_verified = (
        primary_gnss.state.get("proof_level") == "REAL_PASSIVE_GNSS"
        and primary_gnss.state.get("live_capture_observed") is True
        and primary_gnss.generated is False
    )
    if not p2_live_gnss_verified:
        blockers.append("P2_REAL_PASSIVE_GNSS_NOT_VERIFIED")

    if secondary.generated:
        blockers.append("GENERATED_SECONDARY_NOT_PHYSICAL_CORROBORATION")

    if primary_chain.source_ref != primary_gnss.source_ref:
        blockers.append("PRIMARY_SOURCE_CHAIN_BINDING_MISMATCH")
    if secondary_chain.source_ref != secondary.source_ref:
        blockers.append("SECONDARY_SOURCE_CHAIN_BINDING_MISMATCH")

    source_independence_proven = all((
        primary_chain.source_ref != secondary_chain.source_ref,
        primary_chain.instrument_ref != secondary_chain.instrument_ref,
        primary_chain.hardware_chain_ref != secondary_chain.hardware_chain_ref,
        bool(primary_chain.identity_evidence_refs),
        bool(secondary_chain.identity_evidence_refs),
        bool(primary_chain.source_hash_refs),
        bool(secondary_chain.source_hash_refs),
    ))
    if not source_independence_proven:
        blockers.append("INDEPENDENT_PHYSICAL_SOURCE_NOT_PROVEN")

    primary_calibration_bound = bool(
        primary_chain.calibration_ref or primary_chain.calibration_not_applicable_ref
    )
    secondary_calibration_bound = bool(
        secondary_chain.calibration_ref or secondary_chain.calibration_not_applicable_ref
    )
    calibration_binding_proven = (
        bool(primary_chain.configuration_ref)
        and bool(secondary_chain.configuration_ref)
        and primary_calibration_bound
        and secondary_calibration_bound
    )
    if not calibration_binding_proven:
        blockers.append("CALIBRATION_OR_JUSTIFICATION_NOT_BOUND")

    if primary_gnss.observation_id not in cross_modal_report.modality_refs:
        blockers.append("PRIMARY_OBSERVATION_NOT_IN_CROSS_MODAL_REPORT")
    if secondary.observation_id not in cross_modal_report.modality_refs:
        blockers.append("SECONDARY_OBSERVATION_NOT_IN_CROSS_MODAL_REPORT")

    pair = _pair_for(
        cross_modal_report,
        primary_gnss.observation_id,
        secondary.observation_id,
    )

    if pair is None:
        temporal_alignment_proven = False
        spatial_alignment_proven = False
        blockers.append("CROSS_MODAL_PAIR_NOT_FOUND")
    else:
        temporal_alignment_proven = (
            pair.temporal == CompatibilityStatusV0.COMPATIBLE
            or bool(primary_chain.time_alignment_evidence_refs)
            or bool(secondary_chain.time_alignment_evidence_refs)
        )
        spatial_alignment_proven = (
            pair.spatial == CompatibilityStatusV0.COMPATIBLE
            or bool(primary_chain.frame_alignment_evidence_refs)
            or bool(secondary_chain.frame_alignment_evidence_refs)
        )
        if pair.independence == CompatibilityStatusV0.COMPATIBLE and not source_independence_proven:
            blockers.append("F20_SOURCE_REF_COMPATIBILITY_NOT_PHYSICAL_INDEPENDENCE")

    if not temporal_alignment_proven:
        blockers.append("TEMPORAL_ALIGNMENT_NOT_PROVEN")
    if not spatial_alignment_proven:
        blockers.append("SPATIAL_ALIGNMENT_NOT_PROVEN")

    if cross_modal_report.generated_present:
        blockers.append("GENERATED_MODALITY_NOT_PHYSICAL_TRUTH")

    blockers = list(dict.fromkeys(blockers))
    proven = (
        p2_live_gnss_verified
        and source_independence_proven
        and calibration_binding_proven
        and temporal_alignment_proven
        and spatial_alignment_proven
        and not secondary.generated
        and not blockers
    )

    return GpsMultiSourceCorroborationV0(
        report_id=report_id,
        primary_gnss_ref=primary_gnss.observation_id,
        secondary_observation_ref=secondary.observation_id,
        cross_modal_report_ref=cross_modal_report.report_id,
        primary_source_chain_ref=primary_chain.hardware_chain_ref,
        secondary_source_chain_ref=secondary_chain.hardware_chain_ref,
        p2_live_gnss_verified=p2_live_gnss_verified,
        source_independence_proven=source_independence_proven,
        calibration_binding_proven=calibration_binding_proven,
        temporal_alignment_proven=temporal_alignment_proven,
        spatial_alignment_proven=spatial_alignment_proven,
        multi_source_corroboration_proven=proven,
        blockers=tuple(blockers),
    )
