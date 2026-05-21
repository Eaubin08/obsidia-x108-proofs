import pytest
from periphery.number_encoding.crypto_boundary import evaluate_crypto_boundary


def test_no_claim_produces_hash():
    r = evaluate_crypto_boundary("cb1", "represent the number 42 symbolically")
    assert r.crypto_claim_detected is False
    assert r.claim_blocked is False
    assert len(r.sha256_hash) == 64
    assert r.sandbox_only is True


def test_break_claim_blocked():
    r = evaluate_crypto_boundary("cb2", "break sha256 with this method")
    assert r.crypto_claim_detected is True
    assert r.claim_blocked is True


def test_replace_sha_blocked():
    r = evaluate_crypto_boundary("cb3", "replace_sha with custom algorithm")
    assert r.claim_blocked is True


def test_sandbox_always_true():
    r = evaluate_crypto_boundary("cb4", "entropy analysis of binary data")
    assert r.sandbox_only is True


def test_dict_fields():
    r = evaluate_crypto_boundary("cb5", "symbolic number")
    d = r.to_dict()
    assert "sandbox_only" in d and "crypto_claim_detected" in d and "sha256_hash" in d
