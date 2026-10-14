from dataclasses import FrozenInstanceError

import pytest

from periphery.governed_world.bridge_v0 import governance_payload_to_aggregate
from periphery.mmonde.contracts_v0 import WorldObservationV0
from periphery.multimodal.bridge_v0 import ModalityObservationV0, modality_to_world_observation
from periphery.udip.contracts_v0 import GovernancePayloadV0


def _payload(**overrides):
    values = dict(
        domain_id="meta",
        domain_state_ref="meta:world:now",
        world_state_ref="world",
        evidence_refs=("evidence:direct",),
        provenance_refs=("source:origin",),
    )
    values.update(overrides)
    return GovernancePayloadV0(**values)


def test_provenance_is_not_promoted_to_evidence():
    aggregate = governance_payload_to_aggregate(_payload(), confidence=0.9)
    assert aggregate.evidence_refs == ["evidence:direct"]
    assert aggregate.extra_metrics["provenance_refs"] == ["source:origin"]
    assert "provenance:source:origin" not in aggregate.evidence_refs


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_governed_world_rejects_out_of_range_confidence(confidence):
    with pytest.raises(ValueError, match="confidence must be between"):
        governance_payload_to_aggregate(_payload(), confidence=confidence)


def test_multimodal_canonical_fields_cannot_be_overridden_by_state():
    item = ModalityObservationV0(
        observation_id="camera-1",
        modality="image",
        observed_at="2026-10-07T00:00:00Z",
        source_ref="camera:1",
        source_hash="hash",
        state={"modality": "forged", "generated": False, "frame_ref": "forged", "latency_ms": 999},
        latency_ms=12.5,
        frame_ref="frame:canonical",
        generated=True,
    )
    world = modality_to_world_observation(item)
    assert world.state["modality"] == "image"
    assert world.state["generated"] is True
    assert world.state["frame_ref"] == "frame:canonical"
    assert world.state["latency_ms"] == 12.5
    assert "FRAME_UNKNOWN" not in world.uncertainty
    assert "LATENCY_UNKNOWN" not in world.uncertainty
