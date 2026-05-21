"""Tests for operator loop via automation layer."""
import pytest
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.brody_rights_authority_matrix import (
    OPERATOR_COMMAND_PROPOSAL, ACTION_OR_ACT_REQUEST, PURE_RESPONSE,
)


def _op_snap(msg: str = "prépare une commande pour tester API status") -> dict:
    return run_brody_automation_layer(
        session_id="op-test-001",
        user_message=msg,
        language="fr",
        request_type=OPERATOR_COMMAND_PROPOSAL,
        authority_snapshot={"requires_human_operator": True, "requires_kx108_decision": False},
        context_packet={"query": msg, "context_items": []},
        response_md="Je prépare un command packet opérateur.",
    )


def test_operator_human_command_packet_field_present():
    snap = _op_snap()
    assert "human_command_packet_ready" in snap["operator_loop"]


def test_operator_execution_not_allowed_for_brody():
    snap = _op_snap()
    assert snap["operator_loop"]["execution_allowed_for_brody"] is False


def test_operator_human_operator_required_true():
    snap = _op_snap()
    assert snap["operator_loop"]["human_operator_required"] is True


def test_operator_gate_classification_present():
    snap = _op_snap()
    assert snap["operator_loop"]["command_gate_classification"] != ""


def test_operator_emits_act_false():
    snap = _op_snap()
    assert snap["emits_act"] is False


def test_operator_graphiti_write_false():
    snap = _op_snap()
    assert snap["graphiti_write"] is False


def test_operator_blocked_contains_execution():
    snap = _op_snap()
    assert any("execut" in s.lower() or "run" in s.lower() or "auto_run" in s.lower()
               for s in snap["blocked_steps"])


def test_non_operator_type_loop_not_active():
    snap = run_brody_automation_layer(
        session_id="op-test-002",
        user_message="bonjour",
        language="fr",
        request_type=PURE_RESPONSE,
        authority_snapshot={"requires_human_operator": False, "requires_kx108_decision": False},
        context_packet={"query": "", "context_items": []},
        response_md="Salut.",
    )
    assert snap["operator_loop"]["human_command_packet_ready"] is False
    assert snap["operator_loop"]["command_gate_classification"] == "NOT_APPLICABLE"


def test_act_request_not_executed():
    snap = run_brody_automation_layer(
        session_id="act-test-001",
        user_message="autorise act",
        language="fr",
        request_type=ACTION_OR_ACT_REQUEST,
        authority_snapshot={"requires_human_operator": True, "requires_kx108_decision": True},
        context_packet={"query": "", "context_items": []},
        response_md="Je ne peux pas autoriser ACT.",
    )
    assert snap["emits_act"] is False
    assert snap["allowed_to_act"] is False
    assert snap["operator_loop"]["execution_allowed_for_brody"] is False
