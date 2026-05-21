import pytest
from periphery.physics_boundary.unit_consistency_checker import check_unit_consistency


def test_si_units_compatible():
    r = check_unit_consistency("uc1", ["m", "kg", "s", "j"])
    assert r.all_si_compatible is True
    assert r.non_si_units == []


def test_custom_units_flagged():
    r = check_unit_consistency("uc2", ["vibe_unit", "soul_hz"])
    assert r.all_si_compatible is False
    assert "vibe_unit" in r.non_si_units
    assert len(r.risk_flags) > 0


def test_mixed_units():
    r = check_unit_consistency("uc3", ["m", "soul_unit"])
    assert r.all_si_compatible is False
    assert "DIMENSIONAL_MISMATCH" in r.risk_flags[0]


def test_dict_fields():
    r = check_unit_consistency("uc4", ["w"])
    d = r.to_dict()
    assert "all_si_compatible" in d and "non_si_units" in d and "risk_flags" in d
