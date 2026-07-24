"""
test_brody_v3_memory_education_packet — V3 Block 3C
18 tests couvrant les invariants readonly, la sécurité, et les types de lessons.
DECISION_AUTHORITY=KX108_ONLY. PATCH=YES_BLOCK_3C_ONLY. COMMIT=NO.
"""
from __future__ import annotations

import pytest
from apps.obsidia_api.brody_memory_education_packet import (
    BrodyMemoryEducationPacketBuilder,
    build_education_packet,
    EDU_ADVERSARIAL,
    EDU_BOUNDARY,
    EDU_MISSING_DATA,
    EDU_FASTPATH,
    EDU_WEAK_SIGNAL,
    EDU_DEAD_PATH,
    EDU_DOMAIN,
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
        "candidate_summary": f"[{candidate_type}] domain={domain}",
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
        "advisory_only": True,
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
_BOUNDARY = _make_candidate(candidate_type="boundary_candidate",
                             missing_proof_tags=["données manquantes critiques"],
                             contradiction_tags=[])
_FASTPATH = _make_candidate(candidate_type="education_candidate", domain="gps",
                             fastpath_triggered=True, fastpath_type="gps_missing_data_fastpath")
_WEAK = _make_candidate(candidate_type="weak_signal_candidate",
                         weak_signal_tags=["signal faible détecté", "pattern inhabituel"])

BUILDER = BrodyMemoryEducationPacketBuilder()


def _build(c: dict = _STD) -> dict:
    return BUILDER.build(memory_candidate=c)


# ── Test 1 — education_packet_id présent ─────────────────────────────────────

def test_education_packet_id_present():
    ep = _build()
    assert "education_packet_id" in ep
    assert ep["education_packet_id"].startswith("EP_")


# ── Test 2 — candidate_id conservé ───────────────────────────────────────────

def test_candidate_id_conserved():
    ep = _build()
    assert ep["candidate_id"] == "MC_ABCDEF1234567890"


# ── Test 3 — trace_id conservé ───────────────────────────────────────────────

def test_trace_id_conserved():
    ep = _build()
    assert ep["trace_id"] == "TR_ABCDEF1234567890"


# ── Test 4 — readonly=True ────────────────────────────────────────────────────

def test_readonly_true():
    ep = _build()
    assert ep["readonly"] is True


# ── Test 5 — canonical_write=False ───────────────────────────────────────────

def test_canonical_write_false():
    ep = _build()
    assert ep["canonical_write"] is False


# ── Test 6 — graphiti_write=False ────────────────────────────────────────────

def test_graphiti_write_false():
    ep = _build()
    assert ep["graphiti_write"] is False


# ── Test 7 — neo4j_write=False ───────────────────────────────────────────────

def test_neo4j_write_false():
    ep = _build()
    assert ep["neo4j_write"] is False


# ── Test 8 — kernel_mutation=False ───────────────────────────────────────────

def test_kernel_mutation_false():
    ep = _build()
    assert ep["kernel_mutation"] is False


# ── Test 9 — emits_act=False ─────────────────────────────────────────────────

def test_emits_act_false():
    ep = _build()
    assert ep["emits_act"] is False


# ── Test 10 — allowed_to_decide=False ────────────────────────────────────────

def test_allowed_to_decide_false():
    ep = _build()
    assert ep["allowed_to_decide"] is False


# ── Test 11 — allowed_to_act=False ───────────────────────────────────────────

def test_allowed_to_act_false():
    ep = _build()
    assert ep["allowed_to_act"] is False


# ── Test 12 — decision_authority=KX108_ONLY ──────────────────────────────────

def test_decision_authority_kx108_only():
    ep = _build()
    assert ep["decision_authority"] == "KX108_ONLY"


# ── Test 13 — human_validation_required=True ─────────────────────────────────

def test_human_validation_required_true():
    ep = _build()
    assert ep["human_validation_required"] is True
    assert ep["human_validation_state"] == "pending"


# ── Test 14 — adversarial → adversarial_rejection_lesson ─────────────────────

def test_adversarial_candidate_adversarial_rejection_lesson():
    ep = _build(_ADV)
    assert ep["education_type"] == EDU_ADVERSARIAL
    assert ep["security_flags"]["is_adversarial"] is True
    assert ep["canonical_write"] is False
    assert ep["emits_act"] is False
    assert ep["allowed_to_act"] is False


# ── Test 15 — boundary candidate → boundary_lesson ou missing_data_lesson ─────

def test_boundary_candidate_lesson_type():
    ep = _build(_BOUNDARY)
    assert ep["education_type"] in (EDU_BOUNDARY, EDU_MISSING_DATA)
    assert ep["canonical_write"] is False
    assert ep["human_validation_required"] is True


# ── Test 16 — fastpath candidate → fastpath_lesson ───────────────────────────

def test_fastpath_candidate_fastpath_lesson():
    ep = _build(_FASTPATH)
    assert ep["education_type"] == EDU_FASTPATH
    assert ep["canonical_write"] is False
    assert ep["emits_act"] is False


# ── Test 17 — no secret capture ──────────────────────────────────────────────

def test_no_secret_capture():
    c = _make_candidate()
    c["candidate_payload"]["message_excerpt"] = "API_KEY=sk-ABCDEF123456 compromise"
    c["security_flags"]["secret_in_msg"] = True
    ep = _build(c)
    text = str(ep.get("lesson_summary", "")) + str(ep.get("bio_terrain_profile", ""))
    assert "sk-ABCDEF123456" not in text
    assert ep["canonical_write"] is False


# ── Test 18 — no raw private token stored ────────────────────────────────────

def test_no_raw_private_token_stored():
    c = _make_candidate()
    c["candidate_payload"]["message_excerpt"] = "Bearer eyJhbGciOiJSUzI1NiJ9.abc.xyz"
    ep = _build(c)
    text = str(ep)
    assert "eyJhbGciOiJSUzI1NiJ9" not in text
    assert ep["canonical_write"] is False


# ── Test bonus — module-level function ───────────────────────────────────────

def test_build_education_packet_module_function():
    ep = build_education_packet(memory_candidate=_STD)
    assert ep["education_packet_id"].startswith("EP_")
    assert ep["canonical_write"] is False
    assert ep["decision_authority"] == "KX108_ONLY"
    assert ep["readonly"] is True
