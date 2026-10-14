from __future__ import annotations

import pytest

from periphery.gps_physical.bridge_v0 import (
    RecordedGpsEvidenceV0,
    recorded_gps_to_domain,
    recorded_gps_to_world,
)


def evidence(**overrides):
    data = dict(
        evidence_id="rinex-ab02-2026-210",
        observed_at="2026-07-29T00:00:00.000Z",
        source_ref="NOAA_NGS_NCN_CORS_RINEX",
        source_hash="c81c0c78f99cc945d8d4f2074fd46de98974965d897b887c0ba45cdc77e81ea0",
        proof_level="RECORDED_REAL_GNSS",
        state={"satellites_count": 31, "gps_status": "ONLINE"},
        evidence_refs=("manifest:ab02-210",),
    )
    data.update(overrides)
    return RecordedGpsEvidenceV0(**data)


def test_recorded_gps_enters_mmonde_without_becoming_truth():
    world = recorded_gps_to_world(evidence())
    obs = world.observations[0]
    assert world.candidate_reality is True
    assert obs.causal_status == "UNKNOWN"
    assert obs.allowed_to_decide is False
    assert obs.allowed_to_act is False


def test_recorded_provenance_does_not_prove_physical_authenticity():
    with pytest.raises(ValueError, match="cannot prove physical authenticity"):
        evidence(physical_authenticity_proven=True)


def test_blocked_receiver_configuration_is_preserved_fail_closed():
    world = recorded_gps_to_world(evidence(receiver_status="BLOCKED_RECEIVER_CONFIGURATION"))
    assert "RECEIVER_CONFIGURATION_BLOCKED" in world.unknowns
    assert "LIVE_OR_ATTACK_CLAIM_NOT_CLOSED" in world.risk_flags


def test_gps_domain_bridge_keeps_kx108_authority():
    state = recorded_gps_to_domain(evidence())
    assert state.domain_id == "gps_defense_aviation"
    assert state.decision_authority == "KX108_ONLY"
    assert state.allowed_to_decide is False
    assert state.allowed_to_act is False
