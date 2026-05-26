import pytest
from periphery.number_encoding.radix_systems import represent_in_radices


def test_zero_representation():
    r = represent_in_radices(0)
    assert r.decimal == "0"
    assert r.binary == "0b0"


def test_value_108_has_hex():
    r = represent_in_radices(108)
    assert r.hexadecimal == "0x6c"
    assert r.decimal == "108"


def test_ternary_of_9():
    r = represent_in_radices(9)
    assert r.ternary == "100"


def test_base36_of_36():
    r = represent_in_radices(36)
    assert r.base36 == "10"


def test_dict_fields():
    r = represent_in_radices(42)
    d = r.to_dict()
    assert "binary" in d and "ternary" in d and "hexadecimal" in d and "base36" in d
