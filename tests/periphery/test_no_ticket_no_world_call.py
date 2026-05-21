import pytest
from periphery.world_calls.sovereign_ticket import require_ticket_or_block, issue_sovereign_ticket


def test_no_ticket_blocks():
    with pytest.raises(AssertionError, match="NO_SOVEREIGN_TICKET_NO_WORLD_CALL"):
        require_ticket_or_block(None)


def test_valid_ticket_passes():
    ticket = issue_sovereign_ticket(
        action_id="test",
        os3_ticket_id="os3_x",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=0,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    require_ticket_or_block(ticket)


def test_ticket_dry_run_only():
    ticket = issue_sovereign_ticket(
        action_id="test",
        os3_ticket_id="os3_x",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=0,
        world_call_class="READ_ONLY_WORLD_CALL",
    )
    assert ticket.dry_run_only is True


def test_expired_ticket_blocks():
    from datetime import datetime, timezone, timedelta
    ticket = issue_sovereign_ticket(
        action_id="test",
        os3_ticket_id="os3_x",
        x108_gate="ALLOW",
        scope="bank",
        autonomy_level=0,
        world_call_class="READ_ONLY_WORLD_CALL",
        ttl_seconds=-1,
    )
    with pytest.raises(AssertionError, match="SOVEREIGN_TICKET_EXPIRED"):
        require_ticket_or_block(ticket)
