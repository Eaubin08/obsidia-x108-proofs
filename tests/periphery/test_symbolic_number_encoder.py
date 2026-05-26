import pytest
from periphery.number_encoding.symbolic_number_encoder import encode_symbolic_number


def test_108_is_x108_kernel():
    r = encode_symbolic_number(108)
    assert r.symbolic_name == "X108_KERNEL"
    assert "SYMBOLIC:X108_KERNEL" in r.tags


def test_34_is_cognitive_trees():
    r = encode_symbolic_number(34)
    assert r.symbolic_name == "COGNITIVE_TREES"
    assert r.is_fibonacci is True


def test_13_is_fibonacci_and_prime():
    r = encode_symbolic_number(13)
    assert r.is_fibonacci is True
    assert r.is_prime is True


def test_0_is_void():
    r = encode_symbolic_number(0)
    assert r.symbolic_name == "VOID"


def test_dict_fields():
    r = encode_symbolic_number(7)
    d = r.to_dict()
    assert "symbolic_name" in d and "is_fibonacci" in d and "tags" in d
