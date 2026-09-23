"""F2A Transverse Value Interface smoke tests.

Tests the GENCOIN_TRANSVERSE_INTERFACE_V0 and SIGMA_CALIBRATION_PACKET_V0
invariants in isolation (no live API required).

18 invariants per F2A spec:
 1.  value_layer exists in packet.
 2.  value_layer.mode == SHADOW_READONLY.
 3.  value_layer.final_scoring_enabled == false.
 4.  All Gencoin scores remain null.
 5.  decision_authority == KX108_ONLY.
 6.  emits_act == false.
 7.  emits_verdict == false.
 8.  memory_write == false.
 9.  kernel_mutation == false.
10.  x108_mutation == false.
11.  sigma_packet exists when built.
12.  sigma_packet.usable_for_gencoin == false.
13.  sigma_packet.usable_for_thermodynamics == false.
14.  No ACT / ALLOW / BLOCK / VERDICT emitted by any module.
15.  IR -> Sigma -> Reverse ordering preserved (inputs_available reflects presence).
16.  34 arbres textual and formal computation are distinguished.
17.  trees_formal_computation is always False/DEFERRED.
18.  safe_call_snapshot degrades gracefully on bad input (no crash).
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_gencoin_transverse_interface import (
    build_gencoin_transverse_packet,
    build_sigma_packet,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

_IR = {
    "intent_type": "pure_response",
    "entities": [],
    "constraints": [],
    "risk_flags": [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "memory_write": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
}

_TVS = {
    "final_answer": "Je suis Brody, interface structuree readonly.",
    "voice_source": "DOMAIN_RACCORD_STRUCTURAL",
    "sigma_pressure": "LOW",
    "adaptive_response_policy": {
        "sigma_pressure": "LOW",
        "response_size": "MEDIUM",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "emits_act": False,
        "memory_write": False,
    },
}

_DR = {
    "domains": ["ARCHITECTURE_EXPLANATION"],
    "structural_answer": "Les 34 arbres sont un signal cognitif readonly.",
    "structural_answer_available": True,
    "voice_mode": "DOMAIN_RACCORD_ARCHITECTURE",
    "write_boundary_required": False,
}

_TREES = {
    "trees_available": True,
    "tree_policy_status": "TREE_POLICY_PASS",
}

_CHAIN_PASS = {
    "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "material_quality": "USABLE_MATERIAL",
    "query_results_count": 3,
}

_CHAIN_EMPTY: dict = {}

_ADAPTIVE = {
    "sigma_pressure": "LOW",
    "response_size": "MEDIUM",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "can_act": False,
    "can_decide": False,
}


# ── Helper ───────────────────────────────────────────────────────────────────

def _build_full():
    return build_gencoin_transverse_packet(
        ir_candidate=_IR,
        true_voice_snapshot=_TVS,
        domain_raccord=_DR,
        trees_snap=_TREES,
        memory_chain=_CHAIN_PASS,
        has_proof_readonly=True,
        adaptive_response_policy=_ADAPTIVE,
    )


# ── Invariant 1: value_layer exists ──────────────────────────────────────────

def test_01_value_layer_exists():
    pkt = _build_full()
    assert "value_layer" in pkt, "value_layer must be present in packet"


# ── Invariant 2: mode == SHADOW_READONLY ─────────────────────────────────────

def test_02_value_layer_mode_shadow_readonly():
    vl = _build_full()["value_layer"]
    assert vl["mode"] == "SHADOW_READONLY"


# ── Invariant 3: final_scoring_enabled == false ───────────────────────────────

def test_03_final_scoring_disabled():
    vl = _build_full()["value_layer"]
    assert vl["final_scoring_enabled"] is False


# ── Invariant 4: all Gencoin scores remain null ───────────────────────────────

def test_04_all_scores_null():
    scores = _build_full()["value_layer"]["scores"]
    null_score_keys = [
        "cognitive_value", "proof_value", "reuse_value", "memory_value",
        "attention_cost", "energy_cost", "stability_value", "economic_projection",
    ]
    for key in null_score_keys:
        assert scores[key] is None, f"Score {key!r} must be null, got {scores[key]!r}"


# ── Invariant 5: decision_authority == KX108_ONLY ────────────────────────────

def test_05_decision_authority_kx108_only():
    vl = _build_full()["value_layer"]
    assert vl["decision_authority"] == "KX108_ONLY"


# ── Invariant 6: emits_act == false ──────────────────────────────────────────

def test_06_emits_act_false():
    vl = _build_full()["value_layer"]
    assert vl["emits_act"] is False


# ── Invariant 7: emits_verdict == false ──────────────────────────────────────

def test_07_emits_verdict_false():
    vl = _build_full()["value_layer"]
    assert vl["emits_verdict"] is False


# ── Invariant 8: memory_write == false ───────────────────────────────────────

def test_08_memory_write_false():
    vl = _build_full()["value_layer"]
    assert vl["memory_write"] is False


# ── Invariant 9: kernel_mutation == false ────────────────────────────────────

def test_09_kernel_mutation_false():
    vl = _build_full()["value_layer"]
    assert vl["kernel_mutation"] is False


# ── Invariant 10: x108_mutation == false ─────────────────────────────────────

def test_10_x108_mutation_false():
    vl = _build_full()["value_layer"]
    assert vl["x108_mutation"] is False


# ── Invariant 11: sigma_packet exists when built (V1 since F2B) ──────────────

def test_11_sigma_packet_exists():
    sp = build_sigma_packet(_ADAPTIVE)
    assert sp is not None
    assert "version" in sp
    # F2B upgraded sigma from V0 to V1 — version must be V1
    assert sp["version"] == "SIGMA_CALIBRATION_PACKET_V1"


# ── Invariant 12: sigma_packet.usable_for_gencoin follows calibration_status ─

def test_12_sigma_packet_usable_for_gencoin_false():
    # F2B: usable_for_gencoin depends on calibration_status.
    # INSUFFICIENT_MATERIAL → False; CALIBRATED_SHADOW_READONLY → True;
    # CALIBRATED_BOUNDARY_ONLY → False.
    # With None input → INSUFFICIENT_MATERIAL → False.
    sp_insuf = build_sigma_packet(None)
    assert sp_insuf["usable_for_gencoin"] is False

    # Boundary case → CALIBRATED_BOUNDARY_ONLY → False.
    sp_boundary = build_sigma_packet({"response_size": "BOUNDARY_COMPACT",
                                      "boundary_detected": True, "readonly": True,
                                      "emits_act": False, "memory_write": False})
    assert sp_boundary["usable_for_gencoin"] is False


# ── Invariant 13: sigma_packet.usable_for_thermodynamics follows status ───────

def test_13_sigma_packet_usable_for_thermodynamics_false():
    # F2B: same logic as usable_for_gencoin.
    sp_insuf = build_sigma_packet(None)
    assert sp_insuf["usable_for_thermodynamics"] is False

    sp_boundary = build_sigma_packet({"response_size": "BOUNDARY_COMPACT",
                                      "boundary_detected": True, "readonly": True,
                                      "emits_act": False, "memory_write": False})
    assert sp_boundary["usable_for_thermodynamics"] is False


# ── Invariant 14: no ACT / ALLOW / BLOCK / VERDICT anywhere ─────────────────

def test_14_no_act_verdict_allow_block():
    pkt = _build_full()
    sp = build_sigma_packet(_ADAPTIVE)
    import json
    dumped = json.dumps({"pkt": pkt, "sp": sp}, default=str)
    forbidden = ['"emits_act": true', '"emits_verdict": true',
                 '"can_act": true', '"can_decide": true',
                 '"ALLOW"', '"BLOCK"', '"VERDICT"']
    for token in forbidden:
        assert token not in dumped, f"Forbidden token {token!r} found in packet"


# ── Invariant 15: inputs_available reflects pipeline presence ────────────────

def test_15_inputs_available_hooks():
    vl = _build_full()["value_layer"]
    ia = vl["inputs_available"]
    # IR present
    assert ia["ir_candidate"] is True
    # Sigma: adaptive_response_policy has sigma_pressure
    assert ia["sigma"] is True
    # Thermodynamics always False
    assert ia["thermodynamics"] is False
    # Memory: chain PASS
    assert ia["memory"] is True
    # Proof: has_proof_readonly=True
    assert ia["proof"] is True
    # Reverse OS: tvs has final_answer
    assert ia["reverse_os"] is True


# ── Invariant 16: trees_textual_signal and trees_formal_computation distinguished

def test_16_trees_distinction():
    vl = _build_full()["value_layer"]
    ia = vl["inputs_available"]
    ist = vl["input_status"]
    # Must have separate keys
    assert "trees_textual_signal" in ia
    assert "trees_formal_computation" in ia
    assert "trees_textual_signal" in ist
    assert "trees_formal_computation" in ist
    # They must be different values (textual may be True, formal always False)
    assert ia["trees_textual_signal"] is True   # ARCHITECTURE_EXPLANATION domain -> True
    assert ia["trees_formal_computation"] is False


# ── Invariant 17: trees_formal_computation always False / DEFERRED ────────────

def test_17_trees_formal_computation_always_deferred():
    # Even if we pass trees_snap with formal computation data, formal stays False
    vl_with_trees = build_gencoin_transverse_packet(
        trees_snap={"trees_available": True, "formal_computation_result": "some_data"},
        domain_raccord={"domains": []},
    )["value_layer"]
    assert vl_with_trees["inputs_available"]["trees_formal_computation"] is False
    assert vl_with_trees["input_status"]["trees_formal_computation"] == "DEFERRED"


# ── Invariant 18: graceful degradation on bad/empty input ────────────────────

def test_18_graceful_degradation_no_crash():
    # Empty inputs — must not crash, must return valid packet
    pkt = build_gencoin_transverse_packet()
    assert "value_layer" in pkt
    vl = pkt["value_layer"]
    assert vl["final_scoring_enabled"] is False
    assert vl["decision_authority"] == "KX108_ONLY"
    assert all(v is None for v in vl["scores"].values())

    # None inputs
    pkt2 = build_gencoin_transverse_packet(
        ir_candidate=None, true_voice_snapshot=None,
        domain_raccord=None, trees_snap=None, memory_chain=None,
    )
    assert pkt2["value_layer"]["emits_act"] is False

    # Bad sigma packet input
    sp = build_sigma_packet(None)
    assert sp["usable_for_gencoin"] is False
    assert sp["truth_score"] is None


# ── Additional: sigma_packet reuses existing sigma_pressure ──────────────────

def test_sigma_packet_reuses_sigma_pressure():
    pol = {"sigma_pressure": "HIGH", "decision_authority": "KX108_ONLY"}
    sp = build_sigma_packet(pol)
    assert sp["sigma_pressure"] == "HIGH"
    # F2B: V1 computes truth_score when material is sufficient.
    # With advisory_policy present (has_adaptive=True), V1 calibrates.
    # truth_score is a bounded float (not None) or None only if INSUFFICIENT_MATERIAL.
    if sp["calibration_status"] == "INSUFFICIENT_MATERIAL":
        assert sp["truth_score"] is None
    else:
        assert sp["truth_score"] is not None
        assert isinstance(sp["truth_score"], float)
        assert 0.0 <= sp["truth_score"] <= 1.0


def test_sigma_packet_no_sigma_pressure_stays_none():
    sp = build_sigma_packet({})
    assert sp["sigma_pressure"] is None


# ── Additional: no memory present → memory hook False ────────────────────────

def test_memory_hook_false_when_no_chain():
    vl = build_gencoin_transverse_packet(
        ir_candidate=_IR,
        memory_chain=_CHAIN_EMPTY,
    )["value_layer"]
    assert vl["inputs_available"]["memory"] is False
    assert vl["input_status"]["memory"] == "NO_MATERIAL"
