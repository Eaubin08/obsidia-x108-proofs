from __future__ import annotations

import pytest

from periphery.mmonde.contracts_v0 import WorldObservationV0, WorldStateV0
from periphery.udip.contracts_v0 import (
    DomainStateRefV0,
    GovernancePayloadV0,
    domain_state_to_governance_payload,
    world_state_to_domain_state,
)


def world() -> WorldStateV0:
    obs = WorldObservationV0(
        observation_id="obs-1",
        observed_at="2026-10-06T12:00:00Z",
        source_refs=("sensor-a",),
        evidence_refs=("evidence-a",),
        uncertainty=("freshness_unknown",),
        contradictions=("sensor_disagreement",),
    )
    return WorldStateV0(
        world_state_id="world-1",
        valid_at="2026-10-06T12:00:00Z",
        observations=(obs,),
        unknowns=("domain_mapping_unknown",),
        risk_flags=("hostile_input_possible",),
        provenance_refs=("capture-1",),
    )


def test_world_to_domain_conserves_uncertainty_and_provenance():
    state = world_state_to_domain_state(world(), domain_id="gps")
    assert state.world_state_ref == "world-1"
    assert state.unknowns == ("domain_mapping_unknown", "freshness_unknown")
    assert state.contradictions == ("sensor_disagreement",)
    assert state.risk_flags == ("hostile_input_possible",)
    assert state.evidence_refs == ("evidence-a",)
    assert state.provenance_refs == ("capture-1", "sensor-a")


def test_domain_to_governance_payload_is_transport_not_decision():
    state = world_state_to_domain_state(world(), domain_id="gps")
    payload = domain_state_to_governance_payload(state, proposed_action_ref="proposal-1")
    assert payload.proposed_action_ref == "proposal-1"
    assert payload.decision is None
    assert payload.binder_permission is False
    assert payload.allowed_to_act is False
    assert payload.decision_authority == "KX108_ONLY"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"decision": "ACT"},
        {"binder_permission": True},
        {"allowed_to_act": True},
        {"decision_authority": "DOMAIN"},
    ],
)
def test_governance_payload_rejects_authority_leak(kwargs):
    data = dict(domain_id="gps", domain_state_ref="gps:world-1:t", world_state_ref="world-1")
    data.update(kwargs)
    with pytest.raises(ValueError):
        GovernancePayloadV0(**data)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"decision_authority": "DOMAIN"},
        {"allowed_to_decide": True},
        {"allowed_to_act": True},
    ],
)
def test_domain_state_rejects_authority_leak(kwargs):
    data = dict(domain_id="gps", world_state_ref="world-1", valid_at="t")
    data.update(kwargs)
    with pytest.raises(ValueError):
        DomainStateRefV0(**data)
