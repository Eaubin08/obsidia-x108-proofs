from periphery.cross_modal.contracts_v0 import (
    CrossModalCoherenceReportV0,
    assess_cross_modal_pair_v0,
    build_cross_modal_coherence_report_v0,
)
from periphery.multimodal.bridge_v0 import ModalityObservationV0
from periphery.physical_evidence.contracts_v0 import CompatibilityStatusV0


def _obs(
    oid: str,
    modality: str,
    source: str,
    *,
    observed_at: str = "2026-10-07T00:00:00Z",
    frame_ref: str | None = "frame:1",
    unit: str | None = "m",
    generated: bool = False,
):
    state = {"value": 1.0}
    if unit is not None:
        state["unit"] = unit
    return ModalityObservationV0(
        observation_id=oid,
        modality=modality,
        observed_at=observed_at,
        source_ref=source,
        source_hash=f"hash:{oid}",
        state=state,
        evidence_refs=(f"evidence:{oid}",),
        frame_ref=frame_ref,
        generated=generated,
    )


def test_same_time_frame_unit_and_distinct_sources_are_compatible_except_causality():
    left = _obs("o1", "image", "camera:1")
    right = _obs("o2", "gnss", "receiver:1")
    pair = assess_cross_modal_pair_v0(left, right)
    assert pair.temporal == CompatibilityStatusV0.COMPATIBLE
    assert pair.spatial == CompatibilityStatusV0.COMPATIBLE
    assert pair.metric == CompatibilityStatusV0.COMPATIBLE
    assert pair.independence == CompatibilityStatusV0.COMPATIBLE
    assert pair.causal == CompatibilityStatusV0.UNKNOWN
    assert "CAUSAL_COMPATIBILITY_NOT_PROVEN" in pair.reasons


def test_generated_channel_never_establishes_physical_truth():
    left = _obs("o1", "image", "generator:1", generated=True)
    right = _obs("o2", "gnss", "receiver:1")
    pair = assess_cross_modal_pair_v0(left, right)
    assert "GENERATED_MODALITY_NOT_PHYSICAL_TRUTH" in pair.reasons


def test_different_frames_require_transform_proof():
    left = _obs("o1", "image", "camera:1", frame_ref="camera")
    right = _obs("o2", "gnss", "receiver:1", frame_ref="ECEF")
    pair = assess_cross_modal_pair_v0(left, right)
    assert pair.spatial == CompatibilityStatusV0.UNKNOWN
    assert "FRAME_TRANSFORM_NOT_PROVEN" in pair.reasons


def test_same_source_is_not_counted_as_independent():
    left = _obs("o1", "image", "shared-source")
    right = _obs("o2", "imu", "shared-source")
    pair = assess_cross_modal_pair_v0(left, right)
    assert pair.independence == CompatibilityStatusV0.UNKNOWN
    assert "SOURCE_INDEPENDENCE_NOT_PROVEN" in pair.reasons


def test_metric_mismatch_does_not_fake_compatibility():
    left = _obs("o1", "image", "camera:1", unit="m")
    right = _obs("o2", "temperature", "sensor:1", unit="K")
    pair = assess_cross_modal_pair_v0(left, right)
    assert pair.metric == CompatibilityStatusV0.UNKNOWN
    assert "METRIC_TRANSFORM_NOT_PROVEN" in pair.reasons


def test_report_preserves_evidence_provenance_and_remains_non_sovereign():
    observations = (
        _obs("o1", "image", "camera:1"),
        _obs("o2", "gnss", "receiver:1"),
        _obs("o3", "imu", "imu:1"),
    )
    report = build_cross_modal_coherence_report_v0(
        report_id="cross-modal:1",
        observations=observations,
    )
    assert isinstance(report, CrossModalCoherenceReportV0)
    assert len(report.pair_assessments) == 3
    assert set(report.provenance_refs) == {"camera:1", "receiver:1", "imu:1"}
    assert set(report.evidence_refs) == {"evidence:o1", "evidence:o2", "evidence:o3"}
    assert report.physical_coherence_proven is False
    assert report.decision_authority == "KX108_ONLY"
    assert report.allowed_to_decide is False
    assert report.allowed_to_act is False


def test_report_cannot_self_promote_physical_coherence():
    pair = assess_cross_modal_pair_v0(
        _obs("o1", "image", "camera:1"),
        _obs("o2", "gnss", "receiver:1"),
    )
    try:
        CrossModalCoherenceReportV0(
            report_id="bad",
            modality_refs=("o1", "o2"),
            pair_assessments=(pair,),
            physical_coherence_proven=True,
        )
    except ValueError as exc:
        assert "cannot self-promote" in str(exc)
    else:
        raise AssertionError("cross-modal report must not self-promote physical coherence")
