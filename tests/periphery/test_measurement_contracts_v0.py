from periphery.measurement.contracts_v0 import (
    InstrumentRefV0,
    MeasurementContextV0,
    SituatedMeasurementV0,
)
from periphery.world_dynamics.contracts_v0 import SpatialFrameRefV0, TimeEnvelopeV0


def test_missing_calibration_must_remain_explicit():
    instrument = InstrumentRefV0(instrument_ref="sensor:1", instrument_kind="imu")
    try:
        MeasurementContextV0(
            phenomenon_ref="motion",
            signal_kind="acceleration",
            unit="m/s2",
            precision=0.01,
            time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
            instrument=instrument,
        )
    except ValueError as exc:
        assert "CALIBRATION_UNKNOWN" in str(exc)
    else:
        raise AssertionError("missing calibration must not be silently accepted")


def test_measurement_preserves_context_and_uncertainty():
    context = MeasurementContextV0(
        phenomenon_ref="motion",
        signal_kind="acceleration",
        unit="m/s2",
        precision=0.01,
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
        instrument=InstrumentRefV0(
            instrument_ref="imu:1",
            instrument_kind="imu",
            calibration_ref="cal:imu:1",
        ),
        spatial_frame=SpatialFrameRefV0(frame_ref="body"),
        environment_ref="env:test",
        measurement_limits=("SATURATION_LIMIT_UNKNOWN",),
        uncertainty=("NOISE_PRESENT",),
        provenance_refs=("source:imu:1",),
    )
    measurement = SituatedMeasurementV0(
        measurement_id="m:1",
        value=9.81,
        context=context,
        source_refs=("source:imu:1",),
        source_hashes=("sha256:abc",),
    )
    assert measurement.context.unit == "m/s2"
    assert measurement.context.spatial_frame.frame_ref == "body"
    assert "NOISE_PRESENT" in measurement.context.uncertainty


def test_provenance_does_not_prove_physical_authenticity():
    context = MeasurementContextV0(
        phenomenon_ref="position",
        signal_kind="gnss",
        unit="m",
        precision=None,
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
        instrument=InstrumentRefV0(
            instrument_ref="gnss:1",
            instrument_kind="gnss",
            calibration_ref="cal:gnss:1",
        ),
    )
    measurement = SituatedMeasurementV0(
        measurement_id="m:2",
        value={"x": 1, "y": 2, "z": 3},
        context=context,
        source_refs=("rinex:file",),
        source_hashes=("sha256:def",),
    )
    assert measurement.physical_authenticity_proven is False


def test_physical_authenticity_requires_evidence():
    context = MeasurementContextV0(
        phenomenon_ref="distance",
        signal_kind="radar",
        unit="m",
        precision=0.1,
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
        instrument=InstrumentRefV0(
            instrument_ref="radar:1",
            instrument_kind="radar",
            calibration_ref="cal:radar:1",
        ),
    )
    try:
        SituatedMeasurementV0(
            measurement_id="m:3",
            value=42.0,
            context=context,
            source_refs=("source:radar:1",),
            physical_authenticity_proven=True,
        )
    except ValueError as exc:
        assert "requires explicit evidence refs" in str(exc)
    else:
        raise AssertionError("physical authenticity without evidence must fail closed")


def test_measurement_is_non_sovereign():
    context = MeasurementContextV0(
        phenomenon_ref="temperature",
        signal_kind="thermal",
        unit="K",
        precision=0.5,
        time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
        instrument=InstrumentRefV0(
            instrument_ref="thermo:1",
            instrument_kind="thermometer",
            calibration_ref="cal:thermo:1",
        ),
    )
    measurement = SituatedMeasurementV0(
        measurement_id="m:4",
        value=293.15,
        context=context,
        source_refs=("source:thermo:1",),
    )
    assert measurement.decision_authority == "KX108_ONLY"
    assert measurement.allowed_to_decide is False
    assert measurement.allowed_to_act is False
