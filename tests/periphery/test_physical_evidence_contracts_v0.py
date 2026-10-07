from periphery.measurement.contracts_v0 import InstrumentRefV0, MeasurementContextV0, SituatedMeasurementV0
from periphery.physical_evidence.contracts_v0 import (
    CompatibilityStatusV0,
    assess_physical_compatibility_v0,
    build_replayable_physical_evidence_candidate_v0,
)
from periphery.physical_signal.contracts_v0 import (
    PhysicalSignalEventV0,
    PhysicalSignalReportV0,
    build_world_state_candidate_v0,
)
from periphery.world_dynamics.contracts_v0 import SpatialFrameRefV0, TimeEnvelopeV0


def _event(event_id: str, source: str, *, observed_at: str = "2026-10-07T00:00:00Z", frame: str = "ECEF", unit: str = "m"):
    measurement = SituatedMeasurementV0(
        measurement_id=f"m:{event_id}",
        value=1.0,
        context=MeasurementContextV0(
            phenomenon_ref="vehicle:1",
            signal_kind="position",
            unit=unit,
            precision=0.5,
            time=TimeEnvelopeV0(observed_at=observed_at),
            instrument=InstrumentRefV0(
                instrument_ref=f"instrument:{event_id}",
                instrument_kind="sensor",
                calibration_ref=f"cal:{event_id}",
            ),
            spatial_frame=SpatialFrameRefV0(frame_ref=frame),
        ),
        source_refs=(source,),
        evidence_refs=(f"evidence:{event_id}",),
    )
    return PhysicalSignalEventV0(event_id=event_id, measurement=measurement, signal_family="TEST")


def test_same_time_frame_unit_and_distinct_sources_are_compatible_except_causality():
    e1 = _event("e1", "s1")
    e2 = _event("e2", "s2")
    result = assess_physical_compatibility_v0((e1, e2))
    assert result.temporal == CompatibilityStatusV0.COMPATIBLE
    assert result.spatial == CompatibilityStatusV0.COMPATIBLE
    assert result.metric == CompatibilityStatusV0.COMPATIBLE
    assert result.independence == CompatibilityStatusV0.COMPATIBLE
    assert result.causal == CompatibilityStatusV0.UNKNOWN
    assert "CAUSAL_COMPATIBILITY_NOT_PROVEN" in result.reasons


def test_different_times_do_not_create_false_temporal_compatibility():
    e1 = _event("e1", "s1", observed_at="2026-10-07T00:00:00Z")
    e2 = _event("e2", "s2", observed_at="2026-10-07T00:00:01Z")
    result = assess_physical_compatibility_v0((e1, e2))
    assert result.temporal == CompatibilityStatusV0.UNKNOWN
    assert "TEMPORAL_ALIGNMENT_NOT_PROVEN" in result.reasons


def test_different_frames_require_transform_proof():
    e1 = _event("e1", "s1", frame="ECEF")
    e2 = _event("e2", "s2", frame="ENU")
    result = assess_physical_compatibility_v0((e1, e2))
    assert result.spatial == CompatibilityStatusV0.UNKNOWN
    assert "FRAME_TRANSFORM_NOT_PROVEN" in result.reasons


def test_same_source_does_not_count_as_independent_evidence():
    e1 = _event("e1", "same-source")
    e2 = _event("e2", "same-source")
    result = assess_physical_compatibility_v0((e1, e2))
    assert result.independence == CompatibilityStatusV0.UNKNOWN
    assert "SOURCE_INDEPENDENCE_NOT_PROVEN" in result.reasons


def test_replayable_candidate_binds_report_world_and_events_without_truth_promotion():
    e1 = _event("e1", "s1")
    e2 = _event("e2", "s2")
    report = PhysicalSignalReportV0(
        report_id="report:1",
        event_refs=("e1", "e2"),
        evidence_refs=("report-evidence",),
        provenance_refs=("s1", "s2"),
    )
    world = build_world_state_candidate_v0(
        candidate_id="world:1",
        report=report,
        events=(e1, e2),
        valid_at="2026-10-07T00:00:00Z",
    )
    packet = build_replayable_physical_evidence_candidate_v0(
        evidence_id="physical-evidence:1",
        report=report,
        world_candidate=world,
        events=(e1, e2),
        replay_refs=("replay:1",),
    )
    assert packet.report_ref == "report:1"
    assert packet.world_candidate_ref == "world:1"
    assert packet.physical_authenticity_proven is False
    assert packet.allowed_to_decide is False
    assert packet.allowed_to_act is False


def test_world_candidate_report_binding_mismatch_fails_closed():
    e1 = _event("e1", "s1")
    report1 = PhysicalSignalReportV0(report_id="report:1", event_refs=("e1",))
    report2 = PhysicalSignalReportV0(report_id="report:2", event_refs=("e1",))
    world = build_world_state_candidate_v0(
        candidate_id="world:1",
        report=report1,
        events=(e1,),
        valid_at="2026-10-07T00:00:00Z",
    )
    try:
        build_replayable_physical_evidence_candidate_v0(
            evidence_id="bad",
            report=report2,
            world_candidate=world,
            events=(e1,),
        )
    except ValueError as exc:
        assert "binding mismatch" in str(exc)
    else:
        raise AssertionError("mismatched report/world candidate must fail closed")
