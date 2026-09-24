"""OperationGraph — bounded arithmetic derivation for local math closures.

Unifies the computation step of the existing math solvers behind one
representation: each operation records inputs, operator, output and a human-
readable derivation line. The graph is bounded (MAX_OPERATIONS) and refuses
division by zero, incompatible expectations and non-integral discrete
results unless explicitly allowed.

The parser stays outside: existing extractors feed quantities in; this
module only computes and derives. It never sees task IDs.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MAX_OPERATIONS = 6

SUPPORTED_OPERATORS = frozenset({
    "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE",
    "PERCENT_OF", "PERCENT_INCREASE", "PERCENT_DECREASE",
    "RATIO", "AVERAGE", "RATE", "UNIT_CONVERSION",
})


class OperationError(ValueError):
    """Raised when an operation violates its preconditions."""


@dataclass
class Operation:
    operator: str
    inputs: tuple[float, ...]
    output: float
    unit: str | None
    derivation: str


@dataclass
class OperationGraph:
    operations: list[Operation] = field(default_factory=list)

    def _push(self, op: Operation) -> float:
        if len(self.operations) >= MAX_OPERATIONS:
            raise OperationError(f"operation bound exceeded ({MAX_OPERATIONS})")
        self.operations.append(op)
        return op.output

    # ── operators ────────────────────────────────────────────────────────────
    def add(self, a: float, b: float, unit: str | None = None) -> float:
        return self._push(Operation("ADD", (a, b), a + b, unit,
                                     f"{a} + {b} = {a + b}"))

    def subtract(self, a: float, b: float, unit: str | None = None) -> float:
        return self._push(Operation("SUBTRACT", (a, b), a - b, unit,
                                     f"{a} - {b} = {a - b}"))

    def multiply(self, a: float, b: float, unit: str | None = None) -> float:
        return self._push(Operation("MULTIPLY", (a, b), a * b, unit,
                                     f"{a} * {b} = {a * b}"))

    def divide(self, a: float, b: float, unit: str | None = None) -> float:
        if b == 0:
            raise OperationError("division by zero")
        return self._push(Operation("DIVIDE", (a, b), a / b, unit,
                                     f"{a} / {b} = {a / b}"))

    def percent_of(self, pct: float, base: float, unit: str | None = None) -> float:
        out = base * pct / 100.0
        return self._push(Operation("PERCENT_OF", (pct, base), out, unit,
                                     f"{pct}% of {base} = {out}"))

    def percent_decrease(self, base: float, pct: float, unit: str | None = None) -> float:
        out = base - base * pct / 100.0
        return self._push(Operation("PERCENT_DECREASE", (base, pct), out, unit,
                                     f"{base} - {pct}% = {out}"))

    def percent_increase(self, base: float, pct: float, unit: str | None = None) -> float:
        out = base + base * pct / 100.0
        return self._push(Operation("PERCENT_INCREASE", (base, pct), out, unit,
                                     f"{base} + {pct}% = {out}"))

    def average(self, values: tuple[float, ...], unit: str | None = None) -> float:
        if not values:
            raise OperationError("average of empty set")
        out = sum(values) / len(values)
        return self._push(Operation("AVERAGE", values, out, unit,
                                     f"avg{values} = {out}"))

    def ratio(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("ratio with zero denominator")
        return self._push(Operation("RATIO", (a, b), a / b, None,
                                     f"{a} : {b} = {a / b}"))

    def rate(self, amount: float, duration: float, unit: str | None = None) -> float:
        if duration == 0:
            raise OperationError("rate over zero duration")
        out = amount / duration
        return self._push(Operation("RATE", (amount, duration), out, unit,
                                     f"{amount} per {duration} = {out}"))

    def unit_conversion(self, value: float, factor: float,
                        unit: str | None = None) -> float:
        out = value * factor
        return self._push(Operation("UNIT_CONVERSION", (value, factor), out, unit,
                                     f"{value} x {factor} = {out} {unit or ''}".strip()))

    # ── result contracts ─────────────────────────────────────────────────────
    def require_integral(self, value: float) -> int:
        """Discrete-quantity contract: refuse a fractional final result."""
        if value != int(value):
            raise OperationError(f"non-integral discrete result: {value}")
        return int(value)

    def require_non_negative(self, value: float) -> float:
        if value < 0:
            raise OperationError(f"negative result where impossible: {value}")
        return value

    @property
    def derivation_steps(self) -> list[str]:
        return [op.derivation for op in self.operations]
