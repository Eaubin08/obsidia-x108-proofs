"""
Phase F integration test: full world call gateway pipeline.
Ticket → classify → gateway → dry-run only, egress_allowed=False always.
"""
import pytest
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.world_call_classifier import WorldCallClass, classify_world_call
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.world_action_bus import publish_event

READ_ONLY = WorldCallClass.READ_ONLY_WORLD_CALL
FORBIDDEN = WorldCallClass.FORBIDDEN_WORLD_CALL
REVERSIBLE = WorldCallClass.REVERSIBLE_WORLD_CALL


def test_no_ticket_gateway_blocks():
    gateway = ObsidiaGateway()
    decision = gateway.check(None, READ_ONLY, "bank")
    assert decision.gate_result == "BLOCK"
    assert decision.egress_allowed is False
    assert "NO_SOVEREIGN_TICKET" in decision.reason


def test_valid_ticket_read_only_dry_run_pass():
    ticket = issue_sovereign_ticket(
        action_id="act_test_001",
        os3_ticket_id="os3_001",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, READ_ONLY, "bank")
    assert decision.gate_result == "DRY_RUN_PASS"
    assert decision.dry_run_only is True
    assert decision.egress_allowed is False


def test_forbidden_world_call_class_blocked():
    ticket = issue_sovereign_ticket(
        action_id="act_test_002",
        os3_ticket_id="os3_002",
        x108_gate="ALLOW",
        scope="trading",
        autonomy_level=3,
        world_call_class="FORBIDDEN_WORLD_CALL",
    )
    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, FORBIDDEN, "trading")
    assert decision.gate_result == "BLOCK"
    assert decision.egress_allowed is False


def test_wrong_scope_blocks():
    ticket = issue_sovereign_ticket(
        action_id="act_test_003",
        os3_ticket_id="os3_003",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, READ_ONLY, "trading")
    assert decision.gate_result == "BLOCK"
    assert "INVALID_SCOPE" in decision.reason


def test_egress_always_false_even_with_valid_ticket():
    ticket = issue_sovereign_ticket(
        action_id="act_test_004",
        os3_ticket_id="os3_004",
        x108_gate="ALLOW",
        scope="*",
        autonomy_level=2,
        world_call_class="REVERSIBLE_WORLD_CALL",
    )
    gateway = ObsidiaGateway()
    decision = gateway.check(ticket, REVERSIBLE, "bank")
    assert decision.egress_allowed is False


def test_world_action_bus_publish_dry_run():
    ticket = issue_sovereign_ticket(
        action_id="act_bus_001",
        os3_ticket_id="os3_bus_001",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=1,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    evt = publish_event(
        action_id="act_bus_001",
        sovereign_ticket_id=ticket.ticket_id,
        world_call_class="READ_ONLY_WORLD_CALL",
        action_risk_class="READ_ONLY",
        autonomy_level=1,
        intent="check_balance",
        domain="bank",
        blocked=False,
        block_reason="",
    )
    assert evt.dry_run_only is True
