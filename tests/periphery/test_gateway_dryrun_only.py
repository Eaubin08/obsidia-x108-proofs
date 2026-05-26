import pytest
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.world_call_classifier import WorldCallClass
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket


def _valid_ticket(scope="bank"):
    return issue_sovereign_ticket(
        action_id="gw_test",
        os3_ticket_id="os3_gw",
        x108_gate="ALLOW",
        scope=scope,
        autonomy_level=0,
        world_call_class="READ_ONLY_WORLD_CALL",
    )


def test_no_ticket_blocked():
    gw = ObsidiaGateway()
    d = gw.check(None, WorldCallClass.READ_ONLY_WORLD_CALL, "bank")
    assert d.gate_result == "BLOCK"
    assert d.egress_allowed is False


def test_forbidden_world_call_blocked():
    gw = ObsidiaGateway()
    ticket = _valid_ticket()
    d = gw.check(ticket, WorldCallClass.FORBIDDEN_WORLD_CALL, "bank")
    assert d.gate_result == "BLOCK"
    assert d.egress_allowed is False


def test_invalid_scope_blocked():
    gw = ObsidiaGateway()
    ticket = _valid_ticket("bank")
    d = gw.check(ticket, WorldCallClass.READ_ONLY_WORLD_CALL, "trading")
    assert d.gate_result == "BLOCK"
    assert "INVALID_SCOPE" in d.reason


def test_valid_is_dry_run_not_egress():
    gw = ObsidiaGateway()
    ticket = _valid_ticket("bank")
    d = gw.check(ticket, WorldCallClass.READ_ONLY_WORLD_CALL, "bank")
    assert d.gate_result == "DRY_RUN_PASS"
    assert d.egress_allowed is False
    assert d.dry_run_only is True


def test_secret_in_payload_raises():
    from periphery.world_calls.secret_boundary import assert_no_secret_in_agent_payload
    with pytest.raises(AssertionError, match="SECRET_BOUNDARY_VIOLATION"):
        assert_no_secret_in_agent_payload({"api_key": "mysecret123"})
