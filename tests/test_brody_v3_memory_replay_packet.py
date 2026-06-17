"""
test_brody_v3_memory_replay_packet — V3 Block 3C
20 tests couvrant les invariants readonly, la sécurité, les types de replay.
DECISION_AUTHORITY=KX108_ONLY. PATCH=YES_BLOCK_3C_ONLY. COMMIT=NO.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_memory_replay_packet import (
    BrodyMemoryReplayPacketBuilder,
    build_replay_packet,
    REPLAY_ADVERSARIAL,
    REPLAY_BOUNDARY,
    REPLAY_MISSING_DATA,
    REPLAY_FASTPATH,
    REPLAY_DOMAIN,
    REPLAY_DEAD_PATH,
    _FORBIDDEN_TRANSITIONS,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_candidate(
    *,
    candidate_id: str = "MC_ABCDEF1234567890",
    trace_id: str = "TR_ABCDEF1234567890",
    session_id: str = "sess_test_001",
    candidate_type: str = "education_candidate",
    is_adversarial: bool = False,
    priority_score: float = 0.45,
    memory_relevance_score: float = 0.4,
    useful_path_tags: list | None = None,
    dead_path_tags: list | None = None,
    weak_signal_tags: list | None = None,
    contradiction_tags: list | None = None,
    missing_proof_tags: list | None = None,
    risk_flags: list | None = None,
    domain: str = "bank",
    fastpath_triggered: bool = False,
    fastpath_type: str | None = None,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "trace_id": trace_id,
        "session_id": session_id,
        "timestamp": "2026-06-13T19:15:00Z",
        "block": "V3_BLOCK_3B",
        "candidate_type": candidate_type,
        "candidate_payload": {
            "message_excerpt": "Quel est le solde de mon compte ?",
            "response_excerpt": "Votre solde est de 1500 EUR. Validation humaine requise.",
            "domain_detected": domain,
            "intent_type": "advisory",
            "path_coherence_score": 0.75,
            "fastpath_type": fastpath_type,
            "fastpath_triggered": fastpath_triggered,
            "graphiti_allowed": False,
        },
        "domain_tags": [domain],
        "balance_tags": {
            "balance_memoire": {"tension": 0.5, "seuil_depasse": False, "priority": 4},
            "balance_risque": {"tension": 0.6 if is_adversarial else 0.1, "seuil_depasse": is_adversarial, "priority": 0},
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
        "security_flags": {
            "is_adversarial": is_adversarial,
            "secret_in_msg": False,
            "secret_in_resp": False,
            "scrubbed": False,
        },
    }


_STD = _make_candidate()
_ADV = _make_candidate(candidate_type="adversarial_rejection_candidate", is_adversarial=True,
                        priority_score=0.0, useful_path_tags=[])
_MISSING = _make_candidate(candidate_type="boundary_candidate",
                            missing_proof_tags=["données manquantes", "IBAN manquant"])
_FASTPATH = _make_candidate(candidate_type="replay_candidate", domain="gps",
                             fastpath_triggered=True, fastpath_type="gps_missing_data_fastpath")

BUILDER = BrodyMemoryReplayPacketBuilder()


def _build(c: dict = _STD) -> dict:
    return BUILDER.build(memory_candidate=c)


# ── Test 1 — replay_packet_id présent ────────────────────────────────────────

def test_replay_packet_id_present():
    rp = _build()
    assert "replay_packet_id" in rp
    assert rp["replay_packet_id"].startswith("RP_")


# ── Test 2 — candidate_id conservé ───────────────────────────────────────────

def test_candidate_id_conserved():
    rp = _build()
    assert rp["candidate_id"] == "MC_ABCDEF1234567890"


# ── Test 3 — trace_id conservé ───────────────────────────────────────────────

def test_trace_id_conserved():
    rp = _build()
    assert rp["trace_id"] == "TR_ABCDEF1234567890"


# ── Test 4 — readonly=True ────────────────────────────────────────────────────

def test_readonly_true():
    rp = _build()
    assert rp["readonly"] is True


# ── Test 5 — canonical_write=False ───────────────────────────────────────────

def test_canonical_write_false():
    rp = _build()
    assert rp["canonical_write"] is False


# ── Test 6 — graphiti_write=False ────────────────────────────────────────────

def test_graphiti_write_false():
    rp = _build()
    assert rp["graphiti_write"] is False


# ── Test 7 — neo4j_write=False ───────────────────────────────────────────────

def test_neo4j_write_false():
    rp = _build()
    assert rp["neo4j_write"] is False


# ── Test 8 — kernel_mutation=False ───────────────────────────────────────────

def test_kernel_mutation_false():
    rp = _build()
    assert rp["kernel_mutation"] is False


# ── Test 9 — emits_act=False ─────────────────────────────────────────────────

def test_emits_act_false():
    rp = _build()
    assert rp["emits_act"] is False


# ── Test 10 — allowed_to_decide=False ────────────────────────────────────────

def test_allowed_to_decide_false():
    rp = _build()
    assert rp["allowed_to_decide"] is False


# ── Test 11 — allowed_to_act=False ───────────────────────────────────────────

def test_allowed_to_act_false():
    rp = _build()
    assert rp["allowed_to_act"] is False


# ── Test 12 — decision_authority=KX108_ONLY ──────────────────────────────────

def test_decision_authority_kx108_only():
    rp = _build()
    assert rp["decision_authority"] == "KX108_ONLY"


# ── Test 13 — human_validation_required=True ─────────────────────────────────

def test_human_validation_required_true():
    rp = _build()
    assert rp["human_validation_required"] is True
    assert rp["human_validation_state"] == "pending"


# ── Test 14 — replay_steps non vides ─────────────────────────────────────────

def test_replay_steps_not_empty():
    rp = _build()
    assert "replay_steps" in rp
    assert len(rp["replay_steps"]) >= 2
    # Chaque step doit avoir canonical_write=False et emits_act=False
    for step in rp["replay_steps"]:
        assert step.get("canonical_write") is False
        assert step.get("emits_act") is False


# ── Test 15 — forbidden_transitions contient ACT / canonical / kernel ─────────

def test_forbidden_transitions_present():
    rp = _build()
    ft = rp.get("forbidden_transitions", [])
    assert len(ft) > 0
    assert "ACT=YES" in ft
    assert "canonical_write=True" in ft
    assert "kernel_mutation=True" in ft
    assert "emits_act=True" in ft
    assert "allowed_to_act=True" in ft


# ── Test 16 — adversarial → adversarial_rejection_replay ─────────────────────

def test_adversarial_candidate_rejection_replay():
    rp = _build(_ADV)
    assert rp["replay_type"] == REPLAY_ADVERSARIAL
    assert rp["security_flags"]["is_adversarial"] is True
    assert rp["replay_usefulness_score"] == 0.0
    assert rp["canonical_write"] is False
    assert rp["emits_act"] is False


# ── Test 17 — missing data → missing_data_replay ─────────────────────────────

def test_missing_data_candidate_missing_replay():
    rp = _build(_MISSING)
    assert rp["replay_type"] == REPLAY_MISSING_DATA
    assert rp["canonical_write"] is False
    assert rp["human_validation_required"] is True


# ── Test 18 — replay_usefulness_score borné [0.0, 1.0] ───────────────────────

def test_replay_usefulness_score_borné():
    for prio, mem in [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0), (0.3, 0.7)]:
        c = _make_candidate(priority_score=prio, memory_relevance_score=mem)
        rp = _build(c)
        s = rp["replay_usefulness_score"]
        assert 0.0 <= s <= 1.0, f"replay_usefulness_score hors bornes: {s}"
        assert rp["canonical_write"] is False


# ── Test 19 — no secret capture ──────────────────────────────────────────────

def test_no_secret_capture():
    c = _make_candidate()
    c["candidate_payload"]["message_excerpt"] = "API_KEY=sk-ABCDEF123456 compromise"
    c["security_flags"]["secret_in_msg"] = True
    rp = _build(c)
    text = str(rp.get("replay_summary", "")) + str(rp.get("replays", ""))
    assert "sk-ABCDEF123456" not in text
    assert rp["canonical_write"] is False


# ── Test 20 — no raw private token stored ────────────────────────────────────

def test_no_raw_private_token_stored():
    c = _make_candidate()
    c["candidate_payload"]["response_excerpt"] = "Bearer eyJhbGciOiJSUzI1NiJ9.abc.xyz"
    rp = _build(c)
    text = str(rp)
    assert "eyJhbGciOiJSUzI1NiJ9" not in text
    assert rp["canonical_write"] is False


# ── Test bonus — module-level function ───────────────────────────────────────

def test_build_replay_packet_module_function():
    rp = build_replay_packet(memory_candidate=_STD)
    assert rp["replay_packet_id"].startswith("RP_")
    assert rp["canonical_write"] is False
    assert rp["decision_authority"] == "KX108_ONLY"
    assert rp["readonly"] is True
    assert rp["allowed_to_act"] is False
