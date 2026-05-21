import pytest
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.world_call_classifier import WorldCallClass
from periphery.world_calls.world_executor_dryrun import execute_dry_run


def test_gateway_always_egress_false():
    gw = ObsidiaGateway()
    from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
    ticket = issue_sovereign_ticket(
        action_id="x",
        os3_ticket_id="y",
        x108_gate="ALLOW",
        scope="*",
        autonomy_level=0,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    decision = gw.check(ticket, WorldCallClass.READ_ONLY_WORLD_CALL, "*")
    assert decision.egress_allowed is False


def test_executor_never_executes():
    gw = ObsidiaGateway()
    decision = gw.check(None, WorldCallClass.READ_ONLY_WORLD_CALL, "bank")
    result = execute_dry_run("test_action", decision)
    assert result.executed is False
    assert result.simulated is True
    result.assert_not_executed()


def test_gateway_no_secret_passthrough():
    from periphery.world_calls.secret_boundary import redact_secrets
    payload = {"message": "hello", "api_key": "secret123", "data": "safe"}
    redacted = redact_secrets(payload)
    assert redacted["api_key"] == "[REDACTED_BY_SECRET_BOUNDARY]"
    assert redacted["message"] == "hello"
    assert redacted["data"] == "safe"
