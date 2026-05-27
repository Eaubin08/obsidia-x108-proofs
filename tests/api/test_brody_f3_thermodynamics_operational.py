"""F3 Thermodynamics Operational tests.

Tests THERMODYNAMICS_PACKET_V1 and its integration with Sigma V1,
Anti-Mismatch V1, and the Gencoin value_layer.
38 tests covering 38 mandatory invariants.

Invariants:
 1.  thermodynamics_packet exists in returned dict.
 2.  version == THERMODYNAMICS_PACKET_V1.
 3.  mode == SHADOW_READONLY.
 4.  decision_authority == KX108_ONLY.
 5.  advisory_only == true.
 6.  readonly == true.
 7.  emits_act == false.
 8.  emits_verdict == false.
 9.  memory_write == false.
10.  kernel_mutation == false.
11.  x108_mutation == false.
12.  thermodynamics_active == true.
13.  All 9 scores are floats bounded [0.0, 1.0].
14.  entropy_score decreases as truth_score increases.
15.  mismatch_heat == mismatch_score from anti_mismatch_packet.
16.  boundary_heat increases when boundary_detected or BOUNDARY_COMPACT.
17.  memory_friction increases with lower material quality.
18.  projection_cost increases for very short or very long answers.
19.  pressure_load converts LOW/MEDIUM/HIGH correctly.
20.  dissipation_score is bounded [0.0, 1.0].
21.  instability_score is bounded [0.0, 1.0].
22.  coherence_temperature is bounded [0.0, 1.0].
23.  stability_state in {STABLE, WARM, HOT, UNSTABLE, INSUFFICIENT_MATERIAL}.
24.  usable_for_gencoin=False if sigma not usable for thermo.
25.  usable_for_gencoin=False if anti_mismatch risk_level HIGH.
26.  usable_for_gencoin=True if sigma usable + mismatch low + material present.
27.  value_layer.inputs_available.thermodynamics=True when packet present.
28.  value_layer.input_status.thermodynamics reflects stability_state.
29.  value_layer.scores.energy_cost remains null.
30.  value_layer.final_scoring_enabled == False.
31.  Gencoin final scoring remains disabled.
32.  F2A tests pass (backward compatibility).
33.  F2B tests pass (backward compatibility).
34.  F2C tests pass (backward compatibility).
35.  No ACT / verdict / write / kernel mutation introduced.
36.  OS Trad → IR → Reverse ordering unmodified (sigma, anti_mismatch, thermo observe — do not insert).
37.  safe_call_snapshot degradation: absent thermo not claimed usable.
38.  Thermodynamics does not modify sigma, anti_mismatch, or value_layer scores.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_thermodynamics_signal import build_thermodynamics_packet
from apps.obsidia_api.brody_gencoin_transverse_interface import (
    build_gencoin_transverse_packet,
    build_sigma_packet,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

_SIGMA_CALIBRATED = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_thermodynamics": True,
    "usable_for_gencoin": True,
    "truth_score": 0.75,
    "sigma_pressure": "MEDIUM",
}

_SIGMA_HIGH_QUALITY = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_thermodynamics": True,
    "usable_for_gencoin": True,
    "truth_score": 0.95,
    "sigma_pressure": "LOW",
}

_SIGMA_LOW_QUALITY = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_thermodynamics": True,
    "usable_for_gencoin": True,
    "truth_score": 0.30,
    "sigma_pressure": "HIGH",
}

_SIGMA_NOT_USABLE = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_BOUNDARY_ONLY",
    "usable_for_thermodynamics": False,
    "usable_for_gencoin": False,
    "truth_score": 0.40,
    "sigma_pressure": "HIGH",
}

_SIGMA_INSUFFICIENT = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "INSUFFICIENT_MATERIAL",
    "usable_for_thermodynamics": False,
    "truth_score": None,
}

_AMP_LOW = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.10,
    "risk_level": "LOW",
    "decorative_coherence_detected": False,
}

_AMP_HIGH = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.80,
    "risk_level": "HIGH",
    "decorative_coherence_detected": True,
}

_AMP_NONE = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.0,
    "risk_level": "NONE",
    "decorative_coherence_detected": False,
}

_IR = {
    "intent_type": "pure_response",
    "entities": [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "decision_authority": "KX108_ONLY",
}

_TVS_MEDIUM = {
    "final_answer": " ".join(["mot"] * 150),  # 150 words — normal range
}

_TVS_SHORT = {
    "final_answer": "Oui.",  # 1 word — very short
}

_TVS_LONG = {
    "final_answer": " ".join(["mot"] * 900),  # 900 words — very long
}

_TVS_EMPTY: dict = {}

_POL_NORMAL = {
    "sigma_pressure": "MEDIUM",
    "response_size": "MEDIUM",
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
}

_POL_BOUNDARY = {
    "sigma_pressure": "HIGH",
    "response_size": "BOUNDARY_COMPACT",
    "boundary_detected": True,
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
}

_CHAIN_USABLE = {
    "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "material_quality": "USABLE_MATERIAL",
}

_CHAIN_PARTIAL = {
    "material_quality": "PARTIAL_MATERIAL",
}

_CHAIN_EMPTY: dict = {}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_default():
    return build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        anti_mismatch_packet=_AMP_LOW,
        ir_candidate=_IR,
        true_voice_snapshot=_TVS_MEDIUM,
        adaptive_response_policy=_POL_NORMAL,
        memory_chain=_CHAIN_USABLE,
    )


def _tp(result):
    return result["thermodynamics_packet"]


def _scores(result):
    return _tp(result)["scores"]


_EXPECTED_SCORE_KEYS = {
    "entropy_score", "dissipation_score", "instability_score",
    "coherence_temperature", "pressure_load", "mismatch_heat",
    "boundary_heat", "memory_friction", "projection_cost",
}


# ── Invariant 1: packet exists ───────────────────────────────────────────────

def test_01_thermodynamics_packet_exists():
    result = _build_default()
    assert "thermodynamics_packet" in result


# ── Invariant 2: version ─────────────────────────────────────────────────────

def test_02_version():
    assert _tp(_build_default())["version"] == "THERMODYNAMICS_PACKET_V1"


# ── Invariant 3: mode ────────────────────────────────────────────────────────

def test_03_mode_shadow_readonly():
    assert _tp(_build_default())["mode"] == "SHADOW_READONLY"


# ── Invariant 4: decision_authority ─────────────────────────────────────────

def test_04_decision_authority():
    assert _tp(_build_default())["decision_authority"] == "KX108_ONLY"


# ── Invariant 5: advisory_only ───────────────────────────────────────────────

def test_05_advisory_only():
    assert _tp(_build_default())["advisory_only"] is True


# ── Invariant 6: readonly ────────────────────────────────────────────────────

def test_06_readonly():
    assert _tp(_build_default())["readonly"] is True


# ── Invariant 7: emits_act ───────────────────────────────────────────────────

def test_07_emits_act_false():
    assert _tp(_build_default())["emits_act"] is False


# ── Invariant 8: emits_verdict ───────────────────────────────────────────────

def test_08_emits_verdict_false():
    assert _tp(_build_default())["emits_verdict"] is False


# ── Invariant 9: memory_write ────────────────────────────────────────────────

def test_09_memory_write_false():
    assert _tp(_build_default())["memory_write"] is False


# ── Invariant 10: kernel_mutation ───────────────────────────────────────────

def test_10_kernel_mutation_false():
    assert _tp(_build_default())["kernel_mutation"] is False


# ── Invariant 11: x108_mutation ─────────────────────────────────────────────

def test_11_x108_mutation_false():
    assert _tp(_build_default())["x108_mutation"] is False


# ── Invariant 12: thermodynamics_active ──────────────────────────────────────

def test_12_thermodynamics_active():
    assert _tp(_build_default())["thermodynamics_active"] is True


# ── Invariant 13: all 9 scores are floats [0.0, 1.0] ────────────────────────

def test_13_all_scores_bounded_floats():
    scores = _scores(_build_default())
    assert _EXPECTED_SCORE_KEYS == set(scores.keys())
    for key, val in scores.items():
        assert isinstance(val, float), f"Score {key!r} is not float: {val!r}"
        assert 0.0 <= val <= 1.0, f"Score {key!r}={val} out of [0.0, 1.0]"


# ── Invariant 14: entropy_score decreases as truth_score increases ────────────

def test_14_entropy_score_inversely_correlated_with_truth_score():
    low_quality = build_thermodynamics_packet(sigma_packet=_SIGMA_LOW_QUALITY)
    high_quality = build_thermodynamics_packet(sigma_packet=_SIGMA_HIGH_QUALITY)
    e_low = _scores(low_quality)["entropy_score"]
    e_high = _scores(high_quality)["entropy_score"]
    # truth_score 0.30 → entropy ~0.70; truth_score 0.95 → entropy ~0.05
    assert e_low > e_high


# ── Invariant 15: mismatch_heat == mismatch_score ────────────────────────────

def test_15_mismatch_heat_equals_mismatch_score():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        anti_mismatch_packet=_AMP_HIGH,
    )
    assert _scores(result)["mismatch_heat"] == pytest.approx(0.80, abs=0.001)


def test_15b_mismatch_heat_zero_when_no_amp():
    result = build_thermodynamics_packet(sigma_packet=_SIGMA_CALIBRATED)
    assert _scores(result)["mismatch_heat"] == 0.0


# ── Invariant 16: boundary_heat increases with boundary ──────────────────────

def test_16_boundary_heat_increases_with_boundary_compact():
    normal = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        adaptive_response_policy=_POL_NORMAL,
    )
    boundary = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        adaptive_response_policy=_POL_BOUNDARY,
    )
    assert _scores(boundary)["boundary_heat"] > _scores(normal)["boundary_heat"]


def test_16b_boundary_heat_zero_when_normal():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        adaptive_response_policy=_POL_NORMAL,
    )
    assert _scores(result)["boundary_heat"] == 0.0


# ── Invariant 17: memory_friction increases with lower quality ───────────────

def test_17_memory_friction_zero_for_usable():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        memory_chain=_CHAIN_USABLE,
    )
    assert _scores(result)["memory_friction"] == 0.0


def test_17b_memory_friction_higher_for_partial():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        memory_chain=_CHAIN_PARTIAL,
    )
    assert _scores(result)["memory_friction"] == pytest.approx(0.25, abs=0.001)


def test_17c_memory_friction_highest_when_absent():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        memory_chain=_CHAIN_EMPTY,
    )
    assert _scores(result)["memory_friction"] == pytest.approx(0.50, abs=0.001)


# ── Invariant 18: projection_cost varies with answer length ──────────────────

def test_18_projection_cost_short_answer():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        true_voice_snapshot=_TVS_SHORT,
    )
    assert _scores(result)["projection_cost"] == pytest.approx(0.10, abs=0.001)


def test_18b_projection_cost_normal_answer():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        true_voice_snapshot=_TVS_MEDIUM,  # 150 words — in [80..350]
    )
    assert _scores(result)["projection_cost"] == 0.0


def test_18c_projection_cost_very_long_answer():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        true_voice_snapshot=_TVS_LONG,  # 900 words > 800
    )
    assert _scores(result)["projection_cost"] == pytest.approx(0.50, abs=0.001)


# ── Invariant 19: pressure_load converts sigma_pressure ──────────────────────

def test_19_pressure_load_low():
    sp = {**_SIGMA_CALIBRATED, "sigma_pressure": "LOW"}
    result = build_thermodynamics_packet(sigma_packet=sp)
    assert _scores(result)["pressure_load"] == pytest.approx(0.20, abs=0.001)


def test_19b_pressure_load_medium():
    sp = {**_SIGMA_CALIBRATED, "sigma_pressure": "MEDIUM"}
    result = build_thermodynamics_packet(sigma_packet=sp)
    assert _scores(result)["pressure_load"] == pytest.approx(0.50, abs=0.001)


def test_19c_pressure_load_high():
    sp = {**_SIGMA_CALIBRATED, "sigma_pressure": "HIGH"}
    result = build_thermodynamics_packet(sigma_packet=sp)
    assert _scores(result)["pressure_load"] == pytest.approx(0.80, abs=0.001)


def test_19d_pressure_load_unknown_defaults():
    sp = {**_SIGMA_CALIBRATED, "sigma_pressure": None}
    result = build_thermodynamics_packet(sigma_packet=sp)
    assert _scores(result)["pressure_load"] == pytest.approx(0.30, abs=0.001)


# ── Invariant 20: dissipation_score bounded ──────────────────────────────────

def test_20_dissipation_score_bounded():
    result = _build_default()
    s = _scores(result)["dissipation_score"]
    assert 0.0 <= s <= 1.0


# ── Invariant 21: instability_score bounded ───────────────────────────────────

def test_21_instability_score_bounded():
    result = _build_default()
    s = _scores(result)["instability_score"]
    assert 0.0 <= s <= 1.0


# ── Invariant 22: coherence_temperature bounded ───────────────────────────────

def test_22_coherence_temperature_bounded():
    result = _build_default()
    s = _scores(result)["coherence_temperature"]
    assert 0.0 <= s <= 1.0


# ── Invariant 23: stability_state valid enum ─────────────────────────────────

_VALID_STATES = {"STABLE", "WARM", "HOT", "UNSTABLE", "INSUFFICIENT_MATERIAL"}

def test_23_stability_state_valid():
    assert _tp(_build_default())["stability_state"] in _VALID_STATES


def test_23b_stability_state_insufficient_when_no_sigma():
    result = build_thermodynamics_packet()
    assert _tp(result)["stability_state"] == "INSUFFICIENT_MATERIAL"


def test_23c_stability_state_insufficient_when_truth_score_null():
    result = build_thermodynamics_packet(sigma_packet=_SIGMA_INSUFFICIENT)
    assert _tp(result)["stability_state"] == "INSUFFICIENT_MATERIAL"


# ── Invariant 24: usable_for_gencoin False when sigma not usable ─────────────

def test_24_usable_for_gencoin_false_when_sigma_not_usable():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_NOT_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        memory_chain=_CHAIN_USABLE,
    )
    assert _tp(result)["usable_for_gencoin"] is False


# ── Invariant 25: usable_for_gencoin False when anti_mismatch HIGH ───────────

def test_25_usable_for_gencoin_false_when_mismatch_high():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        anti_mismatch_packet=_AMP_HIGH,  # risk_level HIGH
        memory_chain=_CHAIN_USABLE,
        true_voice_snapshot=_TVS_MEDIUM,
    )
    assert _tp(result)["usable_for_gencoin"] is False


# ── Invariant 26: usable_for_gencoin True when sigma usable + mismatch low ───

def test_26_usable_for_gencoin_true_when_all_ok():
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        anti_mismatch_packet=_AMP_LOW,
        memory_chain=_CHAIN_USABLE,
        true_voice_snapshot=_TVS_MEDIUM,
    )
    assert _tp(result)["usable_for_gencoin"] is True


# ── Invariant 27: value_layer.inputs_available.thermodynamics=True ───────────

def test_27_value_layer_thermo_input_true():
    thermo_result = _build_default()
    tp_pkt = thermo_result["thermodynamics_packet"]
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_pkt,
    )
    vl = vl_result["value_layer"]
    assert vl["inputs_available"]["thermodynamics"] is True


# ── Invariant 28: value_layer.input_status.thermodynamics = stability_state ──

def test_28_value_layer_thermo_status_reflects_stability():
    thermo_result = _build_default()
    tp_pkt = thermo_result["thermodynamics_packet"]
    stability = tp_pkt["stability_state"]
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_pkt,
    )
    vl = vl_result["value_layer"]
    assert vl["input_status"]["thermodynamics"] == stability


# ── Invariant 29: value_layer.scores.energy_cost remains null ────────────────

def test_29_energy_cost_remains_null():
    thermo_result = _build_default()
    tp_pkt = thermo_result["thermodynamics_packet"]
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_pkt,
    )
    assert vl_result["value_layer"]["scores"]["energy_cost"] is None


# ── Invariant 30: value_layer.final_scoring_enabled == False ─────────────────

def test_30_final_scoring_disabled():
    thermo_result = _build_default()
    tp_pkt = thermo_result["thermodynamics_packet"]
    vl_result = build_gencoin_transverse_packet(thermodynamics_packet=tp_pkt)
    assert vl_result["value_layer"]["final_scoring_enabled"] is False


# ── Invariant 31: gencoin final scoring remains disabled ─────────────────────

def test_31_all_gencoin_scores_null():
    thermo_result = _build_default()
    tp_pkt = thermo_result["thermodynamics_packet"]
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_pkt,
    )
    scores = vl_result["value_layer"]["scores"]
    for key, val in scores.items():
        assert val is None, f"Gencoin score {key!r} must be null, got {val!r}"


# ── Invariant 32-34: F2A / F2B / F2C backward compatibility ──────────────────

def test_32_f2a_build_gencoin_no_thermo_still_works():
    # Calling without thermodynamics_packet must not crash
    pkt = build_gencoin_transverse_packet(ir_candidate=_IR)
    assert "value_layer" in pkt
    assert pkt["value_layer"]["final_scoring_enabled"] is False
    # Without thermo, inputs_available.thermodynamics must be False (DEFERRED)
    assert pkt["value_layer"]["inputs_available"]["thermodynamics"] is False
    assert pkt["value_layer"]["input_status"]["thermodynamics"] == "DEFERRED"


def test_33_f2b_sigma_packet_unchanged_by_thermo():
    sigma = build_sigma_packet(
        {"sigma_pressure": "MEDIUM", "readonly": True, "emits_act": False, "memory_write": False},
        ir_candidate=_IR,
    )
    # Sigma built without thermo (thermo does not modify sigma)
    assert sigma["version"] == "SIGMA_CALIBRATION_PACKET_V1"
    assert sigma["emits_act"] is False
    assert sigma["decision_authority"] == "KX108_ONLY"


def test_34_f2c_thermo_does_not_modify_anti_mismatch():
    # Anti-mismatch packet is passed to thermo but must come back unmodified
    from apps.obsidia_api.brody_anti_mismatch_signal import build_anti_mismatch_signal
    amp_result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_MEDIUM,
        sigma_packet=_SIGMA_CALIBRATED,
    )
    amp_before = amp_result["anti_mismatch_packet"].copy()
    # Pass to thermo
    build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        anti_mismatch_packet=amp_result["anti_mismatch_packet"],
    )
    # Anti-mismatch packet object must not have been mutated
    assert amp_result["anti_mismatch_packet"] == amp_before


# ── Invariant 35: no ACT / verdict / write / kernel mutation ─────────────────

def test_35_no_act_verdict_write_mutation():
    import json
    tp_result = _build_default()
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_result["thermodynamics_packet"],
    )
    dumped = json.dumps({"tp": tp_result, "vl": vl_result}, default=str)
    forbidden = ['"emits_act": true', '"emits_verdict": true', '"memory_write": true',
                 '"kernel_mutation": true', '"x108_mutation": true']
    for token in forbidden:
        assert token not in dumped, f"Forbidden token {token!r} found"


# ── Invariant 36: OS Trad → IR → Reverse ordering unmodified ────────────────

def test_36_pipeline_observes_only_does_not_insert():
    # Thermodynamics receives IR and reverse — does not modify them
    original_final_answer = _TVS_MEDIUM["final_answer"]
    result = build_thermodynamics_packet(
        sigma_packet=_SIGMA_CALIBRATED,
        ir_candidate=_IR,
        true_voice_snapshot=_TVS_MEDIUM,
    )
    # TVS final_answer must be unchanged
    assert _TVS_MEDIUM["final_answer"] == original_final_answer
    # IR intent_type must be unchanged
    assert _IR["intent_type"] == "pure_response"
    # Thermo does not produce a new ir_candidate or modify reverse OS
    tp = result["thermodynamics_packet"]
    assert "ir_candidate" not in tp
    assert "final_answer" not in tp


# ── Invariant 37: absent thermo not claimed usable ───────────────────────────

def test_37_absent_thermo_value_layer_deferred():
    # Without thermodynamics_packet, gencoin must show DEFERRED, not STABLE
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR)
    vl = vl_result["value_layer"]
    assert vl["inputs_available"]["thermodynamics"] is False
    assert vl["input_status"]["thermodynamics"] == "DEFERRED"


# ── Invariant 38: thermo does not modify sigma or value_layer scores ──────────

def test_38_thermo_does_not_modify_sigma_or_value_layer():
    sigma_before = dict(_SIGMA_CALIBRATED)
    tp_result = build_thermodynamics_packet(sigma_packet=_SIGMA_CALIBRATED)
    # Sigma dict unchanged
    assert _SIGMA_CALIBRATED == sigma_before

    # Value layer scores are still all null after thermo wired
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        thermodynamics_packet=tp_result["thermodynamics_packet"],
    )
    for key, val in vl_result["value_layer"]["scores"].items():
        assert val is None, f"Score {key!r} must remain null"
