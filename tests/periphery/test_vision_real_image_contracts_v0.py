from periphery.vision.contracts_v0 import (
    CandidateInterpretationV0,
    CaptureContextV0,
    ImageAssetRefV0,
    ImageIntegrityReportV0,
    RealImageObservationV0,
    VisualPrimitiveV0,
    real_image_to_modality_observation_v0,
    real_image_to_world_observation_v0,
)


def _image(**kwargs):
    base = dict(
        observation_id="img:1",
        observed_at="2026-10-07T00:00:00Z",
        asset=ImageAssetRefV0(asset_ref="asset:image:1", asset_hash="sha256:abc"),
        source_ref="camera:1",
        capture_context=CaptureContextV0(device_ref="camera-device:1", optics_ref="lens:1"),
    )
    base.update(kwargs)
    return RealImageObservationV0(**base)


def test_real_image_cannot_be_generated():
    try:
        _image(generated=True)
    except ValueError as exc:
        assert "cannot represent generated imagery" in str(exc)
    else:
        raise AssertionError("generated image must not enter real-image contract")


def test_visual_primitive_confidence_is_bounded():
    try:
        VisualPrimitiveV0(
            primitive_id="p1",
            primitive_kind="object",
            confidence=1.2,
        )
    except ValueError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("invalid confidence must fail closed")


def test_generated_hypothesis_cannot_be_observed_fact():
    try:
        CandidateInterpretationV0(
            interpretation_id="i1",
            claim="hidden object exists",
            observed_fact=True,
            generated_hypothesis=True,
        )
    except ValueError as exc:
        assert "cannot simultaneously" in str(exc)
    else:
        raise AssertionError("generated hypothesis must remain distinct from observation")


def test_integrity_proven_requires_physical_compatibility_refs():
    try:
        ImageIntegrityReportV0(integrity_proven=True)
    except ValueError as exc:
        assert "requires physical compatibility evidence refs" in str(exc)
    else:
        raise AssertionError("image integrity cannot self-promote without physical compatibility evidence")


def test_real_image_bridge_preserves_asset_context_and_unknowns():
    primitive = VisualPrimitiveV0(
        primitive_id="p1",
        primitive_kind="object",
        label="vehicle",
        confidence=0.8,
        depth_ref="depth:1",
        motion_ref="motion:1",
    )
    interpretation = CandidateInterpretationV0(
        interpretation_id="i1",
        claim="candidate vehicle",
        supporting_primitive_refs=("p1",),
        confidence=0.7,
    )
    image = _image(
        primitives=(primitive,),
        candidate_interpretations=(interpretation,),
        physical_signal_refs=("physical-evidence:1",),
        prior_state_refs=("state:previous",),
        integrity=ImageIntegrityReportV0(
            uncertainty=("LOW_LIGHT",),
            contradictions=("DEPTH_MOTION_MISMATCH",),
        ),
    )
    modality = real_image_to_modality_observation_v0(image)
    assert modality.modality == "image"
    assert modality.generated is False
    assert modality.causal_status == "UNKNOWN"
    assert "LOW_LIGHT" in modality.uncertainty
    assert "FRAME_UNKNOWN" in modality.uncertainty
    assert "LATENCY_UNKNOWN" in modality.uncertainty
    assert "DEPTH_MOTION_MISMATCH" in modality.contradictions
    assert modality.state["asset_hash"] == "sha256:abc"
    assert modality.state["primitive_refs"] == ["p1"]


def test_real_image_to_world_observation_never_claims_causality_or_authority():
    image = _image(frame_ref="camera_frame", latency_ms=12.0)
    world = real_image_to_world_observation_v0(image)
    assert world.causal_status == "UNKNOWN"
    assert world.readonly is True
    assert world.representation_only is True
    assert world.decision_authority == "KX108_ONLY"
    assert world.allowed_to_decide is False
    assert world.allowed_to_act is False
    assert world.state["generated"] is False
