"""
Unit Consistency Checker — verifies that formula inputs have consistent SI units.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_SI_BASE = {"m", "kg", "s", "a", "k", "mol", "cd"}
_SI_DERIVED = {"j", "n", "w", "pa", "hz", "v", "ohm", "c", "f", "wb", "t", "lm", "lx"}
_ALL_SI = _SI_BASE | _SI_DERIVED | {"dimensionless", "ratio", "normalized", "percent"}


@dataclass
class UnitConsistencyResult:
    check_id: str
    units_provided: list[str]
    all_si_compatible: bool
    non_si_units: list[str]
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "units_provided": self.units_provided,
            "all_si_compatible": self.all_si_compatible,
            "non_si_units": self.non_si_units,
            "risk_flags": self.risk_flags,
        }


def check_unit_consistency(check_id: str, units: list[str]) -> UnitConsistencyResult:
    risk_flags = []
    non_si = [u for u in units if u.lower() not in _ALL_SI]
    if non_si:
        risk_flags.append(f"DIMENSIONAL_MISMATCH:{','.join(non_si)}")
    return UnitConsistencyResult(
        check_id=check_id,
        units_provided=units,
        all_si_compatible=len(non_si) == 0,
        non_si_units=non_si,
        risk_flags=risk_flags,
    )
