"""F2B Sigma Calibration tests — SIGMA_CALIBRATION_PACKET_V1.

28 invariants per F2B spec + additional coverage.

Sigma remains advisory-only. Sigma does not decide. KX108 decides.
Sigma measures signal quality for downstream readonly observers.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_gencoin_transverse_interface import (
    build_sigma_packet,
    build_gencoin_transverse_packet,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

_ADAPTIVE_NORMAL = {
    "sigma_pressure": "LOW",
    "response_size": "MEDIUM",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "can_act": False,
    "can_decide": False,
    "boundary_detected": False,
    "domains": ["ARCHITECTURE_EXPLANATION"],
}

_ADAPTIVE_BOUNDARY = {
    "sigma_pressure": "HIGH",
    "response_size": "BOUNDARY_COMPACT",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "can_act": False,
    "can_decide": False,
    "boundary_detected": True,
    "domains": [],
}

_ADAPTIVE_ARCH = {
    "sigma_pressure": "MEDIUM",
    "response_size": "DEEP",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "can_act": False,
    "can_decide": False,
    "boundary_detected": False,
    "domains": ["ARCHITECTURE_EXPLANATION"],
}

_IR_PRESENT = {
    "intent_type": "pure_response",
    "entities": [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

_TVS_WITH_ANSWER = {
    "final_answer": "Je suis Brody, interface readonly. Architecture Obsidia expliquee.",
    "voice_source": "DOMAIN_RACCORD_ARCHITECTURE",
}

_DR_ARCH = {
    "domains": ["ARCHITECTURE_EXPLANATION"],
    "structural_answer_available": True,
    "write_boundary_required": False,
}

_CHAIN_PASS = {
    "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "material_quality": "USABLE_MATERIAL",
    "query_results_count": 5,
}

_CHAIN_EMPTY: dict = {}


# ── Standard calibrated case ─────────────────────────────────────────────────

def _build_calibrated():
    return build_sigma_packet(
        _ADAPTIVE_ARCH,
        ir_candidate=_IR_PRESENT,
        domain_raccord=_DR_ARCH,
        memory_chain=_CHAIN_PASS,
        true_voice_snapshot=_TVS_WITH_ANSWER,
    )


def _build_boundary():
    return build_sigma_packet(
        _ADAPTIVE_BOUNDARY,
        ir_candidate=_IR_PRESENT,
        domain_raccord={"domains": []},
        memory_chain=_CHAIN_EMPTY,
        true_voice_snapshot=_TVS_WITH_ANSWER,
    )


def _build_insufficient():
    return build_sigma_packet(
        None,
        ir_candidate=None,
        domain_raccord=None,
        memory_chain=None,
        true_voice_snapshot=None,
    )


# ── Invariant 1: sigma_packet exists ─────────────────────────────────────────

def test_01_sigma_packet_exists():
    sp = _build_calibrated()
    assert sp is not None
    assert isinstance(sp, dict)


# ── Invariant 2: version == V1 ───────────────────────────────────────────────

def test_02_version_v1():
    sp = _build_calibrated()
    assert sp["version"] == "SIGMA_CALIBRATION_PACKET_V1"


# ── Invariant 3: mode == SHADOW_READONLY ─────────────────────────────────────

def test_03_mode_shadow_readonly():
    sp = _build_calibrated()
    assert sp["mode"] == "SHADOW_READONLY"


# ── Invariant 4: decision_authority == KX108_ONLY ────────────────────────────

def test_04_decision_authority():
    sp = _build_calibrated()
    assert sp["decision_authority"] == "KX108_ONLY"


# ── Invariant 5: advisory_only == true ───────────────────────────────────────

def test_05_advisory_only():
    sp = _build_calibrated()
    assert sp["advisory_only"] is True


# ── Invariant 6: readonly == true ────────────────────────────────────────────

def test_06_readonly():
    sp = _build_calibrated()
    assert sp["readonly"] is True


# ── Invariant 7: emits_act == false ──────────────────────────────────────────

def test_07_emits_act_false():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert sp["emits_act"] is False


# ── Invariant 8: emits_verdict == false ──────────────────────────────────────

def test_08_emits_verdict_false():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert sp["emits_verdict"] is False


# ── Invariant 9: memory_write == false ───────────────────────────────────────

def test_09_memory_write_false():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert sp["memory_write"] is False


# ── Invariant 10: kernel_mutation == false ───────────────────────────────────

def test_10_kernel_mutation_false():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert sp["kernel_mutation"] is False


# ── Invariant 11: x108_mutation == false ─────────────────────────────────────

def test_11_x108_mutation_false():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert sp["x108_mutation"] is False


# ── Invariant 12: truth_score null or float [0.0, 1.0] ───────────────────────

def test_12_truth_score_bounded():
    sp_cal = _build_calibrated()
    ts = sp_cal["truth_score"]
    assert ts is not None
    assert isinstance(ts, float)
    assert 0.0 <= ts <= 1.0

    sp_insuf = _build_insufficient()
    assert sp_insuf["truth_score"] is None


# ── Invariant 13: sigma_pressure null or bounded string ──────────────────────

def test_13_sigma_pressure_bounded():
    sp = _build_calibrated()
    pressure = sp["sigma_pressure"]
    assert pressure in ("LOW", "MEDIUM", "HIGH", None)


# ── Invariant 14: CALIBRATED_SHADOW_READONLY → usable_for_gencoin == true ────

def test_14_calibrated_usable_for_gencoin():
    sp = _build_calibrated()
    if sp["calibration_status"] == "CALIBRATED_SHADOW_READONLY":
        assert sp["usable_for_gencoin"] is True


# ── Invariant 15: CALIBRATED_SHADOW_READONLY → usable_for_thermodynamics=true

def test_15_calibrated_usable_for_thermodynamics():
    sp = _build_calibrated()
    if sp["calibration_status"] == "CALIBRATED_SHADOW_READONLY":
        assert sp["usable_for_thermodynamics"] is True


# ── Invariant 16: INSUFFICIENT_MATERIAL → usable_for_gencoin == false ────────

def test_16_insufficient_material_usable_false():
    sp = _build_insufficient()
    assert sp["calibration_status"] == "INSUFFICIENT_MATERIAL"
    assert sp["usable_for_gencoin"] is False
    assert sp["usable_for_thermodynamics"] is False


# ── Invariant 17: BOUNDARY_COMPACT → truth_score < 0.50 OR usable=false ─────

def test_17_boundary_compact_truth_score_or_usable_false():
    sp = _build_boundary()
    ts = sp["truth_score"]
    usable = sp["usable_for_gencoin"]
    assert (ts is None or ts < 0.50) or (usable is False), (
        f"BOUNDARY_COMPACT: truth_score={ts}, usable_for_gencoin={usable} — "
        "one of the conditions must hold"
    )


# ── Invariant 18: ARCHITECTURE → truth_score > 0.60 if material sufficient ───

def test_18_architecture_truth_score_high():
    sp = build_sigma_packet(
        _ADAPTIVE_ARCH,
        ir_candidate=_IR_PRESENT,
        domain_raccord=_DR_ARCH,
        memory_chain=_CHAIN_PASS,
        true_voice_snapshot=_TVS_WITH_ANSWER,
    )
    if sp["calibration_status"] == "CALIBRATED_SHADOW_READONLY":
        ts = sp["truth_score"]
        assert ts is not None and ts > 0.60, (
            f"Architecture with sufficient material should give truth_score > 0.60, got {ts}"
        )


# ── Invariant 19: MEMORY_CHAIN_PASS → truth_score > 0.50 ────────────────────

def test_19_memory_chain_pass_truth_score():
    sp = build_sigma_packet(
        _ADAPTIVE_NORMAL,
        ir_candidate=None,
        domain_raccord={"domains": []},
        memory_chain=_CHAIN_PASS,
        true_voice_snapshot=None,
    )
    if sp["calibration_status"] != "INSUFFICIENT_MATERIAL":
        ts = sp["truth_score"]
        assert ts is not None and ts > 0.50, (
            f"MEMORY_CHAIN_PASS should give truth_score > 0.50, got {ts}"
        )


# ── Invariant 20: value_layer always exists ──────────────────────────────────

def test_20_value_layer_exists():
    vl_pkt = build_gencoin_transverse_packet(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_WITH_ANSWER,
        domain_raccord=_DR_ARCH,
        memory_chain=_CHAIN_PASS,
        adaptive_response_policy=_ADAPTIVE_ARCH,
        sigma_packet=_build_calibrated(),
    )
    assert "value_layer" in vl_pkt


# ── Invariant 21: value_layer.final_scoring_enabled == false ─────────────────

def test_21_value_layer_final_scoring_false():
    vl = build_gencoin_transverse_packet(
        sigma_packet=_build_calibrated(),
    )["value_layer"]
    assert vl["final_scoring_enabled"] is False


# ── Invariant 22: all value_layer scores remain null ─────────────────────────

def test_22_value_layer_scores_null():
    vl = build_gencoin_transverse_packet(
        sigma_packet=_build_calibrated(),
    )["value_layer"]
    for k, v in vl["scores"].items():
        assert v is None, f"score {k!r} must be null, got {v!r}"


# ── Invariant 23: value_layer.input_status.sigma reflects calibration_status ─

def test_23_input_status_sigma_reflects_calibration():
    sp = _build_calibrated()
    vl = build_gencoin_transverse_packet(
        ir_candidate=_IR_PRESENT,
        adaptive_response_policy=_ADAPTIVE_ARCH,
        sigma_packet=sp,
    )["value_layer"]
    assert vl["input_status"]["sigma"] == sp["calibration_status"]


# ── Invariant 24: OS Trad → IR → Reverse not modified ────────────────────────

def test_24_pipeline_order_not_modified():
    # sigma_packet has no fields that could intercept OS Trad → IR → Reverse
    sp = _build_calibrated()
    forbidden_intercept = ["os_trad_override", "ir_override", "reverse_override",
                           "pipeline_intercept", "emits_act"]
    for key in forbidden_intercept:
        if key != "emits_act":
            assert key not in sp, f"Forbidden field {key!r} in sigma_packet"
    assert sp["emits_act"] is False


# ── Invariant 25: no ACT / verdict / write / kernel mutation ─────────────────

def test_25_no_act_verdict_write_mutation():
    import json
    sp_cal = _build_calibrated()
    sp_bnd = _build_boundary()
    sp_ins = _build_insufficient()
    vl = build_gencoin_transverse_packet(sigma_packet=sp_cal)

    for payload in [sp_cal, sp_bnd, sp_ins, vl]:
        dumped = json.dumps(payload, default=str)
        forbidden_true = [
            '"emits_act": true', '"emits_verdict": true',
            '"memory_write": true', '"kernel_mutation": true',
            '"x108_mutation": true', '"can_act": true', '"can_decide": true',
        ]
        for token in forbidden_true:
            assert token not in dumped, f"Forbidden token {token!r} found"


# ── Invariant 26: F2A tests still pass (sigma_packet V1 backward-compatible) ─

def test_26_f2a_backward_compatible_no_crash():
    from apps.obsidia_api.brody_gencoin_transverse_interface import (
        build_gencoin_transverse_packet as _bgtp,
    )
    # F2A tests called build_gencoin_transverse_packet without sigma_packet
    pkt = _bgtp(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_WITH_ANSWER,
        domain_raccord=_DR_ARCH,
        trees_snap={"trees_available": True},
        memory_chain=_CHAIN_PASS,
        has_proof_readonly=True,
        adaptive_response_policy=_ADAPTIVE_ARCH,
        # NO sigma_packet — backward-compatible
    )
    vl = pkt["value_layer"]
    assert vl["final_scoring_enabled"] is False
    assert vl["decision_authority"] == "KX108_ONLY"
    assert all(v is None for v in vl["scores"].values())


# ── Invariant 27: no sovereign decision token emitted ────────────────────────

def test_27_no_sovereign_decision_token():
    import json
    sp = _build_calibrated()
    dumped = json.dumps(sp, default=str).upper()
    sovereign_tokens = ['"ALLOW"', '"BLOCK"', '"VERDICT"', '"AUTHORIZE"',
                        '"DECIDE"', '"ACT_GRANTED"', '"KERNEL_PASS"']
    for token in sovereign_tokens:
        assert token not in dumped, f"Sovereign token {token!r} in sigma_packet"


# ── Invariant 28: safe_call absorb — no false calibrated claim ───────────────

def test_28_insufficient_material_not_claimed_calibrated():
    sp = _build_insufficient()
    # If material is insufficient, calibration_status must not be CALIBRATED_SHADOW_READONLY
    assert sp["calibration_status"] != "CALIBRATED_SHADOW_READONLY"
    assert sp["truth_score"] is None
    assert sp["usable_for_gencoin"] is False


# ── Additional: score_components present in calibrated packet ─────────────────

def test_score_components_present_calibrated():
    sp = _build_calibrated()
    sc = sp["score_components"]
    assert "structure_score" in sc
    assert "boundary_score" in sc
    assert "memory_support_score" in sc
    assert "mismatch_penalty" in sc
    assert "material_penalty" in sc


# ── Additional: inputs dict present ──────────────────────────────────────────

def test_inputs_dict_present():
    sp = _build_calibrated()
    assert "inputs" in sp
    assert "has_ir_candidate" in sp["inputs"]
    assert "has_reverse_output" in sp["inputs"]
    assert "has_adaptive_response_policy" in sp["inputs"]
    assert "has_memory_chain" in sp["inputs"]


# ── Additional: features dict present ────────────────────────────────────────

def test_features_dict_present():
    sp = _build_calibrated()
    assert "features" in sp
    f = sp["features"]
    assert "boundary_compact" in f
    assert "architecture_signal" in f
    assert "memory_chain_present" in f
    assert "readonly_boundary_ok" in f
    assert "decorative_coherence_risk" in f


# ── Additional: boundary_compact case usable_for_gencoin=False ───────────────

def test_boundary_compact_usable_for_gencoin_false():
    sp = _build_boundary()
    assert sp["usable_for_gencoin"] is False
    assert sp["usable_for_thermodynamics"] is False


# ── Additional: calibrated case with full material ────────────────────────────

def test_calibrated_case_full_material():
    sp = _build_calibrated()
    assert sp["calibration_status"] == "CALIBRATED_SHADOW_READONLY"
    assert sp["usable_for_gencoin"] is True
    assert sp["usable_for_thermodynamics"] is True
    assert sp["truth_score"] is not None
    assert sp["inputs"]["has_ir_candidate"] is True
    assert sp["inputs"]["has_reverse_output"] is True
    assert sp["inputs"]["has_memory_chain"] is True


# ── Additional: sigma_pressure preserved from adaptive_response_policy ────────

def test_sigma_pressure_reused_not_invented():
    sp = build_sigma_packet({"sigma_pressure": "HIGH", "readonly": True, "emits_act": False,
                              "memory_write": False, "advisory_only": True})
    assert sp["sigma_pressure"] == "HIGH"
    assert sp["truth_score"] is not None  # V1 computes it when material sufficient


# ── Additional: notes always present ─────────────────────────────────────────

def test_notes_present():
    for sp in [_build_calibrated(), _build_boundary(), _build_insufficient()]:
        assert "notes" in sp
        assert isinstance(sp["notes"], list)
        assert len(sp["notes"]) > 0
