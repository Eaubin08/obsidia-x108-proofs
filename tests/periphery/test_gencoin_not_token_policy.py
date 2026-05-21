import pytest
from periphery.blockchain.token_policy import evaluate_token_policy


def test_gencoin_mint_blocked():
    r = evaluate_token_policy("gencoin", "MINT", is_gencoin=True)
    assert r.gate == "BLOCK"
    assert r.mint_allowed is False


def test_gencoin_deploy_blocked():
    r = evaluate_token_policy("gencoin", "DEPLOY", is_gencoin=True)
    assert r.gate == "BLOCK"
    assert r.smart_contract_created is False


def test_gencoin_transfer_blocked():
    r = evaluate_token_policy("gencoin", "TRANSFER", is_gencoin=True)
    assert r.gate == "BLOCK"
    assert "GENCOIN_IS_NOT_A_REAL_TOKEN" in r.reason


def test_gencoin_always_blocked_regardless_of_action():
    for action in ("MINT", "BURN", "TRANSFER", "APPROVE", "STAKE"):
        r = evaluate_token_policy("gencoin", action, is_gencoin=True)
        assert r.gate == "BLOCK", f"Gencoin action {action} should be BLOCK"


def test_gencoin_no_real_token_created():
    r = evaluate_token_policy("gencoin", "CREATE", is_gencoin=True)
    assert r.real_token_created is False
    assert r.smart_contract_created is False
