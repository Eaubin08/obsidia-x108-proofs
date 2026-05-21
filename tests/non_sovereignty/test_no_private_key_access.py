"""
Non-sovereignty: no agent or module may access, store, or request a private key.
"""
import pytest
from periphery.blockchain.wallet_security_gate import evaluate_wallet_request
from periphery.blockchain.signature_boundary import assert_no_private_key_in_payload


def test_private_key_request_always_blocked():
    r = evaluate_wallet_request("ns_pk1", "private_key_export")
    assert r.blocked is True
    assert r.real_wallet_access_allowed is False


def test_secretkey_variant_blocked():
    r = evaluate_wallet_request("ns_pk2", "secret_key_read")
    assert r.blocked is True


def test_private_key_in_payload_raises():
    with pytest.raises(AssertionError):
        assert_no_private_key_in_payload({"private_key": "0xDEAD"})


def test_mnemonic_blocked():
    r = evaluate_wallet_request("ns_pk3", "mnemonic_backup")
    assert r.blocked is True
    assert r.seed_phrase_requested is True
