import pytest
from periphery.number_encoding.compression_score import compute_compression_score


def test_repeated_data_high_compressibility():
    r = compute_compression_score(b"a" * 1000)
    assert r.compressibility == "HIGH_COMPRESSIBILITY"
    assert r.compression_ratio < 0.3


def test_random_like_data_low():
    import os
    r = compute_compression_score(os.urandom(256))
    assert r.compressibility in ("LOW_COMPRESSIBILITY", "INCOMPRESSIBLE", "MODERATE_COMPRESSIBILITY")


def test_empty_data():
    r = compute_compression_score(b"")
    assert r.compressibility == "EMPTY"


def test_string_input():
    r = compute_compression_score("hello world " * 100)
    assert r.original_size > 0
    assert r.compressed_size > 0


def test_dict_fields():
    r = compute_compression_score(b"test data")
    d = r.to_dict()
    assert "compression_ratio" in d and "compressibility" in d
