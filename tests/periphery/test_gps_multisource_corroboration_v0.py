from periphery.cross_modal.contracts_v0 import build_cross_modal_coherence_report_v0
from periphery.gps_physical.corroboration_v0 import (
    PhysicalSourceChainEvidenceV0,
    build_gps_multisource_corroboration_v0,
)
from periphery.multimodal.bridge_v0 import ModalityObservationV0


def _obs(
    oid: str,
    modality: str,
    source: str,
    *,
    proof_level: str | None = None,
    live_capture_observed: bool | None = None,
    generated: bool = False,
):
    state = {"unit": "m/s", "value": 1.0}
    if proof_level is not None:
        state["proof_level"] = proof_level
    if live_capture_observed is not None:
        state["live_capture_observed"] = live_capture_observed
    return ModalityObservationV0(
        observation_id=oid,
        modality=modality,
        observed_at="2026-10-07T10:00:00Z",
        source_ref=source,
        source_hash=f"hash:{source}",
        state=state,
        evidence_refs=(f"evidence:{oid}",),
        frame_ref="frame:vehicle",
        generated=generated,
    )


def _chain(
    source: str,
    modality: str,
    instrument: str,
    hardware: str,
    *,
    calibration: str | None = "calibration:1",
    calibration_na: str | None = None,
):
    return PhysicalSourceChainEvidenceV0(
        source_ref=source,
        modality=modality,
        instrument_ref=instrument,
        hardware_chain_ref=hardware,
        configuration_ref=f"config:{instrument}",
        calibration_ref=calibration,
        calibration_not_applicable_ref=calibration_na,
        identity_evidence_refs=(f"identity:{instrument}",),
        source_hash_refs=(f"hash:{source}",),
    )


def _report(primary, secondary):
    return build_cross_modal_coherence_report_v0(
        report_id="cross-modal:gps-imu",
        observations=(primary, secondary),
    )


def test_p3_full_explicit_independent_gnss_imu_chain_can_prove_corroboration_without_authority():
    gnss = _obs(
        "gnss-live-1",
        "gnss",
        "receiver:gnss:1",
        proof_level="REAL_PASSIVE_GNSS",
        live_capture_observed=True,
    )
    imu = _obs("imu-live-1", "imu", "receiver:imu:1")
    result = build_gps_multisource_corroboration_v0(
        report_id="p3:1",
        primary_gnss=gnss,
        secondary=imu,
        primary_chain=_chain("receiver:gnss:1", "gnss", "gnss-device:1", "chain:gnss"),
        secondary_chain=_chain("receiver:imu:1", "imu", "imu-device:1", "chain:imu"),
        cross_modal_report=_report(gnss, imu),
    )

    assert result.p2_live_gnss_verified is True
    assert result.source_independence_proven is True
    assert result.calibration_binding_proven is True
    assert result.temporal_alignment_proven is True
    assert result.spatial_alignment_proven is True
    assert result.multi_source_corroboration_proven is True
    assert result.blockers == ()
    assert result.causal_attribution_proven is False
    assert result.physical_truth_proven is False
    assert result.decision_authority == "KX108_ONLY"
    assert result.allowed_to_decide is False
    assert result.allowed_to_act is False


def test_p3_distinct_source_refs_on_same_hardware_chain_do_not_prove_independence():
    gnss = _obs(
        "gnss-live-1",
        "gnss",
        "source:a",
        proof_level="REAL_PASSIVE_GNSS",
        live_capture_observed=True,
    )
    imu = _obs("imu-live-1", "imu", "source:b")
    result = build_gps_multisource_corroboration_v0(
        report_id="p3:same-hardware",
        primary_gnss=gnss,
        secondary=imu,
        primary_chain=_chain("source:a", "gnss", "instrument:a", "shared-chain"),
        secondary_chain=_chain("source:b", "imu", "instrument:b", "shared-chain"),
        cross_modal_report=_report(gnss, imu),
    )

    assert result.source_independence_proven is False
    assert result.multi_source_corroboration_proven is False
    assert "INDEPENDENT_PHYSICAL_SOURCE_NOT_PROVEN" in result.blockers
    assert "F20_SOURCE_REF_COMPATIBILITY_NOT_PHYSICAL_INDEPENDENCE" in result.blockers


def test_p3_cannot_start_from_recorded_or_unverified_gnss_primary():
    gnss = _obs(
        "gnss-recorded-1",
        "gnss",
        "receiver:gnss:1",
        proof_level="RECORDED_REAL_GNSS",
        live_capture_observed=False,
    )
    imu = _obs("imu-live-1", "imu", "receiver:imu:1")
    result = build_gps_multisource_corroboration_v0(
        report_id="p3:no-p2",
        primary_gnss=gnss,
        secondary=imu,
        primary_chain=_chain("receiver:gnss:1", "gnss", "gnss-device:1", "chain:gnss"),
        secondary_chain=_chain("receiver:imu:1", "imu", "imu-device:1", "chain:imu"),
        cross_modal_report=_report(gnss, imu),
    )

    assert result.p2_live_gnss_verified is False
    assert result.multi_source_corroboration_proven is False
    assert "P2_REAL_PASSIVE_GNSS_NOT_VERIFIED" in result.blockers


def test_p3_missing_calibration_or_explicit_not_applicable_justification_blocks():
    gnss = _obs(
        "gnss-live-1",
        "gnss",
        "receiver:gnss:1",
        proof_level="REAL_PASSIVE_GNSS",
        live_capture_observed=True,
    )
    imu = _obs("imu-live-1", "imu", "receiver:imu:1")
    result = build_gps_multisource_corroboration_v0(
        report_id="p3:no-calibration",
        primary_gnss=gnss,
        secondary=imu,
        primary_chain=_chain(
            "receiver:gnss:1",
            "gnss",
            "gnss-device:1",
            "chain:gnss",
            calibration=None,
            calibration_na="calibration-na:gnss-config-bound",
        ),
        secondary_chain=_chain(
            "receiver:imu:1",
            "imu",
            "imu-device:1",
            "chain:imu",
            calibration=None,
            calibration_na=None,
        ),
        cross_modal_report=_report(gnss, imu),
    )

    assert result.calibration_binding_proven is False
    assert result.multi_source_corroboration_proven is False
    assert "CALIBRATION_OR_JUSTIFICATION_NOT_BOUND" in result.blockers


def test_p3_generated_secondary_never_counts_as_physical_corroboration():
    gnss = _obs(
        "gnss-live-1",
        "gnss",
        "receiver:gnss:1",
        proof_level="REAL_PASSIVE_GNSS",
        live_capture_observed=True,
    )
    generated_imu = _obs("imu-generated-1", "imu", "generator:imu:1", generated=True)
    result = build_gps_multisource_corroboration_v0(
        report_id="p3:generated",
        primary_gnss=gnss,
        secondary=generated_imu,
        primary_chain=_chain("receiver:gnss:1", "gnss", "gnss-device:1", "chain:gnss"),
        secondary_chain=_chain("generator:imu:1", "imu", "generator:1", "chain:generator"),
        cross_modal_report=_report(gnss, generated_imu),
    )

    assert result.multi_source_corroboration_proven is False
    assert "GENERATED_SECONDARY_NOT_PHYSICAL_CORROBORATION" in result.blockers
    assert "GENERATED_MODALITY_NOT_PHYSICAL_TRUTH" in result.blockers
