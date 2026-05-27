from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.brody_rights_authority_matrix import (
    OPERATOR_COMMAND_PROPOSAL,
    PURE_RESPONSE,
)


def _snap(msg: str, request_type: str = OPERATOR_COMMAND_PROPOSAL):
    return run_brody_automation_layer(
        session_id="f10c-test-session",
        user_message=msg,
        language="fr",
        request_type=request_type,
        authority_snapshot={
            "decision_authority": "KX108_ONLY",
            "requires_human_operator": request_type == OPERATOR_COMMAND_PROPOSAL,
            "readonly": True,
            "emits_act": False,
            "emits_verdict": False,
        },
        context_packet={
            "readonly": True,
            "decision_authority": "KX108_ONLY",
        },
        response_md="readonly automation reconnect test",
    )


def test_operator_command_reconnect_exposes_existing_packet():
    snap = _snap("prepare la commande git status")
    op = snap["operator_loop"]

    assert snap["request_type"] == "OPERATOR_COMMAND_PROPOSAL"
    assert op["human_command_packet_ready"] is True
    assert op["execution_allowed_for_brody"] is False
    assert op["brody_execute_allowed"] is False
    assert op["human_operator_required"] is True
    assert op["human_execution_required"] is True
    assert op["copy_only"] is True
    assert op["present_packet_to_operator"] is True

    packet = op["human_command_packet"]
    assert packet["status"] == "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED"
    assert packet["packet_kind"] == "HUMAN_OPERATOR_COMMAND_PACKET"
    assert packet["brody_execute_allowed"] is False
    assert packet["brody_authorize_allowed"] is False
    assert packet["executed"] is False
    assert packet["readonly_analysis_only"] is True
    assert packet["decision_authority"] == "KX108_ONLY"
    assert packet["emits_act"] is False
    assert packet["emits_verdict"] is False


def test_operator_command_copy_block_exposed():
    snap = _snap("quelle commande dois-je lancer pour git status")
    op = snap["operator_loop"]
    cb = op["command_copy_block"]

    assert cb["label"] == "HUMAN_OPERATOR_COMMAND_PACKET_COPY_ONLY"
    assert "git status" in cb["command"]
    assert cb["warning"] == "Manual human review required. Brody cannot execute."
    assert op["execution_allowed_for_brody"] is False


def test_non_operator_request_has_no_command_packet():
    snap = _snap("explique Obsidia simplement", request_type=PURE_RESPONSE)
    op = snap["operator_loop"]

    assert op["human_command_packet_ready"] is False
    assert op["command_gate_classification"] == "NOT_APPLICABLE"
    assert op["execution_allowed_for_brody"] is False
    assert op["brody_execute_allowed"] is False
    assert op["present_packet_to_operator"] is False
    assert op["human_command_packet"] is None
    assert op["command_copy_block"] is None


def test_operator_command_next_allowed_includes_present_packet():
    snap = _snap("prepare un command packet pour git status")
    assert "present_packet_to_operator" in snap["next_allowed_steps"]
    assert "execute_command_as_brody" in snap["blocked_steps"]
    assert "auto_run" in snap["blocked_steps"]
