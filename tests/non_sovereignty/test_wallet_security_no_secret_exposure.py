"""
V5A Non-Sovereignty Test: Wallet security gate never exposes secrets.
"""
import pytest
from periphery.blockchain.wallet_security_gate import evaluate_wallet_request


def test_private_key_request_blocked():
    """Request containing 'private_key' must be blocked."""
    d = evaluate_wallet_request(
        request_id="test1",
        request_type="get_private_key",
    )
    assert d.blocked is True
    assert d.private_key_requested is True
    assert d.real_wallet_access_allowed is False


def test_seed_phrase_request_blocked():
    """Request containing 'seed_phrase' must be blocked."""
    d = evaluate_wallet_request(
        request_id="test2",
        request_type="get_seed_phrase",
    )
    assert d.blocked is True
    assert d.seed_phrase_requested is True


def test_wallet_connect_request_blocked():
    """Request containing 'wallet_connect' must be blocked."""
    d = evaluate_wallet_request(
        request_id="test3",
        request_type="wallet_connect_mainnet",
    )
    assert d.blocked is True
    assert d.wallet_connect_requested is True


def test_safe_request_passes_through():
    """Safe requests (no key/seed/connect) pass through with real_wallet_access=False."""
    d = evaluate_wallet_request(
        request_id="test4",
        request_type="balance_check",
        payload={"safe": "data"},
    )
    assert d.blocked is False
    assert d.real_wallet_access_allowed is False
    assert d.private_key_requested is False


def test_secret_key_in_payload_blocked():
    """'secret_key' in payload must be blocked."""
    d = evaluate_wallet_request(
        request_id="test5",
        request_type="read_data",
        payload={"secret_key": "0xdeadbeef"},
    )
    assert d.blocked is True
