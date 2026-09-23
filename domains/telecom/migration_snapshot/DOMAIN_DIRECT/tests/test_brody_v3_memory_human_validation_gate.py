"""
test_brody_v3_memory_human_validation_gate — V3 Block 3D
22 tests couvrant les invariants readonly, la securite, et les statuts de
validation. DECISION_AUTHORITY=KX108_ONLY. PATCH=YES_BLOCK_3D_ONLY. COMMIT=NO.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_memory_human_validation_gate import (
    BrodyMemoryHumanValidationGate,
    prepare_validation_decision,
    VSTATUS_PENDING_REVIEW,
    VSTATUS_REJECT_ADVERSARIAL,
    VSTATUS_EDIT_REQUIRED,
    VSTATUS_HOLD_REVIEW,
    VSTATUS_ELIGIBLE_FUTURE,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_candidate(
    *,
    candidate_id: str = "MC_ABCDEF1234567890",
    trace_id: str = "TR_ABCDEF1234567890",
    session_id: str = "sess_test_001",
    candidate_type: str = "education_candidate",
    is_adversarial: bool = False,
    priority_score: float = 0.55,
    memory_relevance_score: float = 0.5,
    useful_path_tags: list | None = None,
    dead_path_tags: list | None = None,
    weak_signal_tags: list | None = None,
    contradiction_tags: list | None = None,
    missing_proof_tags: list | None = None,
    risk_flags: list | None = None,
    domain: str = "bank",
    fastpath_triggered: bool = False,
    secret_in_msg: bool = False,
    secret_in_resp: bool = False,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "trace_id": trace_id,
        "session_id": session_id,
        "timestamp": "2026-06-15T19:30:00Z",
        "block": "V3_BLOCK_3B",
        "candidate_type": candidate_type,
        "candidate_summary": f"[{candidate_type}] domain={domain}",
        "candidate_payload": {
            "message_excerpt": "Quel est le solde de mon compte ?",
            "response_excerpt": "Votre solde est de 1500 EUR. Validation humaine requise.",
            "domain_detected": domain,
            "intent_type": "advisory",
            "path_coherence_score": 0.75,
            "fastpath_triggered": fastpath_triggered,
            "graphiti_allowed": False,
        },
        "domain_tags": [domain],
        "balance_tags": {
            "balance_memoire": {"tension": 0.5, "seuil_depasse": False, "priority": 4},
            "balance_risque": {"tension": 0.6 if is_adversarial else 0.1,
                               "seuil_depasse": is_adversarial, "priority": 0},
        },
        "point_cloud_21d": {
            "axes": {"axis_01_domain": 0.9, "axis_13_memory": 0.5},
            "active_layers": ["authority_layer", "cic_core_layer"],
        },
        "weak_signal_tags": weak_signal_tags or [],
        "dead_path_tags": dead_path_tags or (["adversarial_excluded"] if is_adversarial else []),
        "useful_path_tags": useful_path_tags or ([] if is_adversarial else ["coherent_path:0.75"]),
        "missing_proof_tags": missing_proof_tags or [],
        "contradiction_tags": contradiction_tags or [],
        "risk_flags": risk_flags or (["adversarial_prompt"] if is_adversarial else []),
        "priority_score": priority_score,
        "memory_relevance_score": memory_relevance_score,
        "human_validation_required": True,
        "human_validation_state": "pending",
        "readonly": True,
        "canonical_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": "KX108_ONLY",
        "advisory_only": True,
        "security_flags": {
            "is_adversarial": is_adversarial,
            "secret_in_msg": secret_in_msg,
            "secret_in_resp": secret_in_resp,
            "scrubbed": False,
        },
    }


def _make_ep(candidate_id: str = "MC_ABCDEF1234567890") -> dict:
    return {
        "education_packet_id": "EP_TEST1234567890AB",
        "candidate_id": candidate_id,
        "readonly": True,
        "canonical_write": False,
        "decision_authority": "KX108_ONLY",
    }


def _make_rp(candidate_id: str = "MC_ABCDEF1234567890") -> dict:
    return {
        "replay_packet_id": "RP_TEST1234567890AB",
        "candidate_id": candidate_id,
        "readonly": True,
        "canonical_write": False,
        "decision_authority": "KX108_ONLY",
    }


_STD = _make_candidate()
_ADV = _make_candidate(
    candidate_type="adversarial_rejection_candidate",
    is_adversarial=True,
    priority_score=0.0,
    useful_path_tags=[],
)
_MISSING = _make_candidate(
    candidate_type="boundary_candidate",
    missing_proof_tags=["IBAN manquant", "solde non verifie"],
)
_CONTRADICTION = _make_candidate(
    candidate_type="education_candidate",
    contradiction_tags=["reponse_contradicts_previous_turn", "ordre_incoherent"],
)
_WEAK = _make_candidate(
    candidate_type="weak_signal_candidate",
    weak_signal_tags=["signal_faible_gps", "pattern_inhabituel"],
)
_REPLAY = _make_candidate(candidate_type="replay_candidate")

GATE = BrodyMemoryHumanValidationGate()


def _prepare(c: dict = _STD) -> dict:
    return GATE.prepare(
        memory_candidate=c,
        education_packet=_make_ep(c.get("candidate_id", "MC_ABCDEF1234567890")),
        replay_packet=_make_rp(c.get("candidate_id", "MC_ABCDEF1234567890")),
    )


# ── Test 1 — validation_packet_id present ────────────────────────────────────

def test_validation_packet_id_present():
    vd = _prepare()
    assert "validation_packet_id" in vd
    assert vd["validation_packet_id"].startswith("VD_")


# ── Test 2 — candidate_id conserve ───────────────────────────────────────────

def test_candidate_id_conserved():
    vd = _prepare()
    assert vd["candidate_id"] == "MC_ABCDEF1234567890"


# ── Test 3 — readonly=True ────────────────────────────────────────────────────

def test_readonly_true():
    vd = _prepare()
    assert vd["readonly"] is True


# ── Test 4 — canonical_write=False ───────────────────────────────────────────

def test_canonical_write_false():
    vd = _prepare()
    assert vd["canonical_write"] is False


# ── Test 5 — graphiti_write=False ────────────────────────────────────────────

def test_graphiti_write_false():
    vd = _prepare()
    assert vd["graphiti_write"] is False


# ── Test 6 — neo4j_write=False ───────────────────────────────────────────────

def test_neo4j_write_false():
    vd = _prepare()
    assert vd["neo4j_write"] is False


# ── Test 7 — kernel_mutation=False ───────────────────────────────────────────

def test_kernel_mutation_false():
    vd = _prepare()
    assert vd["kernel_mutation"] is False


# ── Test 8 — emits_act=False ─────────────────────────────────────────────────

def test_emits_act_false():
    vd = _prepare()
    assert vd["emits_act"] is False


# ── Test 9 — allowed_to_decide=False ─────────────────────────────────────────

def test_allowed_to_decide_false():
    vd = _prepare()
    assert vd["allowed_to_decide"] is False


# ── Test 10 — allowed_to_act=False ───────────────────────────────────────────

def test_allowed_to_act_false():
    vd = _prepare()
    assert vd["allowed_to_act"] is False


# ── Test 11 — decision_authority=KX108_ONLY ──────────────────────────────────

def test_decision_authority_kx108_only():
    vd = _prepare()
    assert vd["decision_authority"] == "KX108_ONLY"


# ── Test 12 — human_validation_required=True ─────────────────────────────────

def test_human_validation_required_true():
    vd = _prepare()
    assert vd["human_validation_required"] is True
    assert vd["human_validation_state"] == "pending"


# ── Test 13 — adversarial candidate → reject_adversarial ─────────────────────

def test_adversarial_candidate_reject_adversarial():
    vd = _prepare(_ADV)
    assert vd["validation_status"] == VSTATUS_REJECT_ADVERSARIAL
    assert vd["security_flags"]["is_adversarial"] is True
    assert vd["canonical_write"] is False
    assert vd["emits_act"] is False
    assert vd["allowed_to_act"] is False
    assert len(vd["rejection_flags"]) > 0


# ── Test 14 — missing_data/boundary candidate → hold_review ──────────────────

def test_missing_data_boundary_hold_review():
    vd = _prepare(_MISSING)
    assert vd["validation_status"] == VSTATUS_HOLD_REVIEW
    assert vd["canonical_write"] is False
    assert vd["human_validation_required"] is True


# ── Test 15 — contradiction candidate → edit_required ────────────────────────

def test_contradiction_candidate_edit_required():
    vd = _prepare(_CONTRADICTION)
    assert vd["validation_status"] == VSTATUS_EDIT_REQUIRED
    assert len(vd["edit_required_fields"]) > 0
    assert vd["canonical_write"] is False


# ── Test 16 — clean education candidate → eligible_for_future_human_acceptance

def test_clean_education_candidate_eligible():
    vd = _prepare(_STD)
    assert vd["validation_status"] == VSTATUS_ELIGIBLE_FUTURE
    assert vd["canonical_write"] is False
    assert vd["canon_candidate_allowed"] is False
    assert vd["allowed_to_act"] is False


# ── Test 17 — clean replay candidate → eligible_for_future_human_acceptance ──

def test_clean_replay_candidate_eligible():
    vd = _prepare(_REPLAY)
    assert vd["validation_status"] == VSTATUS_ELIGIBLE_FUTURE
    assert vd["canonical_write"] is False
    assert vd["allowed_to_act"] is False


# ── Test 18 — weak_signal candidate → hold_review ────────────────────────────

def test_weak_signal_candidate_hold_review():
    vd = _prepare(_WEAK)
    assert vd["validation_status"] == VSTATUS_HOLD_REVIEW
    assert vd["canonical_write"] is False
    assert vd["human_validation_required"] is True


# ── Test 19 — no auto accept ──────────────────────────────────────────────────

def test_no_auto_accept():
    """eligible_for_future_human_acceptance still requires explicit human action."""
    vd = _prepare(_STD)
    assert vd["validation_status"] == VSTATUS_ELIGIBLE_FUTURE
    # Must still require human validation — never auto-promoted
    assert vd["human_validation_required"] is True
    assert vd["human_validation_state"] == "pending"
    assert vd["canon_candidate_allowed"] is False
    assert vd["canonical_write"] is False
    # Action must be PRESENT_TO_HUMAN_VALIDATOR, not an automatic write
    assert vd["validation_action"] == "PRESENT_TO_HUMAN_VALIDATOR"


# ── Test 20 — no canonical write even when eligible ──────────────────────────

def test_no_canonical_write_even_when_eligible():
    for ctype in ("education_candidate", "replay_candidate", "useful_path_candidate"):
        c = _make_candidate(candidate_type=ctype)
        vd = _prepare(c)
        assert vd["canonical_write"] is False, f"canonical_write=True pour {ctype}"
        assert vd["canon_candidate_allowed"] is False
        assert vd["graphiti_write"] is False
        assert vd["neo4j_write"] is False
        assert vd["kernel_mutation"] is False
        assert vd["emits_act"] is False
        assert vd["allowed_to_act"] is False


# ── Test 21 — no secret capture ──────────────────────────────────────────────

def test_no_secret_capture():
    c = _make_candidate(secret_in_msg=True)
    c["candidate_payload"]["message_excerpt"] = "API_KEY=sk-ABCDEF123456 leak"
    vd = _prepare(c)
    text = str(vd.get("validation_reason", "")) + str(vd.get("required_human_action", ""))
    assert "sk-ABCDEF123456" not in text
    assert vd["canonical_write"] is False
    # secret detected → reject_adversarial
    assert vd["validation_status"] == VSTATUS_REJECT_ADVERSARIAL


# ── Test 22 — no raw private token stored ────────────────────────────────────

def test_no_raw_private_token_stored():
    c = _make_candidate()
    c["candidate_payload"]["response_excerpt"] = "Bearer eyJhbGciOiJSUzI1NiJ9.abc.xyz"
    vd = _prepare(c)
    text = str(vd)
    assert "eyJhbGciOiJSUzI1NiJ9" not in text
    assert vd["canonical_write"] is False
    # token in response → reject_adversarial (secret policy)
    assert vd["validation_status"] == VSTATUS_REJECT_ADVERSARIAL


# ── Test 3F_repair_A — SECRET_INJECTION_ATTEMPT → reject_adversarial ─────────

def test_3f_repair_secret_injection_attempt_rejected():
    """Block 3F repair: candidate with SECRET_INJECTION_ATTEMPT in risk_flags → reject_adversarial."""
    c = _make_candidate(candidate_type="education_candidate")
    c["risk_flags"] = ["SECRET_INJECTION_ATTEMPT"]
    vd = _prepare(c)
    assert vd["validation_status"] == VSTATUS_REJECT_ADVERSARIAL, (
        f"SECRET_INJECTION_ATTEMPT doit produire reject_adversarial, obtenu: {vd['validation_status']}"
    )
    assert vd["canon_candidate_allowed"] is False
    assert vd["canonical_write"] is False
    assert vd["allowed_to_act"] is False


# ── Test 3F_repair_B — eligible non produit si secret flag positionné ─────────

def test_3f_repair_no_eligible_on_secret_flag():
    """Block 3F repair: eligible_for_future_human_acceptance never returned when secret flags set."""
    # secret_in_msg=True via security_flags
    c = _make_candidate(secret_in_msg=True)
    vd = _prepare(c)
    assert vd["validation_status"] != VSTATUS_ELIGIBLE_FUTURE, (
        "eligible_for_future_human_acceptance ne doit jamais être produit si secret_in_msg=True"
    )
    assert vd["validation_status"] == VSTATUS_REJECT_ADVERSARIAL
    assert vd["canonical_write"] is False


# ── Test bonus — module-level function ───────────────────────────────────────

def test_prepare_validation_decision_module_function():
    vd = prepare_validation_decision(memory_candidate=_STD)
    assert vd["validation_packet_id"].startswith("VD_")
    assert vd["canonical_write"] is False
    assert vd["decision_authority"] == "KX108_ONLY"
    assert vd["readonly"] is True
    assert vd["allowed_to_act"] is False
    assert vd["human_validation_required"] is True
