import pytest
from periphery.blockchain.token_policy import evaluate_token_policy


def test_gencoin_always_blocked():
    r = evaluate_token_policy("gencoin", "MINT", is_gencoin=True)
    assert r.gate == "BLOCK"
    assert r.mint_allowed is False
    assert r.real_token_created is False
    assert "GENCOIN_IS_NOT_A_REAL_TOKEN" in r.reason


def test_token_mint_blocked():
    r = evaluate_token_policy("tok1", "MINT", is_gencoin=False)
    assert r.gate == "BLOCK"
    assert r.mint_allowed is False


def test_token_deploy_blocked():
    r = evaluate_token_policy("tok2", "DEPLOY")
    assert r.gate == "BLOCK"


def test_other_token_action_hold():
    r = evaluate_token_policy("tok3", "TRANSFER")
    assert r.gate == "HOLD"
    assert r.mint_allowed is False


def test_dict_fields():
    r = evaluate_token_policy("tok4", "READ")
    d = r.to_dict()
    assert "mint_allowed" in d and "real_token_created" in d
    assert d["mint_allowed"] is False
