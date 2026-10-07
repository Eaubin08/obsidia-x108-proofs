"""F24 hardening tests for claim and authority boundaries left open in F15/F16/F18."""
from periphery.measurement.contracts_v0 import InstrumentRefV0, MeasurementContextV0, SituatedMeasurementV0
from periphery.physical_evidence.contracts_v0 import CompatibilityStatusV0, assess_physical_compatibility_v0
from periphery.physical_signal.contracts_v0 import PhysicalSignalEventV0
from periphery.science_constraints.contracts_v0 import (
    ConstraintAssessmentV0,
    ConstraintStatusV0,
    PossibilityStatusV0,
    ScientificInvariantV0,
)
from periphery.vision.contracts_v0 import (
    CaptureContextV0,
    ImageAssetRefV0,
    RealImageObservationV0,
    VisualPrimitiveV0,
    real_image_to_modality_observation_v0,
)
from periphery.world_dynamics.contracts_v0 import SpatialFrameRefV0, TimeEnvelopeV0


def _event(event_id: str, source: str):
    measurement = SituatedMeasurementV0(
        measurement_id=f"m:{event_id}",
        value=1.0,
        context=MeasurementContextV0(
            phenomenon_ref="vehicle:1",
            signal_kind="position",
            unit="m",
            precision=0.5,
            time=TimeEnvelopeV0(observed_at="2026-10-07T00:00:00Z"),
            instrument=InstrumentRefV0(
                instrument_ref=f"instrument:{event_id}",
                instrument_kind="sensor",
                calibration_ref=f"cal:{event_id}",
            ),
            spatial_frame=SpatialFrameRefV0(frame_ref="ECEF"),
        ),
        source_refs=(source,),
        source_hashes=(f"hash:{source}",),
        evidence_refs=(f"evidence:{event_id}",),
    )
    return PhysicalSignalEventV0(event_id=event_id, measurement=measurement, signal_family="TEST")


def test_f15_single_source_never_claims_source_independence():
    result = assess_physical_compatibility_v0((_event("e1", "source:1"),))
    assert result.independence == CompatibilityStatusV0.UNKNOWN
    assert "SOURCE_INDEPENDENCE_NOT_PROVEN" in result.reasons


def test_f16_preserves_capture_governance_and_visual_primitive_detail():
    primitive = VisualPrimitiveV0(
        primitive_id="p1",
        primitive_kind="object",
        label="vehicle",
        confidence=0.8,
        geometry_ref="geometry:1",
        mask_ref="mask:1",
        depth_ref="depth:1",
        motion_ref="motion:1",
        text_value="ABC",
        feature_refs=("feature:1",),
        evidence_refs=("evidence:primitive:1",),
    )
    image = RealImageObservationV0(
        observation_id="img:1",
        observed_at="2026-10-07T00:00:00Z",
        asset=ImageAssetRefV0(asset_ref="asset:image:1", asset_hash="sha256:image"),
        source_ref="camera:1",
        capture_context=CaptureContextV0(
            device_ref="device:1",
            optics_ref="optics:1",
            author_ref="author:1",
            application_ref="app:1",
            consent_ref="consent:1",
        ),
        primitives=(primitive,),
    )
    modality = real_image_to_modality_observation_v0(image)
    assert modality.state["author_ref"] == "author:1"
    assert modality.state["application_ref"] == "app:1"
    assert modality.state["consent_ref"] == "consent:1"
    encoded = modality.state["primitives"][0]
    assert encoded["mask_ref"] == "mask:1"
    assert encoded["depth_ref"] == "depth:1"
    assert encoded["motion_ref"] == "motion:1"
    assert encoded["text_value"] == "ABC"
    assert encoded["evidence_refs"] == ["evidence:primitive:1"]


def test_f18_empirical_invariant_can_be_evidence_backed_without_fake_formal_proof():
    invariant = ScientificInvariantV0(
        invariant_id="inv:empirical",
        statement="empirical regularity within declared scope",
        model_ref="model:empirical",
        evidence_refs=("evidence:dataset:1",),
    )
    assert invariant.proof_refs == ()
    assert invariant.evidence_refs == ("evidence:dataset:1",)
    assert invariant.assumed is False


def test_f18_possible_requires_bounded_evidence_and_model_scope():
    try:
        ConstraintAssessmentV0(
            assessment_id="a:possible-no-evidence",
            constraint_ref="constraint:1",
            status=ConstraintStatusV0.UNKNOWN,
            possibility=PossibilityStatusV0.POSSIBLE,
            model_ref="model:1",
        )
    except ValueError as exc:
        assert "resolved possibility requires explicit evidence_refs" in str(exc)
    else:
        raise AssertionError("POSSIBLE without evidence must fail closed")

    try:
        ConstraintAssessmentV0(
            assessment_id="a:possible-no-model",
            constraint_ref="constraint:1",
            status=ConstraintStatusV0.UNKNOWN,
            possibility=PossibilityStatusV0.POSSIBLE,
            evidence_refs=("evidence:1",),
        )
    except ValueError as exc:
        assert "requires explicit model_ref scope" in str(exc)
    else:
        raise AssertionError("POSSIBLE without model scope must fail closed")


def test_f18_satisfied_and_impossible_cannot_coexist():
    try:
        ConstraintAssessmentV0(
            assessment_id="a:contradictory",
            constraint_ref="constraint:1",
            status=ConstraintStatusV0.SATISFIED,
            possibility=PossibilityStatusV0.IMPOSSIBLE,
            evidence_refs=("evidence:1",),
            model_ref="model:1",
        )
    except ValueError as exc:
        assert "cannot simultaneously be IMPOSSIBLE" in str(exc)
    else:
        raise AssertionError("SATISFIED + IMPOSSIBLE must fail closed")
