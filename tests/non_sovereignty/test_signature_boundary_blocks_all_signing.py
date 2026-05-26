"""
V5A Non-Sovereignty Test: Signature boundary blocks ALL signing operations.
No signing type bypasses the boundary. No private key in payload.
"""
import pytest
from periphery.blockchain.signature_boundary import evaluate_signature_request, assert_no_private_key_in_payload

ALL_SIGN_TYPES = [
    "SIGN_MESSAGE",
    "SIGN_TRANSACTION",
    "ETH_SIGN",
    "PERSONAL_SIGN",
    "SIGN_TYPED_DATA",
    "WALLET_SIGN",
    "EIP712_SIGN",
    "eth_sign",  # lowercase variant
    "sign_anything",  # generic sign
]


@pytest.mark.parametrize("sig_type", ALL_SIGN_TYPES)
def test_all_signing_types_blocked(sig_type):
    """Every known signing type must be blocked."""
    d = evaluate_signature_request(
        request_id=f"test_{sig_type}",
        signature_type=sig_type,
    )
    assert d.blocked is True, f"Signature type {sig_type} must be blocked"
    assert d.signing_attempted is False
    assert d.key_exposed is False


def test_non_signature_type_passes():
    """Non-signature types should pass through (but no signing)."""
    d = evaluate_signature_request(
        request_id="test_safe",
        signature_type="VERIFY_MESSAGE",
    )
    # VERIFY_MESSAGE is not signing — should not be blocked
    assert d.signing_attempted is False
    assert d.key_exposed is False


def test_no_private_key_in_payload():
    """Safe payload should not trigger assertion."""
    assert_no_private_key_in_payload({"safe": "data", "amount": 100})


def test_private_key_in_payload_raises():
    """Payload with 'private_key' must raise AssertionError."""
    with pytest.raises(AssertionError):
        assert_no_private_key_in_payload({"private_key": "0x123"})


def test_seed_phrase_in_payload_raises():
    """Payload with 'seed_phrase' must raise AssertionError."""
    with pytest.raises(AssertionError):
        assert_no_private_key_in_payload({"seed_phrase": "abandon abandon abandon"})


def test_keystore_in_payload_raises():
    """Payload with 'keystore' must raise AssertionError."""
    with pytest.raises(AssertionError):
        assert_no_private_key_in_payload({"keystore": "/path/to/keystore"})
