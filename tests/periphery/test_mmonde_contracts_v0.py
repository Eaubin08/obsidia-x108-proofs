from __future__ import annotations

import pytest

from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0


def observation(**overrides):
    data = dict(
        observation_id="obs-1",
        observed_at="2026-10-06T12:00:00Z",
        source_refs=("sensor-a",),
        entity_ref="entity-1",
        state={"status": "observed"},
        uncertainty=("source_not_yet_authenticated",),
    )
    data.update(overrides)
    return WorldObservationV0(**data)


def test_observation_is_representation_not_authority():
    obs = observation()
    assert obs.readonly is True
    assert obs.representation_only is True
    assert obs.decision_authority == "KX108_ONLY"
    assert obs.allowed_to_decide is False
    assert obs.allowed_to_act is False


def test_temporal_observation_does_not_imply_causality():
    obs = observation()
    assert obs.causal_status == "UNKNOWN"


def test_causal_proven_requires_evidence():
    with pytest.raises(ValueError, match="evidence_refs"):
        observation(causal_status="CAUSAL_PROVEN")


def test_world_state_is_not_memory_or_cognition():
    ws = WorldStateV0(
        world_state_id="world-1",
        valid_at="2026-10-06T12:00:00Z",
        observations=(observation(),),
    )
    assert ws.memory_object is False
    assert ws.cognition_object is False
    assert ws.allowed_to_decide is False
    assert ws.allowed_to_act is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"decision_authority": "MMONDE"},
        {"allowed_to_decide": True},
        {"allowed_to_act": True},
    ],
)
def test_observation_rejects_sovereignty(kwargs):
    with pytest.raises(ValueError):
        observation(**kwargs)
