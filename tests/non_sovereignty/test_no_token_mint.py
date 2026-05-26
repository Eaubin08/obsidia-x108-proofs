"""
Non-sovereignty: no token minting. Gencoin is NOT a real token.
"""
import pytest
from periphery.blockchain.token_policy import evaluate_token_policy
from periphery.blockchain.blockchain_action_classifier import classify_blockchain_action, BlockchainActionClass


def test_token_mint_blocked():
    r = evaluate_token_policy("ns_tok1", "MINT")
    assert r.gate == "BLOCK"
    assert r.mint_allowed is False


def test_token_mint_class_blocked():
    r = classify_blockchain_action("ns_tok2", BlockchainActionClass.TOKEN_MINT)
    assert r.gate == "BLOCK"
    assert r.real_chain_action_allowed is False


def test_gencoin_not_a_token():
    r = evaluate_token_policy("gencoin", "MINT", is_gencoin=True)
    assert r.gate == "BLOCK"
    assert r.mint_allowed is False
    assert r.real_token_created is False


def test_token_burn_requires_review():
    r = classify_blockchain_action("ns_tok3", BlockchainActionClass.TOKEN_BURN)
    assert r.gate in ("BLOCK", "HOLD")
    assert r.real_chain_action_allowed is False
