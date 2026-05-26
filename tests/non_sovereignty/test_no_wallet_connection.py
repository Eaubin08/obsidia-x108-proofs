"""
Non-sovereignty: no wallet connection in V4.
"""
import pytest
from periphery.blockchain.wallet_security_gate import evaluate_wallet_request


def test_wallet_connect_blocked():
    r = evaluate_wallet_request("ns_wc1", "wallet_connect_request")
    assert r.blocked is True
    assert r.wallet_connect_requested is True
    assert r.real_wallet_access_allowed is False


def test_walletconnect_variant_blocked():
    r = evaluate_wallet_request("ns_wc2", "walletconnect_session")
    assert r.blocked is True


def test_connect_wallet_blocked():
    r = evaluate_wallet_request("ns_wc3", "connect_wallet")
    assert r.blocked is True
    assert r.real_wallet_access_allowed is False
