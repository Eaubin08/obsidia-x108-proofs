import pytest
from periphery.blockchain.wallet_security_gate import evaluate_wallet_request


def test_private_key_request_blocked():
    r = evaluate_wallet_request("wr1", "private_key_export")
    assert r.blocked is True
    assert r.private_key_requested is True
    assert r.real_wallet_access_allowed is False


def test_seed_phrase_request_blocked():
    r = evaluate_wallet_request("wr2", "seed_phrase_backup")
    assert r.blocked is True
    assert r.seed_phrase_requested is True


def test_wallet_connect_blocked():
    r = evaluate_wallet_request("wr3", "wallet_connect_request")
    assert r.blocked is True
    assert r.wallet_connect_requested is True


def test_safe_request_not_blocked():
    r = evaluate_wallet_request("wr4", "check_balance_advisory")
    assert r.blocked is False
    assert r.real_wallet_access_allowed is False


def test_dict_fields():
    r = evaluate_wallet_request("wr5", "read_address")
    d = r.to_dict()
    assert "blocked" in d and "real_wallet_access_allowed" in d
    assert d["real_wallet_access_allowed"] is False
