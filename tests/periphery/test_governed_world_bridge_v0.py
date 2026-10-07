from __future__ import annotations

import pytest

from periphery.governed_world.bridge_v0 import decide_governed_world_v0, governance_payload_to_aggregate
from periphery.udip.contracts_v0 import GovernancePayloadV0


def payload(**overrides):
    data = dict(
        domain_id="gps_defense_aviation",
        domain_state_ref="gps:world-1:t",
        world_state_ref="world-1",
        evidence_refs=("evidence:1",),
        provenance_refs=("source:1",),
        proposed_action_ref="proposal:inspect",
    )
    data.update(overrides)
    return GovernancePayloadV0(**data)


def test_world_payload_enters_kernel_as_non_sovereign_aggregate():
    aggregate = governance_payload_to_aggregate(payload(), confidence=0.8)
    assert aggregate.market_verdict == "HOLD"
    assert aggregate.extra_metrics["world_payload_can_decide"] is False
    assert aggregate.extra_metrics["world_payload_can_act"] is False
    assert aggregate.evidence_refs == ["evidence:1"]
    assert aggregate.extra_metrics["provenance_refs"] == ["source:1"]
    assert "provenance:source:1" not in aggregate.evidence_refs


def test_unknown_world_state_with_low_confidence_forces_guard_hold():
    envelope = decide_governed_world_v0(
        payload(unknowns=("PHYSICAL_AUTHENTICITY_UNKNOWN",)),
        confidence=0.4,
    )
    assert envelope.x108_gate == "HOLD"
    assert envelope.reason_code == "UNKNOWNS_OR_CONFIDENCE_LOW"


def test_world_contradictions_can_only_reach_block_through_guard():
    envelope = decide_governed_world_v0(
        payload(contradictions=("C1", "C2")),
        confidence=0.99,
    )
    assert envelope.x108_gate == "BLOCK"
    assert envelope.reason_code == "CONTRADICTION_THRESHOLD_REACHED"


def test_clean_world_input_still_gets_allow_only_from_guard():
    envelope = decide_governed_world_v0(payload(), confidence=0.9)
    assert envelope.x108_gate == "ALLOW"
    assert envelope.ticket_required is True
    assert envelope.source == "canonical_framework"


def test_unsupported_domain_fails_closed_before_guard():
    with pytest.raises(ValueError, match="unsupported KX108 domain"):
        governance_payload_to_aggregate(
            GovernancePayloadV0(
                domain_id="unknown_world_domain",
                domain_state_ref="d:w:t",
                world_state_ref="w",
            ),
            confidence=0.9,
        )
