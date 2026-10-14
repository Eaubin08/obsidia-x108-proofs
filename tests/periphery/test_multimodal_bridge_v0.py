from __future__ import annotations

import pytest

from periphery.multimodal.bridge_v0 import ModalityObservationV0, fuse_modalities_v0


def obs(modality: str, **kw):
    data = dict(
        observation_id=f"obs-{modality}",
        modality=modality,
        observed_at="2026-10-06T18:00:00Z",
        source_ref=f"source-{modality}",
        source_hash=f"hash-{modality}",
        state={"value": 1},
        latency_ms=20.0,
        frame_ref="frame-a",
    )
    data.update(kw)
    return ModalityObservationV0(**data)


def test_modalities_keep_independent_provenance():
    world = fuse_modalities_v0(obs("image"), obs("audio"), world_state_id="world-mm-1", valid_at="2026-10-06T18:00:00Z")
    assert world.provenance_refs == ("source-image", "source-audio")
    assert tuple(o.source_refs[0] for o in world.observations) == ("source-image", "source-audio")


def test_missing_clock_or_frame_properties_remain_unknown():
    world = fuse_modalities_v0(obs("video", latency_ms=None, frame_ref=None), world_state_id="world-mm-2", valid_at="t")
    assert "LATENCY_UNKNOWN" in world.unknowns
    assert "FRAME_UNKNOWN" in world.unknowns


def test_generated_output_is_not_promoted_to_truth():
    world = fuse_modalities_v0(obs("image", generated=True), world_state_id="world-mm-3", valid_at="t")
    assert "GENERATED_OUTPUT_NOT_TRUTH" in world.risk_flags
    assert world.observations[0].state["generated"] is True
    assert world.candidate_reality is True


def test_generated_content_cannot_prove_physical_causality():
    with pytest.raises(ValueError):
        obs("image", generated=True, causal_status="CAUSAL_PROVEN")


def test_multimodal_fusion_has_no_decision_or_action_authority():
    world = fuse_modalities_v0(obs("text"), obs("audio"), world_state_id="world-mm-4", valid_at="t")
    assert world.allowed_to_decide is False
    assert world.allowed_to_act is False
    assert all(o.allowed_to_decide is False and o.allowed_to_act is False for o in world.observations)
