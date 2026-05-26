"""
Dimensional Hygiene — checks equations for unit consistency.
Formula without unit -> unknowns += UNIT_MISSING.
Inconsistent units -> risk_flags += DIMENSIONAL_MISMATCH.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_KNOWN_UNITS = {
    "m", "kg", "s", "a", "k", "mol", "cd",
    "j", "w", "n", "pa", "hz", "v", "ohm", "c", "f",
    "m/s", "m/s^2", "kg*m/s^2", "j/s",
    "dimensionless", "ratio", "percent", "normalized",
}


@dataclass
class DimensionalHygieneResult:
    formula_id: str
    has_units: bool
    units_consistent: bool
    status: str
    unknowns: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "formula_id": self.formula_id,
            "has_units": self.has_units,
            "units_consistent": self.units_consistent,
            "status": self.status,
            "unknowns": self.unknowns,
            "risk_flags": self.risk_flags,
        }


def check_dimensional_hygiene(
    formula_id: str,
    units: list[str] | None,
    formula_status: str = "symbolic",
) -> DimensionalHygieneResult:
    valid_statuses = {"symbolic", "heuristic", "measured", "proven"}
    unknowns = []
    risk_flags = []

    if not units:
        unknowns.append("UNIT_MISSING")
        return DimensionalHygieneResult(
            formula_id=formula_id,
            has_units=False,
            units_consistent=False,
            status=formula_status,
            unknowns=unknowns,
            risk_flags=risk_flags,
        )

    units_lower = [u.lower() for u in units]
    unknown_units = [u for u in units_lower if u not in _KNOWN_UNITS]
    if unknown_units:
        risk_flags.append(f"DIMENSIONAL_MISMATCH:{','.join(unknown_units)}")

    if formula_status not in valid_statuses:
        risk_flags.append(f"UNKNOWN_FORMULA_STATUS:{formula_status}")

    return DimensionalHygieneResult(
        formula_id=formula_id,
        has_units=True,
        units_consistent=len(risk_flags) == 0,
        status=formula_status,
        unknowns=unknowns,
        risk_flags=risk_flags,
    )
