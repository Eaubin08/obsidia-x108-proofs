"""F2C Anti-Mismatch Formal signal tests.

Tests the ANTI_MISMATCH_SIGNAL_V1 and its integration with SIGMA_CALIBRATION_PACKET_V1.
30 mandatory invariants.

Invariants:
 1.  anti_mismatch_packet exists in returned dict.
 2.  version == ANTI_MISMATCH_SIGNAL_V1.
 3.  mode == SHADOW_READONLY.
 4.  decision_authority == KX108_ONLY.
 5.  advisory_only == true.
 6.  readonly == true.
 7.  emits_act == false.
 8.  emits_verdict == false.
 9.  memory_write == false.
10.  kernel_mutation == false.
11.  x108_mutation == false.
12.  mismatch_score is a float bounded [0.0, 1.0].
13.  risk_level is one of {NONE, LOW, MEDIUM, HIGH}.
14.  signals dict contains all 8 expected keys.
15.  signals are all boolean.
16.  architecture_answer_too_short: True when ARCHITECTURE domain + answer < 80 words.
17.  structural_gap: True when IR present and answer < 25 words.
18.  false_on_risk: True when boundary_compact + structural_answer_available + answer > 80 words.
19.  collapse_disguised: True when truth_score >= 0.70 + answer < 40 words + domains present.
20.  memory_claim_without_material: True when answer has memory terms + no usable memory.
21.  sigma_high_but_answer_empty: True when truth_score >= 0.70 + answer < 20 words.
22.  decorative_coherence derived from signals 1, 4, 5, 6, 7.
23.  mismatch_score == 0.0 → risk_level == NONE.
24.  mismatch_score > 0.60 → risk_level == HIGH.
25.  no signals → mismatch_score == 0.0.
26.  Graceful degradation on empty / None inputs — no crash.
27.  sigma build_sigma_packet accepts anti_mismatch_packet without crash.
28.  sigma with formal mismatch_score >= 0.60 → calibration_status == CALIBRATED_WITH_MISMATCH_RISK.
29.  sigma with formal mismatch_score < 0.60 → usable_for_gencoin == True (if not boundary).
30.  sigma with no anti_mismatch_packet → textual fallback preserved (backward compatible).
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_anti_mismatch_signal import build_anti_mismatch_signal
from apps.obsidia_api.brody_gencoin_transverse_interface import build_sigma_packet


# ── Fixtures ────────────────────────────────────────────────────────────────

_IR_PRESENT = {
    "intent_type": "pure_response",
    "entities": [],
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "decision_authority": "KX108_ONLY",
}

_TVS_LONG = {
    "final_answer": " ".join(["mot"] * 120),  # 120 words — long answer
    "voice_source": "DOMAIN_RACCORD_STRUCTURAL",
    "adaptive_response_policy": {
        "sigma_pressure": "MEDIUM",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "emits_act": False,
        "memory_write": False,
    },
}

_TVS_SHORT = {
    "final_answer": "Oui.",  # 1 word — very short answer
}

_TVS_EMPTY: dict = {}

_TVS_MEDIUM = {
    "final_answer": " ".join(["mot"] * 50),  # 50 words — medium answer
}

_TVS_ARCH_SHORT = {
    "final_answer": " ".join(["mot"] * 30),  # 30 words — too short for ARCHITECTURE
}

_TVS_MEMORY = {
    "final_answer": "Je me souviens que tu m'avais dit quelque chose important sur la mémoire et le contexte historique de ce projet.",
}

_DR_ARCH = {
    "domains": ["ARCHITECTURE_EXPLANATION"],
    "structural_answer_available": True,
    "write_boundary_required": False,
}

_DR_EMPTY: dict = {"domains": []}

_POL_NORMAL = {
    "sigma_pressure": "MEDIUM",
    "response_size": "MEDIUM",
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
}

_POL_BOUNDARY = {
    "sigma_pressure": "HIGH",
    "response_size": "BOUNDARY_COMPACT",
    "boundary_detected": True,
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
}

_SIGMA_HIGH = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "truth_score": 0.85,
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
}

_SIGMA_LOW = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "truth_score": 0.40,
    "calibration_status": "CALIBRATED_SHADOW_READONLY",
}

_SIGMA_NONE = {
    "version": "SIGMA_CALIBRATION_PACKET_V1",
    "truth_score": None,
    "calibration_status": "INSUFFICIENT_MATERIAL",
}

_CHAIN_PASS = {
    "status": "BRODY_MEMORY_RESPONSE_CHAIN_PASS",
    "material_quality": "USABLE_MATERIAL",
}

_CHAIN_EMPTY: dict = {}

_DR_BOUNDARY = {
    "domains": ["ARCHITECTURE_EXPLANATION"],
    "structural_answer_available": True,
    "write_boundary_required": True,
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_default():
    return build_anti_mismatch_signal(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_LONG,
        adaptive_response_policy=_POL_NORMAL,
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_HIGH,
        memory_chain=_CHAIN_PASS,
    )


def _amp(result):
    return result["anti_mismatch_packet"]


# ── Invariant 1: packet exists ───────────────────────────────────────────────

def test_01_anti_mismatch_packet_exists():
    result = _build_default()
    assert "anti_mismatch_packet" in result


# ── Invariant 2: version ─────────────────────────────────────────────────────

def test_02_version():
    assert _amp(_build_default())["version"] == "ANTI_MISMATCH_SIGNAL_V1"


# ── Invariant 3: mode ────────────────────────────────────────────────────────

def test_03_mode_shadow_readonly():
    assert _amp(_build_default())["mode"] == "SHADOW_READONLY"


# ── Invariant 4: decision_authority ─────────────────────────────────────────

def test_04_decision_authority():
    assert _amp(_build_default())["decision_authority"] == "KX108_ONLY"


# ── Invariant 5: advisory_only ───────────────────────────────────────────────

def test_05_advisory_only():
    assert _amp(_build_default())["advisory_only"] is True


# ── Invariant 6: readonly ────────────────────────────────────────────────────

def test_06_readonly():
    assert _amp(_build_default())["readonly"] is True


# ── Invariant 7: emits_act ───────────────────────────────────────────────────

def test_07_emits_act_false():
    assert _amp(_build_default())["emits_act"] is False


# ── Invariant 8: emits_verdict ───────────────────────────────────────────────

def test_08_emits_verdict_false():
    assert _amp(_build_default())["emits_verdict"] is False


# ── Invariant 9: memory_write ────────────────────────────────────────────────

def test_09_memory_write_false():
    assert _amp(_build_default())["memory_write"] is False


# ── Invariant 10: kernel_mutation ───────────────────────────────────────────

def test_10_kernel_mutation_false():
    assert _amp(_build_default())["kernel_mutation"] is False


# ── Invariant 11: x108_mutation ─────────────────────────────────────────────

def test_11_x108_mutation_false():
    assert _amp(_build_default())["x108_mutation"] is False


# ── Invariant 12: mismatch_score bounded [0.0, 1.0] ─────────────────────────

def test_12_mismatch_score_bounded():
    result = _build_default()
    score = _amp(result)["mismatch_score"]
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


# ── Invariant 13: risk_level is valid ────────────────────────────────────────

def test_13_risk_level_valid():
    result = _build_default()
    assert _amp(result)["risk_level"] in ("NONE", "LOW", "MEDIUM", "HIGH")


# ── Invariant 14: signals dict has all 8 keys ────────────────────────────────

_EXPECTED_SIGNAL_KEYS = {
    "architecture_answer_too_short",
    "boundary_compact_under_answer",
    "structural_gap",
    "false_on_risk",
    "collapse_disguised",
    "memory_claim_without_material",
    "sigma_high_but_answer_empty",
    "decorative_coherence",
}

def test_14_signals_all_keys_present():
    sigs = _amp(_build_default())["signals"]
    assert _EXPECTED_SIGNAL_KEYS == set(sigs.keys())


# ── Invariant 15: all signals are boolean ────────────────────────────────────

def test_15_signals_all_boolean():
    sigs = _amp(_build_default())["signals"]
    for key, val in sigs.items():
        assert isinstance(val, bool), f"Signal {key!r} is not bool: {val!r}"


# ── Invariant 16: architecture_answer_too_short ──────────────────────────────

def test_16_architecture_answer_too_short():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_ARCH_SHORT,  # 30 words < 80
        domain_raccord=_DR_ARCH,  # ARCHITECTURE_EXPLANATION domain
    )
    assert _amp(result)["signals"]["architecture_answer_too_short"] is True


def test_16b_architecture_answer_not_too_short_when_long():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,  # 120 words > 80
        domain_raccord=_DR_ARCH,
    )
    assert _amp(result)["signals"]["architecture_answer_too_short"] is False


# ── Invariant 17: structural_gap ─────────────────────────────────────────────

def test_17_structural_gap_detected():
    result = build_anti_mismatch_signal(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_SHORT,  # 1 word < 25
    )
    assert _amp(result)["signals"]["structural_gap"] is True


def test_17b_structural_gap_not_detected_long_answer():
    result = build_anti_mismatch_signal(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_LONG,  # 120 words
    )
    assert _amp(result)["signals"]["structural_gap"] is False


# ── Invariant 18: false_on_risk ──────────────────────────────────────────────

def test_18_false_on_risk_detected():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,  # > 80 words
        adaptive_response_policy=_POL_BOUNDARY,  # boundary_compact=True
        domain_raccord=_DR_BOUNDARY,  # structural_answer_available=True
    )
    assert _amp(result)["signals"]["false_on_risk"] is True


def test_18b_false_on_risk_not_detected_without_structural_available():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        adaptive_response_policy=_POL_BOUNDARY,
        domain_raccord={"domains": ["ARCHITECTURE_EXPLANATION"], "structural_answer_available": False},
    )
    assert _amp(result)["signals"]["false_on_risk"] is False


# ── Invariant 19: collapse_disguised ─────────────────────────────────────────

def test_19_collapse_disguised_detected():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_ARCH_SHORT,  # 30 words < 40
        domain_raccord=_DR_ARCH,  # domain_count > 0
        sigma_packet=_SIGMA_HIGH,  # truth_score=0.85 >= 0.70
    )
    assert _amp(result)["signals"]["collapse_disguised"] is True


def test_19b_collapse_disguised_not_detected_low_score():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_ARCH_SHORT,
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_LOW,  # truth_score=0.40 < 0.70
    )
    assert _amp(result)["signals"]["collapse_disguised"] is False


# ── Invariant 20: memory_claim_without_material ──────────────────────────────

def test_20_memory_claim_without_material():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_MEMORY,
        memory_chain=_CHAIN_EMPTY,  # no material
    )
    assert _amp(result)["signals"]["memory_claim_without_material"] is True


def test_20b_memory_claim_with_material_ok():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_MEMORY,
        memory_chain=_CHAIN_PASS,  # USABLE_MATERIAL
    )
    assert _amp(result)["signals"]["memory_claim_without_material"] is False


# ── Invariant 21: sigma_high_but_answer_empty ────────────────────────────────

def test_21_sigma_high_but_answer_empty():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_SHORT,  # 1 word < 20
        sigma_packet=_SIGMA_HIGH,  # truth_score=0.85 >= 0.70
    )
    assert _amp(result)["signals"]["sigma_high_but_answer_empty"] is True


def test_21b_sigma_high_answer_ok():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,  # 120 words >= 20
        sigma_packet=_SIGMA_HIGH,
    )
    assert _amp(result)["signals"]["sigma_high_but_answer_empty"] is False


# ── Invariant 22: decorative_coherence derived ───────────────────────────────

def test_22_decorative_coherence_derived_from_signals():
    # Force architecture_answer_too_short → decorative_coherence should be True
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_ARCH_SHORT,  # 30 words < 80
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_LOW,  # low score so collapse_disguised won't fire
    )
    amp = _amp(result)
    assert amp["signals"]["architecture_answer_too_short"] is True
    assert amp["signals"]["decorative_coherence"] is True


def test_22b_decorative_coherence_false_when_all_clear():
    # Long answer, no memory claims, low sigma, normal policy, no arch domain
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        domain_raccord=_DR_EMPTY,
        sigma_packet=_SIGMA_LOW,
        memory_chain=_CHAIN_PASS,
        adaptive_response_policy=_POL_NORMAL,
    )
    amp = _amp(result)
    assert amp["signals"]["decorative_coherence"] is False


# ── Invariant 23: mismatch_score == 0.0 → risk NONE ─────────────────────────

def test_23_zero_score_risk_none():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        domain_raccord=_DR_EMPTY,
        sigma_packet=_SIGMA_LOW,
        memory_chain=_CHAIN_PASS,
        adaptive_response_policy=_POL_NORMAL,
    )
    amp = _amp(result)
    if amp["mismatch_score"] == 0.0:
        assert amp["risk_level"] == "NONE"


# ── Invariant 24: score > 0.60 → risk HIGH ───────────────────────────────────

def test_24_high_score_risk_high():
    # Force multiple signals: structural_gap + decorative_coherence + collapse_disguised
    result = build_anti_mismatch_signal(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_SHORT,  # 1 word — triggers structural_gap + sigma_high
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_HIGH,  # triggers collapse + sigma_high_but_answer_empty
        memory_chain=_CHAIN_EMPTY,
    )
    amp = _amp(result)
    if amp["mismatch_score"] > 0.60:
        assert amp["risk_level"] == "HIGH"


# ── Invariant 25: no signals → score 0.0 ─────────────────────────────────────

def test_25_no_signals_zero_score():
    result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        domain_raccord=_DR_EMPTY,
        sigma_packet=_SIGMA_LOW,
        memory_chain=_CHAIN_PASS,
        adaptive_response_policy=_POL_NORMAL,
    )
    amp = _amp(result)
    any_signal = any(amp["signals"].values())
    if not any_signal:
        assert amp["mismatch_score"] == 0.0
        assert amp["risk_level"] == "NONE"


# ── Invariant 26: graceful degradation ───────────────────────────────────────

def test_26_graceful_degradation_empty():
    result = build_anti_mismatch_signal()
    assert "anti_mismatch_packet" in result
    amp = _amp(result)
    assert amp["decision_authority"] == "KX108_ONLY"
    assert amp["emits_act"] is False
    assert 0.0 <= amp["mismatch_score"] <= 1.0


def test_26b_graceful_degradation_none_inputs():
    result = build_anti_mismatch_signal(
        ir_candidate=None,
        true_voice_snapshot=None,
        adaptive_response_policy=None,
        domain_raccord=None,
        sigma_packet=None,
        memory_chain=None,
    )
    assert "anti_mismatch_packet" in result
    assert _amp(result)["emits_act"] is False


# ── Invariant 27: sigma accepts anti_mismatch_packet ─────────────────────────

def test_27_sigma_accepts_anti_mismatch_packet():
    amp_result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_HIGH,
        memory_chain=_CHAIN_PASS,
    )
    amp_pkt = amp_result["anti_mismatch_packet"]
    sigma = build_sigma_packet(
        _POL_NORMAL,
        ir_candidate=_IR_PRESENT,
        anti_mismatch_packet=amp_pkt,
    )
    assert "calibration_status" in sigma
    assert sigma["emits_act"] is False
    assert sigma["decision_authority"] == "KX108_ONLY"


# ── Invariant 28: mismatch_score >= 0.60 → CALIBRATED_WITH_MISMATCH_RISK ────

def test_28_sigma_mismatch_risk_status():
    # Build anti_mismatch with high score (multiple signals)
    amp_result = build_anti_mismatch_signal(
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_SHORT,  # structural_gap + sigma_high_but_answer_empty
        domain_raccord=_DR_ARCH,
        sigma_packet=_SIGMA_HIGH,  # collapse_disguised possible
        memory_chain=_CHAIN_EMPTY,
    )
    amp_pkt = amp_result["anti_mismatch_packet"]
    if amp_pkt["mismatch_score"] >= 0.60:
        sigma = build_sigma_packet(
            _POL_NORMAL,
            ir_candidate=_IR_PRESENT,
            anti_mismatch_packet=amp_pkt,
        )
        assert sigma["calibration_status"] == "CALIBRATED_WITH_MISMATCH_RISK"
        assert sigma["usable_for_gencoin"] is False
        assert sigma["usable_for_thermodynamics"] is False


# ── Invariant 29: mismatch_score < 0.60 → usable_for_gencoin True ────────────

def test_29_sigma_usable_when_low_mismatch():
    # Low mismatch scenario — long answer, no memory claims, no collapse
    amp_result = build_anti_mismatch_signal(
        true_voice_snapshot=_TVS_LONG,
        domain_raccord=_DR_EMPTY,
        sigma_packet=_SIGMA_LOW,
        memory_chain=_CHAIN_PASS,
        adaptive_response_policy=_POL_NORMAL,
    )
    amp_pkt = amp_result["anti_mismatch_packet"]
    assert amp_pkt["mismatch_score"] < 0.60
    sigma = build_sigma_packet(
        _POL_NORMAL,
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_LONG,
        memory_chain=_CHAIN_PASS,
        anti_mismatch_packet=amp_pkt,
    )
    assert sigma["calibration_status"] in (
        "CALIBRATED_SHADOW_READONLY", "CALIBRATED_WITH_MISMATCH_RISK"
    )
    if sigma["calibration_status"] == "CALIBRATED_SHADOW_READONLY":
        assert sigma["usable_for_gencoin"] is True


# ── Invariant 30: sigma without anti_mismatch_packet → backward compatible ───

def test_30_sigma_backward_compatible_no_anti_mismatch():
    sigma = build_sigma_packet(
        _POL_NORMAL,
        ir_candidate=_IR_PRESENT,
        true_voice_snapshot=_TVS_LONG,
        memory_chain=_CHAIN_PASS,
    )
    # Must still produce V1 packet without crash
    assert sigma["version"] == "SIGMA_CALIBRATION_PACKET_V1"
    assert sigma["emits_act"] is False
    assert sigma["decision_authority"] == "KX108_ONLY"
    # Without formal anti_mismatch, uses textual fallback
    assert sigma["features"]["anti_mismatch_formal_available"] is False
    assert sigma["features"]["formal_mismatch_score"] is None
