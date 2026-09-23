"""
Anti-invention tests — verify automation_snapshot contains only sourced fields.
Rule: every field must be found in an existing module, manifest, or pointer.
Fields NOT found in existing sources must not appear with synthetic values.
"""
import pytest
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.brody_rights_authority_matrix import (
    MEMORY_CANDIDATE, PURE_RESPONSE, ACTION_OR_ACT_REQUEST,
    CONTEXT_ANALYSIS, CAPABILITY_SCOPE,
)


def _snap(request_type: str, msg: str = "test") -> dict:
    return run_brody_automation_layer(
        session_id="no-invented-test",
        user_message=msg,
        language="fr",
        request_type=request_type,
        authority_snapshot={"requires_human_operator": False, "requires_kx108_decision": False},
        context_packet={"query": msg, "context_items": []},
        response_md="Réponse.",
    )


# ── Fields that MUST NOT appear ───────────────────────────────────────────────

def test_no_confidence_field_at_root():
    snap = _snap(PURE_RESPONSE)
    assert "confidence" not in snap, "confidence is NOT_FOUND_IN_EXISTING_SOURCES"


def test_no_confidence_in_auto_triage_enabled():
    snap = _snap(MEMORY_CANDIDATE, "garde ça en mémoire")
    triage = snap["auto_triage"]
    assert "confidence" not in triage, "confidence is NOT_FOUND_IN_EXISTING_SOURCES in triage module"


def test_no_confidence_in_auto_triage_disabled():
    snap = _snap(PURE_RESPONSE)
    triage = snap["auto_triage"]
    assert "confidence" not in triage


def test_no_triage_score_anywhere():
    snap = _snap(MEMORY_CANDIDATE)
    assert "triage_score" not in snap
    assert "triage_score" not in snap.get("auto_triage", {})


def test_no_risk_level_anywhere():
    snap = _snap(ACTION_OR_ACT_REQUEST)
    assert "risk_level" not in snap
    assert "risk_level" not in snap.get("auto_triage", {})
    assert "risk_level" not in snap.get("memory_candidate_pipeline", {})


def test_no_automation_score():
    snap = _snap(PURE_RESPONSE)
    assert "automation_score" not in snap


def test_no_memory_state_invented():
    snap = _snap(MEMORY_CANDIDATE)
    assert "memory_state" not in snap


def test_no_automation_state_invented():
    snap = _snap(CONTEXT_ANALYSIS)
    assert "automation_state" not in snap


# ── Fields that MUST appear with correct sourced values ──────────────────────

def test_decision_authority_kx108_only_at_root():
    snap = _snap(PURE_RESPONSE)
    assert snap["decision_authority"] == "KX108_ONLY"


def test_decision_authority_kx108_only_memory():
    snap = _snap(MEMORY_CANDIDATE)
    assert snap["decision_authority"] == "KX108_ONLY"


def test_decision_authority_kx108_only_action():
    snap = _snap(ACTION_OR_ACT_REQUEST)
    assert snap["decision_authority"] == "KX108_ONLY"


def test_emits_act_false_always():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, PURE_RESPONSE, CAPABILITY_SCOPE):
        snap = _snap(rt)
        assert snap["emits_act"] is False, f"{rt}: emits_act must be False"


def test_memory_write_false_always():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, PURE_RESPONSE):
        snap = _snap(rt)
        assert snap["memory_write"] is False


def test_graphiti_write_false_always():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, PURE_RESPONSE):
        snap = _snap(rt)
        assert snap["graphiti_write"] is False


def test_neo4j_write_false_always():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST):
        snap = _snap(rt)
        assert snap["neo4j_write"] is False


# ── Sourced zones — CRISTAL/TRANSITION/NEANT are real from manifest ───────────

def test_triage_zone_only_real_values_when_enabled():
    snap = _snap(MEMORY_CANDIDATE, "garde ça en mémoire")
    triage = snap["auto_triage"]
    if triage.get("enabled"):
        assert triage["zone"] in ("CRISTAL", "TRANSITION", "NEANT"), \
            "zone must be one of the 3 values from adapted_rules in triage manifest"


def test_triage_zone_not_run_when_disabled():
    snap = _snap(PURE_RESPONSE)
    assert snap["auto_triage"]["zone"] == "NOT_RUN"


def test_reflex_status_only_real_values():
    snap = _snap(MEMORY_CANDIDATE)
    triage = snap["auto_triage"]
    if triage.get("enabled") and "reflex_status" in triage:
        assert triage["reflex_status"] in (
            "REFLEX_ALERT_ONLY", "PROCEED_CONTEXT_ONLY"
        ), "reflex_status must be from ReflexReducer in triage module"


# ── Writable memory protocol — sourced from WRITABLE_MEMORY_ACTIVATION_CHECKLIST ──

def test_writable_memory_protocol_present():
    snap = _snap(PURE_RESPONSE)
    assert "writable_memory_protocol" in snap


def test_writable_memory_active_false():
    snap = _snap(PURE_RESPONSE)
    wmp = snap["writable_memory_protocol"]
    assert wmp["writable_memory_active"] is False


def test_protocol_state_is_candidate_only():
    snap = _snap(PURE_RESPONSE)
    wmp = snap["writable_memory_protocol"]
    assert wmp["protocol_state"] == "PROTOCOL_CANDIDATE_ONLY"


def test_gates_passing_is_zero_of_six():
    snap = _snap(PURE_RESPONSE)
    wmp = snap["writable_memory_protocol"]
    assert wmp["gates_passing"] == "0/6"


def test_operator_approval_false():
    snap = _snap(PURE_RESPONSE)
    wmp = snap["writable_memory_protocol"]
    assert wmp["operator_approval"] is False


def test_real_import_ready_false():
    snap = _snap(PURE_RESPONSE)
    wmp = snap["writable_memory_protocol"]
    assert wmp["real_import_ready"] is False


# ── Root decision_authority from safe_response ────────────────────────────────

def test_safe_response_decision_authority():
    from apps.obsidia_api.safe_response import safe_backend_response
    resp = safe_backend_response({"test": 1})
    assert resp["decision_authority"] == "KX108_ONLY", \
        "safe_response.py decision_authority must be KX108_ONLY not X108_ONLY"
