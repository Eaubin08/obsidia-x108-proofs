"""F4 Gencoin Shadow Value Layer tests.

Tests GENCOIN_SHADOW_VALUE_PACKET_V1 and its integration with
Sigma V1, Anti-Mismatch V1, Thermodynamics V1, and the Gencoin value_layer.
44 mandatory invariants.

Invariants:
 1.  gencoin_shadow_packet exists in returned dict.
 2.  version == GENCOIN_SHADOW_VALUE_PACKET_V1.
 3.  mode == SHADOW_READONLY.
 4.  decision_authority == KX108_ONLY.
 5.  advisory_only == true.
 6.  readonly == true.
 7.  emits_act == false.
 8.  emits_verdict == false.
 9.  memory_write == false.
10.  kernel_mutation == false.
11.  x108_mutation == false.
12.  final_scoring_enabled == false.
13.  economic_scoring_enabled == false.
14.  blockchain_enabled == false.
15.  memory_promotion_enabled == false.
16.  economic_projection == null always.
17.  usable=True → all shadow scores except economic_projection are float [0.0, 1.0].
18.  usable=False → all shadow scores are null.
19.  cognitive_value decreases when mismatch_score increases.
20.  cognitive_value decreases when entropy_score increases.
21.  proof_value higher when has_proof_readonly=True.
22.  memory_value reflects USABLE/PARTIAL/absent quality bands.
23.  attention_cost increases with answer length.
24.  energy_cost == thermodynamics dissipation_score.
25.  stability_value == 1.0 - instability_score.
26.  reuse_value bounded [0.0, 1.0].
27.  usable_shadow_value=False if sigma not usable for gencoin.
28.  usable_shadow_value=False if thermo not usable for gencoin.
29.  usable_shadow_value=False if anti_mismatch risk HIGH.
30.  value_layer.inputs_available.gencoin_shadow=True when packet present.
31.  value_layer.input_status.gencoin_shadow reflects usable_shadow_value.
32.  value_layer.scores all remain null.
33.  value_layer.final_scoring_enabled == False.
34.  Gencoin final scoring remains disabled.
35.  F2A backward compatibility preserved.
36.  F2B backward compatibility preserved.
37.  F2C backward compatibility preserved.
38.  F3 backward compatibility preserved.
39.  No ACT / verdict / write / kernel mutation.
40.  OS Trad → IR → Reverse ordering unmodified.
41.  blockchain_enabled == false.
42.  memory_promotion_enabled == false.
43.  Absent gencoin_shadow → value_layer shows DEFERRED, not usable.
44.  gencoin_shadow_packet does not modify sigma, anti_mismatch, or thermo.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_gencoin_shadow_value import build_gencoin_shadow_value_packet
from apps.obsidia_api.brody_gencoin_transverse_interface import (
    build_gencoin_transverse_packet,
    build_sigma_packet,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

_SIGMA_USABLE = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_gencoin": True,
    "usable_for_thermodynamics": True,
    "truth_score": 0.75,
    "sigma_pressure": "MEDIUM",
}

_SIGMA_HIGH = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_gencoin": True,
    "truth_score": 0.90,
    "sigma_pressure": "LOW",
}

_SIGMA_LOW = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
    "usable_for_gencoin": True,
    "truth_score": 0.30,
    "sigma_pressure": "HIGH",
}

_SIGMA_NOT_USABLE = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "calibration_status": "CALIBRATED_BOUNDARY_ONLY",
    "usable_for_gencoin": False,
    "truth_score": 0.40,
}

_AMP_LOW = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.10,
    "risk_level": "LOW",
}

_AMP_HIGH_RISK = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.80,
    "risk_level": "HIGH",
}

_AMP_NONE = {
    "version": "ANTI_MISMATCH_SIGNAL_V1",
    "mismatch_score": 0.0,
    "risk_level": "NONE",
}

_THERMO_STABLE = {
    "version": "THERMODYNAMICS_PACKET_V1",
    "usable_for_gencoin": True,
    "stability_state": "STABLE",
    "scores": {
        "entropy_score": 0.25,
        "dissipation_score": 0.217,
        "instability_score": 0.25,
        "coherence_temperature": 0.239,
        "pressure_load": 0.50,
        "mismatch_heat": 0.10,
        "boundary_heat": 0.0,
        "memory_friction": 0.0,
        "projection_cost": 0.0,
    },
}

_THERMO_HOT = {
    "version": "THERMODYNAMICS_PACKET_V1",
    "usable_for_gencoin": True,
    "stability_state": "HOT",
    "scores": {
        "entropy_score": 0.60,
        "dissipation_score": 0.55,
        "instability_score": 0.60,
        "coherence_temperature": 0.55,
        "pressure_load": 0.80,
        "mismatch_heat": 0.60,
        "boundary_heat": 0.40,
        "memory_friction": 0.50,
        "projection_cost": 0.30,
    },
}

_THERMO_NOT_USABLE = {
    "version": "THERMODYNAMICS_PACKET_V1",
    "usable_for_gencoin": False,
    "stability_state": "INSUFFICIENT_MATERIAL",
    "scores": {},
}

_IR = {
    "intent_type": "pure_response",
    "entities": [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "decision_authority": "KX108_ONLY",
}

_TVS_MEDIUM = {
    "final_answer": " ".join(["mot"] * 150),  # 150 words
}

_TVS_SHORT = {
    "final_answer": "Oui.",  # 1 word
}

_TVS_LONG = {
    "final_answer": " ".join(["mot"] * 900),  # 900 words
}

_TVS_MED_350 = {
    "final_answer": " ".join(["mot"] * 400),  # 400 words > 350
}

_CHAIN_USABLE = {
    "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "material_quality": "USABLE_MATERIAL",
}

_CHAIN_PARTIAL = {"material_quality": "PARTIAL_MATERIAL"}
_CHAIN_EMPTY: dict = {}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_default():
    return build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE,
        ir_candidate=_IR,
        true_voice_snapshot=_TVS_MEDIUM,
        memory_chain=_CHAIN_USABLE,
        has_proof_readonly=True,
    )


def _gsp(result):
    return result["gencoin_shadow_packet"]


def _ss(result):
    return _gsp(result)["shadow_scores"]


# ── Invariant 1: packet exists ───────────────────────────────────────────────

def test_01_gencoin_shadow_packet_exists():
    result = _build_default()
    assert "gencoin_shadow_packet" in result


# ── Invariant 2: version ─────────────────────────────────────────────────────

def test_02_version():
    assert _gsp(_build_default())["version"] == "GENCOIN_SHADOW_VALUE_PACKET_V1"


# ── Invariant 3: mode ────────────────────────────────────────────────────────

def test_03_mode_shadow_readonly():
    assert _gsp(_build_default())["mode"] == "SHADOW_READONLY"


# ── Invariant 4: decision_authority ─────────────────────────────────────────

def test_04_decision_authority():
    assert _gsp(_build_default())["decision_authority"] == "KX108_ONLY"


# ── Invariant 5: advisory_only ───────────────────────────────────────────────

def test_05_advisory_only():
    assert _gsp(_build_default())["advisory_only"] is True


# ── Invariant 6: readonly ────────────────────────────────────────────────────

def test_06_readonly():
    assert _gsp(_build_default())["readonly"] is True


# ── Invariant 7: emits_act ───────────────────────────────────────────────────

def test_07_emits_act_false():
    assert _gsp(_build_default())["emits_act"] is False


# ── Invariant 8: emits_verdict ───────────────────────────────────────────────

def test_08_emits_verdict_false():
    assert _gsp(_build_default())["emits_verdict"] is False


# ── Invariant 9: memory_write ────────────────────────────────────────────────

def test_09_memory_write_false():
    assert _gsp(_build_default())["memory_write"] is False


# ── Invariant 10: kernel_mutation ───────────────────────────────────────────

def test_10_kernel_mutation_false():
    assert _gsp(_build_default())["kernel_mutation"] is False


# ── Invariant 11: x108_mutation ─────────────────────────────────────────────

def test_11_x108_mutation_false():
    assert _gsp(_build_default())["x108_mutation"] is False


# ── Invariant 12: final_scoring_enabled ──────────────────────────────────────

def test_12_final_scoring_disabled():
    assert _gsp(_build_default())["final_scoring_enabled"] is False


# ── Invariant 13: economic_scoring_enabled ────────────────────────────────────

def test_13_economic_scoring_disabled():
    assert _gsp(_build_default())["economic_scoring_enabled"] is False


# ── Invariant 14: blockchain_enabled ─────────────────────────────────────────

def test_14_blockchain_disabled():
    assert _gsp(_build_default())["blockchain_enabled"] is False


# ── Invariant 15: memory_promotion_enabled ────────────────────────────────────

def test_15_memory_promotion_disabled():
    assert _gsp(_build_default())["memory_promotion_enabled"] is False


# ── Invariant 16: economic_projection always null ─────────────────────────────

def test_16_economic_projection_always_null():
    # When usable
    assert _ss(_build_default())["economic_projection"] is None
    # When not usable
    result_nu = build_gencoin_shadow_value_packet(sigma_packet=_SIGMA_NOT_USABLE)
    assert result_nu["gencoin_shadow_packet"]["shadow_scores"]["economic_projection"] is None


# ── Invariant 17: usable=True → all scores (excl. economic_projection) float ─

_EXPECTED_SHADOW_KEYS = {
    "cognitive_value", "proof_value", "reuse_value", "memory_value",
    "attention_cost", "energy_cost", "stability_value", "economic_projection",
}

def test_17_usable_true_all_scores_bounded_float():
    result = _build_default()
    gsp = _gsp(result)
    assert gsp["usable_shadow_value"] is True
    ss = gsp["shadow_scores"]
    assert set(ss.keys()) == _EXPECTED_SHADOW_KEYS
    for key, val in ss.items():
        if key == "economic_projection":
            assert val is None
        else:
            assert isinstance(val, float), f"{key!r} must be float"
            assert 0.0 <= val <= 1.0, f"{key!r}={val} out of bounds"


# ── Invariant 18: usable=False → all scores null ──────────────────────────────

def test_18_usable_false_all_scores_null():
    result = build_gencoin_shadow_value_packet(sigma_packet=_SIGMA_NOT_USABLE)
    gsp = _gsp(result)
    assert gsp["usable_shadow_value"] is False
    for key, val in gsp["shadow_scores"].items():
        assert val is None, f"{key!r} must be null when not usable, got {val!r}"


# ── Invariant 19: cognitive_value decreases when mismatch increases ───────────

def test_19_cognitive_value_decreases_with_mismatch():
    low_mismatch = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_NONE,
        thermodynamics_packet=_THERMO_STABLE,
    )
    amp_medium = {"version": "ANTI_MISMATCH_SIGNAL_V1", "mismatch_score": 0.50, "risk_level": "MEDIUM"}
    high_mismatch = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=amp_medium,
        thermodynamics_packet=_THERMO_STABLE,
    )
    cv_low = _ss(low_mismatch)["cognitive_value"]
    cv_high = _ss(high_mismatch)["cognitive_value"]
    assert cv_low > cv_high


# ── Invariant 20: cognitive_value decreases when entropy increases ─────────────

def test_20_cognitive_value_decreases_with_entropy():
    thermo_low_entropy = {**_THERMO_STABLE, "scores": {**_THERMO_STABLE["scores"], "entropy_score": 0.10}}
    thermo_high_entropy = {**_THERMO_STABLE, "scores": {**_THERMO_STABLE["scores"], "entropy_score": 0.80}}
    r_low = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=thermo_low_entropy,
    )
    r_high = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=thermo_high_entropy,
    )
    assert _ss(r_low)["cognitive_value"] > _ss(r_high)["cognitive_value"]


# ── Invariant 21: proof_value higher with proof_readonly ─────────────────────

def test_21_proof_value_higher_with_proof():
    with_proof = _build_default()  # has_proof_readonly=True
    without_proof = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, has_proof_readonly=False,
    )
    assert _ss(with_proof)["proof_value"] > _ss(without_proof)["proof_value"]


# ── Invariant 22: memory_value reflects quality bands ────────────────────────

def test_22_memory_value_usable():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, memory_chain=_CHAIN_USABLE,
    )
    assert _ss(r)["memory_value"] >= 0.70


def test_22b_memory_value_partial():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, memory_chain=_CHAIN_PARTIAL,
    )
    mv = _ss(r)["memory_value"]
    assert 0.45 <= mv <= 0.60


def test_22c_memory_value_absent():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, memory_chain=_CHAIN_EMPTY,
    )
    mv = _ss(r)["memory_value"]
    assert mv < 0.20


# ── Invariant 23: attention_cost increases with answer length ─────────────────

def test_23_attention_cost_short():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, true_voice_snapshot=_TVS_SHORT,
    )
    assert _ss(r)["attention_cost"] == pytest.approx(0.20, abs=0.001)


def test_23b_attention_cost_medium():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, true_voice_snapshot=_TVS_MEDIUM,
    )
    assert _ss(r)["attention_cost"] == pytest.approx(0.40, abs=0.001)


def test_23c_attention_cost_long():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, true_voice_snapshot=_TVS_LONG,
    )
    assert _ss(r)["attention_cost"] == pytest.approx(0.90, abs=0.001)


def test_23d_attention_cost_350_plus():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE, true_voice_snapshot=_TVS_MED_350,
    )
    assert _ss(r)["attention_cost"] == pytest.approx(0.65, abs=0.001)


# ── Invariant 24: energy_cost == dissipation_score ───────────────────────────

def test_24_energy_cost_equals_dissipation():
    r = _build_default()
    expected_dissipation = _THERMO_STABLE["scores"]["dissipation_score"]
    assert _ss(r)["energy_cost"] == pytest.approx(expected_dissipation, abs=0.001)


def test_24b_energy_cost_null_when_no_thermo():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE, anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_NOT_USABLE,
    )
    # Not usable → all null including energy_cost
    assert _gsp(r)["usable_shadow_value"] is False
    assert _ss(r)["energy_cost"] is None


# ── Invariant 25: stability_value == 1.0 - instability_score ─────────────────

def test_25_stability_value_equals_one_minus_instability():
    r = _build_default()
    instability = _THERMO_STABLE["scores"]["instability_score"]
    expected = round(1.0 - instability, 3)
    assert _ss(r)["stability_value"] == pytest.approx(expected, abs=0.001)


# ── Invariant 26: reuse_value bounded ────────────────────────────────────────

def test_26_reuse_value_bounded():
    r = _build_default()
    rv = _ss(r)["reuse_value"]
    assert isinstance(rv, float)
    assert 0.0 <= rv <= 1.0


# ── Invariant 27: usable=False if sigma not usable ───────────────────────────

def test_27_not_usable_when_sigma_not_usable():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_NOT_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE,
    )
    assert _gsp(r)["usable_shadow_value"] is False


# ── Invariant 28: usable=False if thermo not usable ──────────────────────────

def test_28_not_usable_when_thermo_not_usable():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_NOT_USABLE,
    )
    assert _gsp(r)["usable_shadow_value"] is False


# ── Invariant 29: usable=False if anti_mismatch HIGH ─────────────────────────

def test_29_not_usable_when_mismatch_high():
    r = build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_HIGH_RISK,
        thermodynamics_packet=_THERMO_STABLE,
    )
    assert _gsp(r)["usable_shadow_value"] is False


# ── Invariant 30: value_layer.inputs_available.gencoin_shadow=True ───────────

def test_30_value_layer_gencoin_shadow_input_true():
    gsp_result = _build_default()
    gsp_pkt = gsp_result["gencoin_shadow_packet"]
    vl_result = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        gencoin_shadow_packet=gsp_pkt,
    )
    assert vl_result["value_layer"]["inputs_available"]["gencoin_shadow"] is True


# ── Invariant 31: value_layer.input_status.gencoin_shadow reflects usable ────

def test_31_value_layer_gencoin_shadow_status_usable():
    gsp_result = _build_default()
    gsp_pkt = gsp_result["gencoin_shadow_packet"]
    assert gsp_pkt["usable_shadow_value"] is True
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR, gencoin_shadow_packet=gsp_pkt)
    assert vl_result["value_layer"]["input_status"]["gencoin_shadow"] == "USABLE_SHADOW_VALUE"


def test_31b_value_layer_gencoin_shadow_status_not_usable():
    r_nu = build_gencoin_shadow_value_packet(sigma_packet=_SIGMA_NOT_USABLE)
    gsp_pkt = r_nu["gencoin_shadow_packet"]
    assert gsp_pkt["usable_shadow_value"] is False
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR, gencoin_shadow_packet=gsp_pkt)
    assert vl_result["value_layer"]["input_status"]["gencoin_shadow"] == "NOT_USABLE_SHADOW_VALUE"


# ── Invariant 32: value_layer.scores all remain null ─────────────────────────

def test_32_value_layer_scores_all_null():
    gsp_result = _build_default()
    gsp_pkt = gsp_result["gencoin_shadow_packet"]
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR, gencoin_shadow_packet=gsp_pkt)
    for key, val in vl_result["value_layer"]["scores"].items():
        assert val is None, f"value_layer.scores.{key} must be null"


# ── Invariant 33: value_layer.final_scoring_enabled == False ─────────────────

def test_33_value_layer_final_scoring_disabled():
    gsp_pkt = _build_default()["gencoin_shadow_packet"]
    vl_result = build_gencoin_transverse_packet(gencoin_shadow_packet=gsp_pkt)
    assert vl_result["value_layer"]["final_scoring_enabled"] is False


# ── Invariant 34: gencoin final scoring globally disabled ────────────────────

def test_34_gencoin_final_scoring_globally_disabled():
    # Build the full pipeline — final_scoring_enabled must be False everywhere
    gsp_result = _build_default()
    gsp_pkt = gsp_result["gencoin_shadow_packet"]
    vl_result = build_gencoin_transverse_packet(gencoin_shadow_packet=gsp_pkt)
    assert gsp_pkt["final_scoring_enabled"] is False
    assert vl_result["value_layer"]["final_scoring_enabled"] is False


# ── Invariant 35-38: backward compatibility ──────────────────────────────────

def test_35_f2a_gencoin_without_shadow_still_works():
    pkt = build_gencoin_transverse_packet(ir_candidate=_IR)
    assert "value_layer" in pkt
    assert pkt["value_layer"]["final_scoring_enabled"] is False
    assert pkt["value_layer"]["inputs_available"]["gencoin_shadow"] is False
    assert pkt["value_layer"]["input_status"]["gencoin_shadow"] == "DEFERRED"


def test_36_f2b_sigma_unchanged_by_shadow():
    sigma = build_sigma_packet(
        {"sigma_pressure": "MEDIUM", "readonly": True, "emits_act": False, "memory_write": False},
        ir_candidate=_IR,
    )
    assert sigma["version"] == "SIGMA_CALIBRATION_PACKET_V1"
    assert sigma["emits_act"] is False


def test_37_f2c_anti_mismatch_not_mutated_by_shadow():
    amp_before = dict(_AMP_LOW)
    build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE,
    )
    assert _AMP_LOW == amp_before


def test_38_f3_thermo_not_mutated_by_shadow():
    thermo_copy = {**_THERMO_STABLE, "scores": dict(_THERMO_STABLE["scores"])}
    build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=thermo_copy,
    )
    assert thermo_copy["stability_state"] == "STABLE"
    assert thermo_copy["scores"]["dissipation_score"] == _THERMO_STABLE["scores"]["dissipation_score"]


# ── Invariant 39: no ACT / verdict / write / mutation ────────────────────────

def test_39_no_act_verdict_write_mutation():
    import json
    gsp_result = _build_default()
    gsp_pkt = gsp_result["gencoin_shadow_packet"]
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR, gencoin_shadow_packet=gsp_pkt)
    dumped = json.dumps({"gsp": gsp_result, "vl": vl_result}, default=str)
    forbidden = ['"emits_act": true', '"emits_verdict": true', '"memory_write": true',
                 '"kernel_mutation": true', '"x108_mutation": true', '"final_scoring_enabled": true']
    for token in forbidden:
        assert token not in dumped, f"Forbidden token {token!r} found"


# ── Invariant 40: OS Trad → IR → Reverse unmodified ─────────────────────────

def test_40_pipeline_observes_only():
    original_final_answer = _TVS_MEDIUM["final_answer"]
    original_intent = _IR["intent_type"]
    build_gencoin_shadow_value_packet(
        sigma_packet=_SIGMA_USABLE,
        anti_mismatch_packet=_AMP_LOW,
        thermodynamics_packet=_THERMO_STABLE,
        ir_candidate=_IR,
        true_voice_snapshot=_TVS_MEDIUM,
    )
    assert _TVS_MEDIUM["final_answer"] == original_final_answer
    assert _IR["intent_type"] == original_intent


# ── Invariant 41: blockchain_enabled == false ─────────────────────────────────

def test_41_blockchain_disabled():
    assert _gsp(_build_default())["blockchain_enabled"] is False


# ── Invariant 42: memory_promotion_enabled == false ───────────────────────────

def test_42_memory_promotion_disabled():
    assert _gsp(_build_default())["memory_promotion_enabled"] is False


# ── Invariant 43: absent gencoin_shadow → value_layer shows DEFERRED ─────────

def test_43_absent_shadow_value_layer_deferred():
    vl_result = build_gencoin_transverse_packet(ir_candidate=_IR)
    vl = vl_result["value_layer"]
    assert vl["inputs_available"]["gencoin_shadow"] is False
    assert vl["input_status"]["gencoin_shadow"] == "DEFERRED"


# ── Invariant 44: graceful degradation on empty inputs ───────────────────────

def test_44_graceful_degradation():
    result = build_gencoin_shadow_value_packet()
    assert "gencoin_shadow_packet" in result
    gsp = result["gencoin_shadow_packet"]
    assert gsp["decision_authority"] == "KX108_ONLY"
    assert gsp["emits_act"] is False
    assert gsp["final_scoring_enabled"] is False
    assert gsp["usable_shadow_value"] is False
    for val in gsp["shadow_scores"].values():
        assert val is None
