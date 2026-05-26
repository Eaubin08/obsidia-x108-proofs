import pytest
from periphery.blockchain.blockchain_action_classifier import (
    classify_blockchain_action, BlockchainActionClass
)


def test_chain_read_only_allowed():
    r = classify_blockchain_action("ba1", BlockchainActionClass.CHAIN_READ_ONLY)
    assert r.gate == "ALLOW"
    assert r.real_chain_action_allowed is False


def test_sign_transaction_blocked():
    r = classify_blockchain_action("ba2", BlockchainActionClass.SIGN_TRANSACTION_REQUEST)
    assert r.gate == "BLOCK"
    assert r.dry_run_only is True


def test_token_mint_blocked():
    r = classify_blockchain_action("ba3", BlockchainActionClass.TOKEN_MINT)
    assert r.gate == "BLOCK"


def test_defi_swap_hold():
    r = classify_blockchain_action("ba4", BlockchainActionClass.DEFI_SWAP)
    assert r.gate == "HOLD"
    assert r.real_chain_action_allowed is False


def test_smart_contract_deploy_blocked():
    r = classify_blockchain_action("ba5", BlockchainActionClass.SMART_CONTRACT_DEPLOY)
    assert r.gate == "BLOCK"


def test_dict_fields():
    r = classify_blockchain_action("ba6", BlockchainActionClass.BRIDGE_TRANSFER)
    d = r.to_dict()
    assert "gate" in d and "action_class" in d and "dry_run_only" in d
    assert d["real_chain_action_allowed"] is False
