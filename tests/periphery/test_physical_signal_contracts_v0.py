from periphery.measurement.contracts_v0 import InstrumentRefV0, MeasurementContextV0, SituatedMeasurementV0
from periphery.physical_signal.contracts_v0 import (
    PhysicalRiskHintV0,
    PhysicalSignalEventV0,
    PhysicalSignalReportV0,
    SignalContradictionV0,
    WorldStateCandidateV0,
    build_world_state_candidate_v0,
)
from periphery.world_dynamics.contracts_v0 import SpatialFrameRefV0, TimeEnvelopeV0


def _measurement(mid: str, value: object, *, source: str) -> SituatedMeasurementV0:
    return SituatedMeasurementV0(
        measurement_id=mid,
        value=value,
        context=MeasurementContextV0(
            phenomenon_ref="vehicle:1",
            signal_kind="position",
            unit="m",
            precision=0.5,
            time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
            instrument=InstrumentRefV0(
                instrument_ref=f"instrument:{mid}",
                instrument_kind="gnss",
                calibration_ref=f"cal:{mid}",
            ),
            spatial_frame=SpatialFrameRefV0(frame_ref="ECEF"),
        ),
        source_refs=(source,),
    )


def test_physical_signal_event_is_non_sovereign():
    event = PhysicalSignalEventV0(event_id="e1", measurement=_measurement("m1", 1.0, source="s1"), signal_family="GNSS")
    assert event.decision_authority == "KX108_ONLY"
    assert event.allowed_to_decide is False
    assert event.allowed_to_act is False


def test_signal_contradiction_requires_multiple_events():
    try:
        SignalContradictionV0(
            contradiction_id="c1",
            event_refs=("e1",),
            contradiction_kind="POSITION_MISMATCH",
            detail="single event cannot establish inter-signal contradiction",
        )
    except ValueError as exc:
        assert "at least two event refs" in str(exc)
    else:
        raise AssertionError("single-event contradiction must fail")


def test_risk_hint_is_advisory_only():
    hint = PhysicalRiskHintV0(
        risk_code="PHYSICAL_INCONSISTENCY",
        source_event_refs=("e1", "e2"),
        detail="candidate inconsistency",
    )
    assert hint.advisory_only is True
    assert hint.allowed_to_decide is False
    assert hint.allowed_to_act is False


def test_report_provenance_does_not_prove_authenticity():
    report = PhysicalSignalReportV0(
        report_id="r1",
        event_refs=("e1",),
        provenance_refs=("source:real-file",),
    )
    assert report.physical_authenticity_proven is False


def test_build_world_state_candidate_preserves_contradictions_and_risks():
    e1 = PhysicalSignalEventV0(event_id="e1", measurement=_measurement("m1", 1.0, source="s1"), signal_family="GNSS")
    e2 = PhysicalSignalEventV0(event_id="e2", measurement=_measurement("m2", 2.0, source="s2"), signal_family="IMU")
    contradiction = SignalContradictionV0(
        contradiction_id="c1",
        event_refs=("e1", "e2"),
        contradiction_kind="POSITION_MISMATCH",
        detail="GNSS and inertial candidate paths disagree",
        evidence_refs=("ev:c1",),
    )
    hint = PhysicalRiskHintV0(
        risk_code="CROSS_SOURCE_INCONSISTENCY",
        source_event_refs=("e1", "e2"),
        detail="hold for domain review",
    )
    report = PhysicalSignalReportV0(
        report_id="r1",
        event_refs=("e1", "e2"),
        contradictions=(contradiction,),
        risk_hints=(hint,),
        provenance_refs=("s1", "s2"),
        evidence_refs=("ev:c1",),
    )
    candidate = build_world_state_candidate_v0(
        candidate_id="candidate:1",
        report=report,
        events=(e1, e2),
        valid_at="2026-10-07T00:00:00Z",
        confidence=0.6,
    )
    assert isinstance(candidate, WorldStateCandidateV0)
    assert candidate.world_state.candidate_reality is True
    assert "POSITION_MISMATCH" in candidate.world_state.contradictions
    assert "CROSS_SOURCE_INCONSISTENCY" in candidate.world_state.risk_flags
    assert candidate.allowed_to_decide is False
    assert candidate.allowed_to_act is False


def test_report_cannot_reference_missing_event():
    e1 = PhysicalSignalEventV0(event_id="e1", measurement=_measurement("m1", 1.0, source="s1"), signal_family="GNSS")
    report = PhysicalSignalReportV0(report_id="r1", event_refs=("e1", "e2"))
    try:
        build_world_state_candidate_v0(
            candidate_id="candidate:bad",
            report=report,
            events=(e1,),
            valid_at="2026-10-07T00:00:00Z",
        )
    except ValueError as exc:
        assert "unknown physical events" in str(exc)
    else:
        raise AssertionError("unknown physical event ref must fail closed")
