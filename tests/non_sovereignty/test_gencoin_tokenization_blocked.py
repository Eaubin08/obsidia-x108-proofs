"""
V5A Non-Sovereignty Test: Gencoin tokenization is absolutely blocked.
No mint, no deploy, no real token creation for Gencoin.
"""
import pytest
from periphery.blockchain.token_policy import evaluate_token_policy


def test_gencoin_mint_blocked():
    """MINT action on Gencoin must be absolutely blocked."""
    d = evaluate_token_policy(
        token_id="gencoin_001",
        action="MINT",
        is_gencoin=True,
    )
    assert d.gate == "BLOCK"
    assert d.mint_allowed is False
    assert d.real_token_created is False
    assert d.smart_contract_created is False
    assert d.is_gencoin is True


def test_gencoin_deploy_blocked():
    """DEPLOY action on Gencoin must be absolutely blocked."""
    d = evaluate_token_policy(
        token_id="gencoin_002",
        action="DEPLOY",
        is_gencoin=True,
    )
    assert d.gate == "BLOCK"
    assert d.real_token_created is False
    assert d.smart_contract_created is False


def test_gencoin_create_blocked():
    """CREATE action on Gencoin must be absolutely blocked."""
    d = evaluate_token_policy(
        token_id="gencoin_003",
        action="CREATE",
        is_gencoin=True,
    )
    assert d.gate == "BLOCK"


def test_gencoin_all_actions_blocked():
    """All tokenization actions on Gencoin must be BLOCK."""
    actions = ["MINT", "DEPLOY", "CREATE", "TRANSFER", "BURN"]
    for action in actions:
        d = evaluate_token_policy(
            token_id="gencoin_x",
            action=action,
            is_gencoin=True,
        )
        assert d.gate == "BLOCK", f"Gencoin action {action} must be BLOCK"


def test_gencoin_reason_is_correct():
    """Block reason must state Gencoin is not a real token."""
    d = evaluate_token_policy(
        token_id="gencoin_z",
        action="MINT",
        is_gencoin=True,
    )
    assert "GENCOIN_IS_NOT_A_REAL_TOKEN" in d.reason
