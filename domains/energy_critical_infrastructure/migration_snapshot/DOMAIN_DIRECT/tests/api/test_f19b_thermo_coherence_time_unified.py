from apps.obsidia_api.brody_thermo_coherence_time_unified import (
    build_energy_probe,
    build_replay_coherence_shadow,
    build_time_shadow,
    build_unified_thermo_coherence_time_packet,
)


THERMO = {
    "version": "THERMODYNAMICS_PACKET_V1",
    "usable_for_gencoin": True,
    "usable_for_value_layer": True,
    "stability_state": "STABLE",
    "scores": {
        "entropy_score": 0.1,
        "dissipation_score": 0.2,
        "instability_score": 0.2,
        "coherence_temperature": 0.2,
        "pressure_load": 0.2,
        "mismatch_heat": 0.0,
        "boundary_heat": 0.0,
        "memory_friction": 0.1,
        "projection_cost": 0.1,
    },
}

SIGMA = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "truth_score": 0.9,
    "sigma_score": 0.88,
    "usable_for_thermodynamics": True,
}

ANTI = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.02,
    "risk_level": "LOW",
}


def _payload():
    return {
        "thermodynamics_packet": THERMO,
        "sigma_packet": SIGMA,
        "anti_mismatch_packet": ANTI,
        "memory_response_chain_snapshot": {
            "selected_items_count": 3,
            "material_quality": "USABLE_MATERIAL",
        },
        "audit_event": {"event_id": "F19B_TEST"},
        "readonly": True,
        "emits_act": False,
        "memory_write": False,
        "graphiti_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
    }


def test_energy_probe_reuses_existing_energy_thermo():
    p = build_energy_probe(
        thermodynamics_packet=THERMO,
        sigma_packet=SIGMA,
        anti_mismatch_packet=ANTI,
    )

    assert p["source"] == "periphery.energy_thermo.run_energy_thermo"
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["emits_act"] is False
    assert p["memory_write"] is False
    assert p["kernel_mutation"] is False
    assert "extra_metrics" in p
    assert "energy_efficiency" in p["extra_metrics"]
    assert "thermo_debt" in p["extra_metrics"]


def test_replay_coherence_shadow_is_readonly():
    p = build_replay_coherence_shadow(
        payload=_payload(),
        memory_response_chain_snapshot={"selected_items_count": 2},
    )

    assert p["status"] == "COHERENCE_SHADOW_COMPUTED_READONLY"
    assert p["coherence_score"] >= 0.5
    assert p["boundary_ok_count"] == 1
    assert p["source_hit_count"] == 2
    assert p["ledger_ok_count"] == 1
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["emits_act"] is False


def test_time_shadow_is_non_decision_even_without_temporal_context():
    p = build_time_shadow(
        temporal_context_snapshot={},
        thermodynamics_packet=THERMO,
    )

    assert p["status"] == "TIME_SHADOW_NO_TEMPORAL_CONTEXT"
    assert p["temporal_context_present"] is False
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["emits_act"] is False
    assert p["memory_write"] is False


def test_unified_packet_contains_scores_and_boundaries():
    p = build_unified_thermo_coherence_time_packet(payload=_payload())

    assert p["version"] == "THERMO_COHERENCE_TIME_UNIFIED_PACKET_V1"
    assert p["status"] == "THERMO_COHERENCE_TIME_UNIFIED_READONLY_PASS"
    assert p["source"] == "BRODY_F19B_UNIFIED_THERMO_COHERENCE_TIME"

    assert p["inputs"]["has_thermodynamics_packet"] is True
    assert p["inputs"]["has_sigma_packet"] is True
    assert p["inputs"]["has_anti_mismatch_packet"] is True
    assert p["inputs"]["energy_thermo_source"] == "periphery.energy_thermo.run_energy_thermo"

    assert "thermo_coherence_temperature" in p["scores"]
    assert "energy_efficiency" in p["scores"]
    assert "replay_coherence_score" in p["scores"]
    assert "time_pressure" in p["scores"]
    assert isinstance(p["composite_temperature"], float)
    assert p["stability_state"] in ("STABLE", "WARM", "HOT", "UNSTABLE")

    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["allowed_to_decide"] is False
    assert p["allowed_to_act"] is False
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False


def test_brody_route_exposes_thermo_unified_packet():
    from pathlib import Path

    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")

    assert "build_unified_thermo_coherence_time_packet" in src
    assert "_thermo_unified_payload = {" in src
    assert "_thermo_unified_packet = safe_call_snapshot(" in src
    assert '"thermo_unified_packet": _thermo_unified_packet,' in src

    payload_block = src.split("_thermo_unified_payload = {", 1)[1].split("_thermo_unified_packet = safe_call_snapshot", 1)[0]
    assert '"thermo_unified_packet": _thermo_unified_packet,' not in payload_block
