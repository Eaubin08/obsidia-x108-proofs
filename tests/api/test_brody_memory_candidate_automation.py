"""Tests for memory candidate pipeline via automation layer."""
import pytest
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.brody_rights_authority_matrix import MEMORY_CANDIDATE, MEMORY_WRITE_REQUEST


def _memory_snap(msg: str = "garde ça en mémoire") -> dict:
    return run_brody_automation_layer(
        session_id="mem-test-001",
        user_message=msg,
        language="fr",
        request_type=MEMORY_CANDIDATE,
        authority_snapshot={"requires_human_operator": True, "requires_kx108_decision": False},
        context_packet={"query": msg, "context_items": []},
        response_md="Je prépare un candidat mémoire. graphiti_write=false.",
    )


def test_presave_enabled_for_memory_candidate():
    snap = _memory_snap()
    assert snap["presave_buffer"]["enabled"] is True


def test_manual_validation_required_true():
    snap = _memory_snap()
    assert snap["presave_buffer"]["manual_validation_required"] is True


def test_memory_write_false_everywhere():
    snap = _memory_snap()
    assert snap["memory_write"] is False
    assert snap["graphiti_write"] is False
    assert snap["neo4j_write"] is False
    assert snap["memory_candidate_pipeline"]["graphiti_write"] is False
    assert snap["memory_candidate_pipeline"]["neo4j_write"] is False


def test_candidate_created_in_pipeline():
    snap = _memory_snap()
    assert snap["memory_candidate_pipeline"]["candidate_created"] is True


def test_needs_review_set():
    snap = _memory_snap()
    assert snap["memory_candidate_pipeline"]["needs_review"] is True


def test_triage_zone_valid():
    snap = _memory_snap()
    triage = snap["auto_triage"]
    assert triage["enabled"] is True
    assert triage["zone"] in ("ACTIVE", "SEMI_ACTIVE", "GHOST_SIDE_TABLE", "BOUNDARY_ALERT_NON_DECISIONAL")


def test_triage_memory_intake_always_false():
    snap = _memory_snap()
    assert snap["auto_triage"]["memory_intake"] is False


def test_memory_write_request_also_activates_pipeline():
    snap = run_brody_automation_layer(
        session_id="mem-write-test",
        user_message="écris dans graphiti",
        language="fr",
        request_type=MEMORY_WRITE_REQUEST,
        authority_snapshot={"requires_human_operator": True, "requires_kx108_decision": True},
        context_packet={"query": "", "context_items": []},
        response_md="Je ne peux pas écrire directement dans Graphiti.",
    )
    assert snap["presave_buffer"]["enabled"] is True
    assert snap["graphiti_write"] is False


def test_presave_candidate_has_boundary_flags():
    snap = _memory_snap()
    candidate = snap["presave_buffer"]["presave_candidate"]
    assert candidate is not None
    assert candidate.get("graphiti_write") is False
    assert candidate.get("memory_write") is False
    assert candidate.get("decision_authority") == "KX108_ONLY"


def test_gates_total_is_six():
    snap = _memory_snap()
    assert snap["memory_candidate_pipeline"]["gates_total"] == 6


def test_gates_passing_is_zero():
    snap = _memory_snap()
    assert snap["memory_candidate_pipeline"]["gates_passing"] == 0
