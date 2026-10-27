"""Symbolic Friction V0 — compare two values and keep both sides of a disagreement.

Recovered from the historical Friction Symbolique protocol (P2PLUS sources,
01_SOURCES/extracted_text_all.md, protocole_friction_symbolique): the divergence
between a logical and a diffuse value is |logical - diffuse|, compared strictly
with an explicit threshold (historical values: 0.3 in the protocol, 0.15 in the
pack stub).

Measures and records only: no resolution, no learning, no memory write, no ACT,
HOLD or verdict. Decision authority stays KX108_ONLY. In V0 the values come from
a controlled bench; no runtime producer is wired.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any

VERSION = "SYMBOLIC_FRICTION_V0"
CONVERGENCE_OK = "CONVERGENCE_OK"
FRICTION = "FRICTION"
NOT_COMPARABLE = "NOT_COMPARABLE"

PROVENANCE = "P2PLUS/01_SOURCES/extracted_text_all.md#protocole_friction_symbolique"
LIMITATIONS = ("SCALE_COMPARABILITY_NOT_DEMONSTRATED", "NO_RESOLUTION", "NO_LEARNING")

_BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "advisory_only": True,
    "can_decide": False,
    "emits_act": False,
    "memory_write": False,
}


def _finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def measure_symbolic_friction(trigger: str, logical: Any, diffuse: Any, *, threshold: float) -> dict[str, Any]:
    """Return a CONVERGENCE_OK / FRICTION / NOT_COMPARABLE record; never a mean, never a decision."""
    if not isinstance(trigger, str):
        raise ValueError("TRIGGER_NOT_STR")
    if not _finite_number(threshold) or threshold < 0:
        raise ValueError("THRESHOLD_INVALID")

    reasons = [f"{side}_NOT_A_FINITE_NUMBER" for side, value in (("LOGICAL", logical), ("DIFFUSE", diffuse))
               if not _finite_number(value)]
    divergence = None
    if not reasons:
        try:
            divergence = float(abs(logical - diffuse))
        except OverflowError:
            divergence = math.inf
        if not math.isfinite(divergence):
            reasons.append("DIVERGENCE_NOT_FINITE")
            divergence = None

    if reasons:
        status = NOT_COMPARABLE
    elif divergence > threshold:
        status = FRICTION
    else:
        status = CONVERGENCE_OK

    return {
        "version": VERSION,
        "status": status,
        "divergence": divergence,
        "threshold": float(threshold),
        "paradox": {"logical": logical, "diffuse": diffuse},
        "trigger_digest": hashlib.sha256(trigger.encode("utf-8")).hexdigest(),
        "provenance": PROVENANCE,
        "limitations": list(LIMITATIONS),
        "not_comparable_reasons": reasons,
        **_BOUNDARY,
    }
