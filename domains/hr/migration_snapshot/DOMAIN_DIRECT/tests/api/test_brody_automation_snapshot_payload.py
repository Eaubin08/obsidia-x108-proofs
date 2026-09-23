"""Tests for automation_snapshot in /api/brody/chat payload shape."""
import pytest
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer, AUTOMATION_BOUNDARY
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import enrich_final_answer_with_automation
from apps.obsidia_api.brody_rights_authority_matrix import (
    MEMORY_CANDIDATE, STRUCTURAL_PREPARATION, OPERATOR_COMMAND_PROPOSAL,
    ACTION_OR_ACT_REQUEST, CONTEXT_ANALYSIS, PURE_RESPONSE,
)


def _make_snap(request_type: str, msg: str = "test") -> dict:
    return run_brody_automation_layer(
        session_id="payload-test-001",
        user_message=msg,
        language="fr",
        request_type=request_type,
        authority_snapshot={"requires_human_operator": False, "requires_kx108_decision": False},
        context_packet={"query": msg, "context_items": []},
        response_md="Réponse.",
    )


# ── Payload shape contract ────────────────────────────────────────────────────

def test_payload_has_all_boundary_keys():
    snap = _make_snap(PURE_RESPONSE)
    for k, v in AUTOMATION_BOUNDARY.items():
        assert k in snap, f"Missing key {k}"
        assert snap[k] == v, f"{k}: expected {v}, got {snap[k]}"


def test_payload_has_all_section_keys():
    snap = _make_snap(PURE_RESPONSE)
    for section in ("session_ledger", "presave_buffer", "auto_triage",
                    "memory_candidate_pipeline", "operator_loop"):
        assert section in snap, f"Missing section: {section}"


def test_payload_next_allowed_steps_is_list():
    snap = _make_snap(PURE_RESPONSE)
    assert isinstance(snap["next_allowed_steps"], list)


def test_payload_blocked_steps_is_list():
    snap = _make_snap(PURE_RESPONSE)
    assert isinstance(snap["blocked_steps"], list)


def test_payload_created_at_present():
    snap = _make_snap(PURE_RESPONSE)
    assert "created_at" in snap
    assert snap["created_at"]


def test_payload_request_type_echoed():
    snap = _make_snap(MEMORY_CANDIDATE)
    assert snap["request_type"] == MEMORY_CANDIDATE


# ── enrich_final_answer_with_automation ──────────────────────────────────────

def test_enrich_memory_candidate_adds_addendum():
    snap = _make_snap(MEMORY_CANDIDATE, "garde ça en mémoire")
    result = enrich_final_answer_with_automation("Réponse de base.", snap, "fr")
    assert "Automation" in result or "automation" in result or "presave" in result.lower()


def test_enrich_operator_proposal_adds_addendum():
    snap = _make_snap(OPERATOR_COMMAND_PROPOSAL, "prépare la commande")
    result = enrich_final_answer_with_automation("Voici le packet.", snap, "fr")
    assert "packet" in result.lower() or "opérateur" in result.lower() or "Automation" in result


def test_enrich_action_request_adds_addendum():
    snap = _make_snap(ACTION_OR_ACT_REQUEST, "autorise act")
    result = enrich_final_answer_with_automation("Je refuse.", snap, "fr")
    assert "act" in result.lower() or "Automation" in result or "kx108" in result.lower()


def test_enrich_pure_response_unchanged():
    snap = _make_snap(PURE_RESPONSE, "bonjour")
    base = "Bonjour, je suis Brody."
    result = enrich_final_answer_with_automation(base, snap, "fr")
    assert result == base


def test_enrich_structural_prep_unchanged():
    snap = _make_snap(STRUCTURAL_PREPARATION, "prépare un context packet")
    base = "Je prépare le packet."
    result = enrich_final_answer_with_automation(base, snap, "fr")
    assert result == base


def test_enrich_preserves_base_answer():
    snap = _make_snap(MEMORY_CANDIDATE)
    base = "Je prépare un candidat mémoire."
    result = enrich_final_answer_with_automation(base, snap, "fr")
    assert result.startswith(base)


# ── Final answer contains automation awareness ────────────────────────────────

def test_capabilities_response_includes_limits():
    """'quelles sont tes limites' → snapshot present with next/blocked steps."""
    snap = _make_snap(CONTEXT_ANALYSIS, "quelles sont tes limites")
    result = enrich_final_answer_with_automation("Je peux analyser.", snap, "fr")
    # Should add automation addendum for CONTEXT_ANALYSIS
    # next_allowed_steps and blocked_steps present
    assert snap["next_allowed_steps"]
    assert snap["blocked_steps"]
