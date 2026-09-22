"""Tests for brody_automation_orchestrator — boundary and routing."""
import pytest
from apps.obsidia_api.brody_automation_orchestrator import (
    run_brody_automation_layer,
    AUTOMATION_BOUNDARY,
)
from apps.obsidia_api.brody_rights_authority_matrix import (
    MEMORY_CANDIDATE,
    STRUCTURAL_PREPARATION,
    OPERATOR_COMMAND_PROPOSAL,
    ACTION_OR_ACT_REQUEST,
    CONTEXT_ANALYSIS,
    PURE_RESPONSE,
)

_BASE_CTX = {"query": "test", "context_items": []}
_BASE_AUTH = {"requires_human_operator": False, "requires_kx108_decision": False}


def _snap(request_type: str, user_message: str = "test") -> dict:
    return run_brody_automation_layer(
        session_id="test-session-001",
        user_message=user_message,
        language="fr",
        request_type=request_type,
        authority_snapshot=_BASE_AUTH,
        context_packet=_BASE_CTX,
        response_md="Réponse test.",
    )


# ── Absolute boundary invariants ─────────────────────────────────────────────

def test_boundary_readonly_always_true():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, STRUCTURAL_PREPARATION, PURE_RESPONSE):
        snap = _snap(rt)
        assert snap["readonly"] is True, f"{rt}: readonly must be True"


def test_boundary_emits_act_always_false():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, OPERATOR_COMMAND_PROPOSAL):
        snap = _snap(rt)
        assert snap["emits_act"] is False, f"{rt}: emits_act must be False"


def test_boundary_graphiti_write_always_false():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, STRUCTURAL_PREPARATION):
        snap = _snap(rt)
        assert snap["graphiti_write"] is False
        assert snap["memory_candidate_pipeline"]["graphiti_write"] is False


def test_boundary_neo4j_write_always_false():
    snap = _snap(MEMORY_CANDIDATE)
    assert snap["neo4j_write"] is False
    assert snap["memory_candidate_pipeline"]["neo4j_write"] is False


def test_boundary_decision_authority_kx108():
    for rt in (MEMORY_CANDIDATE, ACTION_OR_ACT_REQUEST, OPERATOR_COMMAND_PROPOSAL):
        snap = _snap(rt)
        assert snap["decision_authority"] == "KX108_ONLY"


def test_boundary_memory_decision_always_false():
    snap = _snap(MEMORY_CANDIDATE)
    assert snap["memory_decision"] is False


def test_boundary_allowed_to_act_always_false():
    snap = _snap(ACTION_OR_ACT_REQUEST)
    assert snap["allowed_to_act"] is False


# ── "Garde ça en mémoire" — MEMORY_CANDIDATE ─────────────────────────────────

def test_memory_candidate_presave_enabled():
    snap = _snap(MEMORY_CANDIDATE, "garde ça en mémoire")
    assert snap["presave_buffer"]["enabled"] is True
    assert snap["presave_buffer"]["manual_validation_required"] is True
    assert snap["presave_buffer"]["presave_candidate"] is not None


def test_memory_candidate_pipeline_state():
    snap = _snap(MEMORY_CANDIDATE)
    pipeline = snap["memory_candidate_pipeline"]
    assert pipeline["candidate_created"] is True
    assert pipeline["graphiti_write"] is False
    assert pipeline["neo4j_write"] is False


def test_memory_candidate_auto_triage_runs():
    snap = _snap(MEMORY_CANDIDATE, "garde ça en mémoire")
    triage = snap["auto_triage"]
    assert triage["enabled"] is True
    assert triage["memory_intake"] is False
    assert triage["zone"] in ("ACTIVE", "SEMI_ACTIVE", "GHOST_SIDE_TABLE", "BOUNDARY_ALERT_NON_DECISIONAL")


def test_memory_candidate_next_steps_contain_presave():
    snap = _snap(MEMORY_CANDIDATE)
    assert any("presave" in s for s in snap["next_allowed_steps"])


def test_memory_candidate_blocked_graphiti():
    snap = _snap(MEMORY_CANDIDATE)
    assert "graphiti_write" in snap["blocked_steps"]


# ── "Prépare un ContextPacket" — STRUCTURAL_PREPARATION ─────────────────────

def test_structural_prep_presave_disabled():
    snap = _snap(STRUCTURAL_PREPARATION, "prépare un contextpacket")
    assert snap["presave_buffer"]["enabled"] is False


def test_structural_prep_triage_not_run():
    snap = _snap(STRUCTURAL_PREPARATION)
    assert snap["auto_triage"]["zone"] == "NOT_RUN"


def test_structural_prep_next_contains_context_packet():
    snap = _snap(STRUCTURAL_PREPARATION)
    assert any("context_packet" in s for s in snap["next_allowed_steps"])


def test_structural_prep_emits_act_false():
    snap = _snap(STRUCTURAL_PREPARATION)
    assert snap["emits_act"] is False


# ── "Prépare une commande" — OPERATOR_COMMAND_PROPOSAL ──────────────────────

def test_operator_proposal_human_operator_required():
    snap = _snap(OPERATOR_COMMAND_PROPOSAL, "prépare une commande pour tester API status")
    assert snap["operator_loop"]["human_operator_required"] is True


def test_operator_proposal_execution_not_allowed_for_brody():
    snap = _snap(OPERATOR_COMMAND_PROPOSAL)
    assert snap["operator_loop"]["execution_allowed_for_brody"] is False


def test_operator_proposal_presave_not_active():
    snap = _snap(OPERATOR_COMMAND_PROPOSAL)
    assert snap["presave_buffer"]["enabled"] is False


# ── "Autorise act" — ACTION_OR_ACT_REQUEST ───────────────────────────────────

def test_action_request_emits_act_false():
    snap = _snap(ACTION_OR_ACT_REQUEST, "autorise act")
    assert snap["emits_act"] is False


def test_action_request_allowed_to_act_false():
    snap = _snap(ACTION_OR_ACT_REQUEST)
    assert snap["allowed_to_act"] is False


def test_action_request_blocked_contains_act():
    snap = _snap(ACTION_OR_ACT_REQUEST)
    assert any("act" in s.lower() for s in snap["blocked_steps"])


# ── "Quelles sont tes limites" — CONTEXT_ANALYSIS ────────────────────────────

def test_context_analysis_snapshot_present():
    snap = _snap(CONTEXT_ANALYSIS, "quelles sont tes limites")
    assert snap is not None
    assert "next_allowed_steps" in snap
    assert "blocked_steps" in snap


def test_context_analysis_has_capabilities():
    snap = _snap(CONTEXT_ANALYSIS)
    assert len(snap["next_allowed_steps"]) > 0


def test_context_analysis_blocked_decide():
    snap = _snap(CONTEXT_ANALYSIS)
    assert "decide" in snap["blocked_steps"] or "memory_write" in snap["blocked_steps"]


# ── Payload shape ─────────────────────────────────────────────────────────────

def test_snapshot_has_all_required_keys():
    snap = _snap(PURE_RESPONSE)
    required = [
        "session_ledger", "presave_buffer", "auto_triage",
        "memory_candidate_pipeline", "operator_loop",
        "next_allowed_steps", "blocked_steps",
        "request_type", "created_at",
        "readonly", "emits_act", "graphiti_write",
        "neo4j_write", "decision_authority",
    ]
    for k in required:
        assert k in snap, f"Missing key: {k}"


def test_session_ledger_always_attempted():
    snap = _snap(PURE_RESPONSE)
    assert "enabled" in snap["session_ledger"]
    assert snap["session_ledger"]["memory_write"] is False
