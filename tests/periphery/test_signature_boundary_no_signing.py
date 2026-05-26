import pytest
from periphery.blockchain.signature_boundary import evaluate_signature_request, assert_no_private_key_in_payload


def test_sign_message_blocked():
    r = evaluate_signature_request("sr1", "SIGN_MESSAGE")
    assert r.blocked is True
    assert r.signing_attempted is False
    assert r.key_exposed is False


def test_sign_transaction_blocked():
    r = evaluate_signature_request("sr2", "SIGN_TRANSACTION")
    assert r.blocked is True


def test_eth_sign_blocked():
    r = evaluate_signature_request("sr3", "ETH_SIGN")
    assert r.blocked is True


def test_non_signing_not_blocked():
    r = evaluate_signature_request("sr4", "GET_BLOCK_NUMBER")
    assert r.blocked is False


def test_private_key_in_payload_raises():
    with pytest.raises(AssertionError, match="PRIVATE_KEY"):
        assert_no_private_key_in_payload({"private_key": "0xabc123"})


def test_clean_payload_no_raise():
    assert_no_private_key_in_payload({"action": "read_balance", "address": "0xabc"})
