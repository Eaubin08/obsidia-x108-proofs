import pytest
from periphery.physics_boundary.dimensional_hygiene import check_dimensional_hygiene


def test_no_units_produces_unknown():
    r = check_dimensional_hygiene("f1", units=None)
    assert r.has_units is False
    assert "UNIT_MISSING" in r.unknowns


def test_si_units_consistent():
    r = check_dimensional_hygiene("f2", units=["m", "kg", "s"])
    assert r.has_units is True
    assert r.units_consistent is True


def test_unknown_units_flag():
    r = check_dimensional_hygiene("f3", units=["obsidia_unit", "vibe_hz"])
    assert "DIMENSIONAL_MISMATCH" in " ".join(r.risk_flags)


def test_symbolic_status_accepted():
    r = check_dimensional_hygiene("f4", units=["dimensionless"], formula_status="symbolic")
    assert r.status == "symbolic"
    assert r.units_consistent is True


def test_dict_fields():
    r = check_dimensional_hygiene("f5", units=["j"])
    d = r.to_dict()
    assert "has_units" in d and "units_consistent" in d and "risk_flags" in d
