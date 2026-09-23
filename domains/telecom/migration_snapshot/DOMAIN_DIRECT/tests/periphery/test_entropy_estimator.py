import pytest
from periphery.number_encoding.entropy_estimator import estimate_entropy


def test_uniform_bytes_high_entropy():
    data = bytes(range(256))
    r = estimate_entropy(data)
    assert r.is_high_entropy is True
    assert r.entropy_normalized > 0.99


def test_repeated_byte_low_entropy():
    data = b"aaaaaaaaaaaaaaaa"
    r = estimate_entropy(data)
    assert r.entropy_normalized < 0.1
    assert r.is_high_entropy is False


def test_empty_data():
    r = estimate_entropy(b"")
    assert r.data_len == 0
    assert r.entropy_bits == 0.0


def test_string_input():
    r = estimate_entropy("hello world")
    assert r.data_len > 0
    assert 0.0 <= r.entropy_normalized <= 1.0


def test_dict_fields():
    r = estimate_entropy(b"test")
    d = r.to_dict()
    assert "entropy_bits" in d and "entropy_normalized" in d and "is_high_entropy" in d
