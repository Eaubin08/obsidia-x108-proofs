import pytest
from periphery.math_core.multi_agent_consensus import multi_agent_consensus


def test_one_block_overrides_all():
    votes = [
        {"agent_id": "a", "vote": "ALLOW"},
        {"agent_id": "b", "vote": "BLOCK"},
        {"agent_id": "c", "vote": "ALLOW"},
    ]
    result = multi_agent_consensus(votes)
    assert result.consensus == "BLOCK"
    assert "b" in result.block_voters


def test_hold_overrides_allow():
    votes = [
        {"agent_id": "a", "vote": "ALLOW"},
        {"agent_id": "b", "vote": "HOLD"},
    ]
    result = multi_agent_consensus(votes)
    assert result.consensus == "HOLD"


def test_all_allow_consensus():
    votes = [
        {"agent_id": "a", "vote": "ALLOW"},
        {"agent_id": "b", "vote": "ALLOW"},
    ]
    result = multi_agent_consensus(votes)
    assert result.consensus == "ALLOW"


def test_empty_votes_allow():
    result = multi_agent_consensus([])
    assert result.consensus == "ALLOW"
